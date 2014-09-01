#   Copyright 2014 Code for Hampton Roads contributors
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import config
from datetime import datetime
import re
import scrapertools
from slugify import slugify

c = config.load()

BASE_URL = 'http://www.healthspace.com/'
LOCALITY_LIST_URL = 'Clients/VDH/vdh_website.nsf/Main-HealthRegions?OpenView&Count=10000'
LOCALITY_MAIN_URL = '/Main-News-Recent'
CITY_LIST_URL = '/Food-CityList'

def get_cities():
    localities = []
    cities = []
    
    locality_list = scrapertools.get_content(BASE_URL + LOCALITY_LIST_URL)
    locality_a_tags = locality_list.body.div.img.find_all_next('a')
    locality_urls = list(set(locality['href'][1:] for locality in locality_a_tags))
    
    for locality_url in locality_urls:
        locality_main = scrapertools.get_content(BASE_URL + locality_url + LOCALITY_MAIN_URL)
        locality_name = locality_main.find('h3').string
        localities.append({
            'name': locality_name,
            'url': locality_url
        })
        print 'Locality: ' + locality_name

    for locality in localities:
        city_list = scrapertools.get_content(BASE_URL + locality['url'] + CITY_LIST_URL)
        city_a_tags = city_list.find_all('a')
        
        for city in city_a_tags:
            name = str(city.string).strip()
            print 'Loading {0} ({1})'.format(name, locality['name'])
            cities.append({
                'name': name,
                'locality': locality['name'],
                'baseUrl': city['href'][:city['href'].find('Food-List-ByName')],
                'establishmentUrl': city['href'].replace('Count=30', '')
            })
    
    return cities

def get_establishments(city):
    establishments_found = []

    start = 1
    count = 1000
    more = True

    while more:
        establishment_list = scrapertools.get_content(BASE_URL + city['establishmentUrl']+'&start='+str(start)+'&count='+str(count))
        if establishment_list.find(text='No documents found') is not None:
            more = False
            continue
        start += count
        establishments = establishment_list.find_all('tr')
        for establishment in establishments:
            details = establishment.find_all('td')
            if len(details) == 4 and details[0] is not None and details[0].a is not None:
                date = (None if scrapertools.get_text(details[3]) is None
                        else datetime.strptime(scrapertools.get_text(details[3]), '%d-%b-%Y'))
                # Removes establishment IDs and newlines from the establishment name
                name = re.sub('(#|\()(\s)*([0-9][0-9]-[0-9][0-9][0-9][0-9])(\))?', '', scrapertools.get_text(details[0]))
                name = re.sub('(\n)+', ' ', name)
                address = scrapertools.get_text(details[2])
                slug_id = slugify(name.strip() + ' ' + address)
                establishments_found.append({
                    'slug': slug_id,
                    'name': name.strip(),
                    'url': details[0].a['href'],
                    'address': address,
                    'locality': city['locality'],
                    'last_inspection_date': date,
                    'baseUrl': city['baseUrl'],
                    'inserted': datetime.now()
                })
    return establishments_found


def get_establishment_details(establishment):

    establishment_details = scrapertools.get_content(BASE_URL + establishment['url'])
    establishment['city'] = re.sub('(<(/)?br>)|(\r)|(\n)',
                                   '',
                                   str(establishment_details.find(text=re.compile('Facility Location')).parent.next_sibling.find('br')))
    establishment['type'] = establishment_details.find(text=re.compile("Facility Type")).parent.next_sibling.string

    return establishment


def get_inspections(establishment, city_url):
    inspections_found = []
    
    establishment_details = scrapertools.get_content(BASE_URL + establishment['url'])
    inspections = establishment_details.find_all(text='Inspection Type')[0].find_parent('tr').find_all_next('tr')

    for inspection in inspections:
        details = inspection.find_all('td')

        if details[0].a is None:
            continue
        
        violations = get_violations(BASE_URL + city_url + '/' + details[0].a['href'])
        inspections_found.append({
            'type': scrapertools.get_text(details[0]),
            'date': datetime.strptime(scrapertools.get_text(details[1]), '%d-%b-%Y'),
            'violations': violations
        })
    
    return inspections_found

def get_establishment_geo(establishment):
    geo = scrapertools.get_lat_lng(establishment['address'], establishment['city'], c['state'])
    if geo is not None:
        establishment['geo'] = {'type': 'Point', 'coordinates': [geo['lng'], geo['lat']]}

    return establishment


def get_violations(inspection_details_url):
    violations_found = []
    
    inspection_details = scrapertools.get_content(inspection_details_url)

    violations = inspection_details.find(text='Violations:').find_next('table')

    if violations is None:
        return []
    violations = violations.find('tr').find_next_siblings()
    for violation in violations:
        details = violation.find_all('td')

        violations_found.append({
            'code': scrapertools.get_all_text(details[0])[0],
            'repeat': any(['Repeat' in tag.string for tag in details[1].contents if tag.name == 'b']),
            'critical': any(['Critical' in tag.string for tag in details[1].contents if tag.name == 'b']),
            'corrected': any(['Corrected' in tag.string for tag in details[1].contents if tag.name == 'b']),
            'correction': ' '.join([tag.string for tag in details[1].contents if tag.name == 'font']).strip(),
            'observation': ' '.join([tag.string for tag in details[1].contents if tag.name == None]).strip()
        })
    return violations_found

