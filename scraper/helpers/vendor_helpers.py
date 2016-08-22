import scrapy
import re
import json
from urllib import parse, request
from slugify import slugify
from scrapy.utils.project import get_project_settings

settings = get_project_settings()

def get_urls(self,response):
    '''
    Returns absolute URLS from Javascript
    '''

    scripts = response.xpath('//script/text()').extract()

    urls = list(filter(None, map(get_function_urls, scripts)))

    if len(urls) == 1:
        return urls[0]
    else:
        return None


def get_function_urls(script):
    '''
    Extracts URLS from functions and returns as a list
    '''

    url_list = re.findall('(?<=function\s)(.*)(?:\(thisEvent\)\s{\n)(?:location\s\=\s\")(.*)(?:\")', script)

    return [url[1] for url in url_list]


def vendor_address(location):
    return location.split(',')[0]

def vendor_city(location):
    return location.split(',')[1].split('VA')[0].rstrip()

def vendor_search_name(name):
    return slugify(name, separator = ' ')

def vendor_guid(url):
	if url:
		matches = re.match('(http://healthspace.com/Clients/VDH/)(.*)(/web.nsf/formFacility.xsp\?id=)(.*)',url, flags=re.I)
		if matches:
			return matches.group(4)

	return None

def get_lat_lng(address):

    ss_id = settings['SS_ID']
    ss_token = settings['SS_TOKEN']

    if ss_id is not None and ss_token is not None:
        # If address is a PO Box, skip
        if re.search('P(\.)?O(\.)?(\sBox\s)[0-9]+', address['street']) is None and address['street'] != '':
            url = 'https://api.smartystreets.com/street-address?'
            url += 'state=' + parse.quote(str(address['state']))
            url += '&city=' + parse.quote(str(address['city']))
            url += '&auth-id=' + str(ss_id)
            url += '&auth-token=' + str(ss_token)
            url += '&street=' + parse.quote(str(address['street']))

            response = request.urlopen(url)
            data = json.loads(response.read().decode('utf-8'))

            if len(data) == 1:
                lat_lng = {'lat': data[0]['metadata']['latitude'], 'lng': data[0]['metadata']['longitude']}
                return lat_lng

    return None



def vendor_category(type):
	categories = {'Seasonal Fast Food Restaurant': 'Restaurant',
              'Fast Food Restaurant': 'Restaurant',
              'Full Service Restaurant': 'Restaurant',
              'Public Middle or High School Food Service': 'Education',
              'Mobile Food Unit': 'Mobile Food',
              'Private Elementary School Food Service': 'Education',
              'Child Care Food Service': 'Education',
              'Other Food Service': 'Other',
              'Mobile food unit': 'Mobile Food',
              'Public Elementary School Food Service': 'Education',
              'Dept. of Juvenile Justice Food Service': 'Government',
              'Carry Out Food Service Only': 'Grocery',
              'Commissary': 'Grocery',
              'Hotel Continental Breakfast': 'Hospitality',
              'Full Service Restaurant/Caterer': 'Restaurant',
              'Hospital Food Service': 'Medical',
              'Caterer': 'Restaurant',
              'State College Food Service': 'Education',
              'Convenience Store Food Service': 'Grocery',
              'Private Middle or High School Food Service': 'Education',
              'Bed & Breakfast Food Service': 'Hospitality',
              'Adult Care Home Food Service': 'Medical',
              'Fast Food Restaurant/Caterer': 'Restaurant',
              'Adult Day Care Food Service': 'Medical',
              'Nursing Home Food Service': 'Medical',
              'Summer Food Service Program Feeding Site': 'Education',
              'Jail Food Service': 'Government',
              'Private College Food Service': 'Education',
              'Group Home Food Service': 'Medical',
              'Seasonal Full Service Restaurant': 'Restaurant',
              'Summer Camp Food Service': 'Education',
              'Grocery Store Food Service': 'Grocery',
              'Public Elementry School Food Service': 'Education',
              'Public Primary School Food Service': 'Education',
              'Private High School Food Service': 'Education',
              'State Institution Food Service': 'Government',
              'Summer camp kitchen': 'Education',
              'Institution': 'Government',
              'Residential Child Care Institution Food Service': 'Education',
              'Summer Food Service Program Kitchen': 'Education',
              'Hotel continental breakfast': 'Hospitality',
              'Public school kitchen': 'Education',
              'Snack Bar': 'Grocery',
              'Bed & Breakfast': 'Hospitality',
              'Restaurant': 'Restaurant',
              'Private Elementry School Food Service': 'Education',
              'Adult care home food service': 'Medical'}
	return categories[type]
