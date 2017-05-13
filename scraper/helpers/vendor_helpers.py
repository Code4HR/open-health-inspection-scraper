import scrapy
import re
import json
import logging
from pymongo import MongoClient
from urllib import parse, request
from slugify import slugify
from datetime import datetime
from scrapy.utils.project import get_project_settings

logger = logging.getLogger('Vendor Helpers')

def connect_db():
    settings = get_project_settings()

    connection = MongoClient(host=settings['MONGODB_SERVER'],
                             port=int(settings['MONGODB_PORT']))

    db = connection[settings['MONGODB_DB']]
    if settings['MONGODB_USER'] and settings['MONGODB_PWD']:
        db.authenticate(settings['MONGODB_USER'], settings['MONGODB_PWD'])

    return db[settings['MONGODB_COLLECTION']]


def get_urls(self,response):
    # Returns absolute URLS from Javascript

    scripts = response.xpath('//script/text()').extract()

    urls = list(filter(None, map(get_function_urls, scripts)))

    if len(urls) == 1:
        return urls[0]
    else:
        return None


def get_function_urls(script):
    # Extracts URLS from functions and returns as a list

    url_list = re.findall('(?<=function\s)(.*)(?:\(thisEvent\)\s{\n)(?:location\s\=\s\")(.*)(?:\")', script)

    return [url[1] for url in url_list]


def vendor_address(location):
    parts = location.split(',')
    return ','.join(parts[0:(len(parts)-2)]).strip()

def vendor_city(location):
    parts = location.split(',')
    return parts[len(parts)-2].split('VA')[0].strip()

def vendor_search_name(name):
    return slugify(name, separator = ' ')

def vendor_guid(url):
    if url:
        matches = re.match('(http://healthspace.com/Clients/VDH/)(.*)(/web.nsf/formFacility.xsp\?id=)(.*)',url, flags=re.I)
        if matches:
            return matches.group(4)

    return None

def get_lat_lng(address):

    existing_lat_lng = address_compare(address)

    if existing_lat_lng is None:
        if address['street'] is not None and address['city'] is not None:
            # Take a dict of address parts and call SmartyStreets to geocode it.
            settings = get_project_settings()

            ss_id = settings['SS_ID']
            ss_token = settings['SS_TOKEN']

            if ss_id is not None and ss_token is not None:
                # If address is a PO Box, skip
                if re.search('P(\.)?O(\.)?(\sBox\s)[0-9]+', address['street']) is None and address['street'] != '':
                    logger.debug(address)
                    url = 'https://api.smartystreets.com/street-address?'
                    url += 'state=' + parse.quote(address['state'])
                    url += '&city=' + parse.quote(address['city'])
                    url += '&auth-id=' + str(ss_id)
                    url += '&auth-token=' + str(ss_token)
                    url += '&street=' + parse.quote(address['street'])

                    response = request.urlopen(url)
                    data = json.loads(response.read().decode('utf-8'))

                    if len(data) == 1:
                        logger.debug('Geocoded ' + str(address))
                        lat_lng = {'type': 'Point',
                                   'coordinates': [data[0]['metadata']['longitude'], data[0]['metadata']['latitude']]}
                        return lat_lng
                    else:
                        logger.debug('Could not geocode address ' + str(address))
                        logger.debug(response.status)
                        logger.debug(response.info())
                        logger.debug(data)
        return None

    logger.debug('Address is current and has already been geocoded')
    return existing_lat_lng


def needs_geocoding(address):
    existing_lat_lng = address_compare(address)

    if existing_lat_lng is None:
        if address['street'] is not None and address['city'] is not None:
            if re.search('P(\.)?O(\.)?(\sBox\s)[0-9]+', address['street']) is None and address['street'] != '':
                return True
    return None


def needs_geocoding_date(address):
    existing_lat_lng = address_compare(address)

    if existing_lat_lng is None:
        if address['street'] is not None and address['city'] is not None:
            if re.search('P(\.)?O(\.)?(\sBox\s)[0-9]+', address['street']) is None and address['street'] != '':
                return datetime.utcnow()
    return None


def address_compare(address):
    collection = connect_db()

    existing = collection.find_one({
        'guid': address['guid'],
        'address': address['street'],
        'city': address['city'],
        'geo': { '$exists': True }
    }, {'geo': 1})

    if existing is not None:
        return existing['geo']

    return None

def vendor_category(type):
    # Lookup the vendor type in a dict and return a broader category
    categories = {'Adult care home food service': 'Medical',
                  'Adult Care Home Food Service': 'Medical',
                  'Adult Day Care Food Service': 'Medical',
                  'Bed & Breakfast': 'Hospitality',
                  'Bed & Breakfast Food Service': 'Hospitality',
                  'Carry Out Food Service Only': 'Grocery',
                  'Caterer': 'Restaurant',
                  'Child Care Food Service': 'Education',
                  'Commissary': 'Grocery',
                  'Convenience Store Food Service': 'Grocery',
                  'Dept. of Juvenile Justice Food Service': 'Government',
                  'Fast Food Restaurant': 'Restaurant',
                  'Fast Food Restaurant/Caterer': 'Restaurant',
                  'Full Service Restaurant': 'Restaurant',
                  'Full Service Restaurant/Caterer': 'Restaurant',
                  'Grocery Store Food Service': 'Grocery',
                  'Group Home Food Service': 'Medical',
                  'Hospital Food Service': 'Medical',
                  'Hotel Continental Breakfast': 'Hospitality',
                  'Hotel continental breakfast': 'Hospitality',
                  'Institution': 'Government',
                  'Jail Food Service': 'Government',
                  'Local Convenience Store Food Service': 'Grocery',
                  'Local Grocery Store Food Service': 'Grocery',
                  'Mobile Food Unit': 'Mobile Food',
                  'Mobile food unit': 'Mobile Food',
                  'Nursing Home Food Service': 'Medical',
                  'Other Food Service': 'Other',
                  'Private College Food Service': 'Education',
                  'Private Elementary School Food Service': 'Education',
                  'Private Elementry School Food Service': 'Education',
                  'Private High School Food Service': 'Education',
                  'Private Middle or High School Food Service': 'Education',
                  'Public Elementary School Food Service': 'Education',
                  'Public Elementry School Food Service': 'Education',
                  'Public Middle or High School Food Service': 'Education',
                  'Public Primary School Food Service': 'Education',
                  'Public school kitchen': 'Education',
                  'Residential Child Care Institution Food Service': 'Education',
                  'Restaurant': 'Restaurant',
                  'Seasonal Fast Food Restaurant': 'Restaurant',
                  'Seasonal Full Service Restaurant': 'Restaurant',
                  'Snack Bar': 'Grocery',
                  'State College Food Service': 'Education',
                  'State Institution Food Service': 'Government',
                  'Summer Camp Food Service': 'Education',
                  'Summer camp kitchen': 'Education',
                  'Summer Food Service Program Feeding Site': 'Education',
                  'Summer Food Service Program Kitchen': 'Education'}

    if type in categories:
        return categories[type]
    else:
        return 'Other'
