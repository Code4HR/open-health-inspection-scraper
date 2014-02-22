from bs4 import BeautifulSoup
import pymongo
from pymongo import MongoClient
import scraperwiki

def clean(data):
    if data is not None:
        return data.replace(u'\xa0', '')
    return data

print 'Connect to DB'

client = MongoClient('mongodb://cfa:cfa123@ds033639.mongolab.com:33639/healthdata')
db = client.healthdata

print 'Start scraping!'

print 'Find Cities'

BASE_URL = 'http://www.healthspace.com/'

html = scraperwiki.scrape(BASE_URL + 'Clients/VDH/vdh_website.nsf/Main-HealthRegions?OpenView&Count=10000')
localities = BeautifulSoup(html)

cities = []
cityNames = []

for locality in localities.body.div.p.find_next_siblings('a'):
    html = scraperwiki.scrape(BASE_URL + locality['href'] + '/Food-CityList')
    cityHtml = BeautifulSoup(html)
    for city in cityHtml.find_all('a'):
        if city.string not in cityNames:
            print 'Adding ' + city.string
            cityNames.append(city.string)
            cities.append({ 'name': city.string, 'url': city['href'].replace('Count=30', 'Count=10000') })

for city in cities:
    print 'Do ' + city['name']
    
    print 'City Places URL: ' +  BASE_URL + city['url']
    
    baseLocalityUrl = city['url'][:city['url'].find('Food-List-ByName')]
    print 'Base locality url ' + baseLocalityUrl
    
    html = scraperwiki.scrape(BASE_URL + city['url'])
    places = BeautifulSoup(html)
    
    cityCollection = db[city['name']]

    for place in places.find_all('tr'):

        tds = place.find_all('td')

        if len(tds) == 4 and tds[0] is not None and tds[0].a is not None:
    
            placeData = {
                'name' : clean(tds[0].find(text=True)),
                'address' : clean(tds[2].find(text=True)),
                'last_inspection_date' : clean(tds[3].find(text=True))
            }
        
            if cityCollection.find_one(placeData) is not None:
                print 'Already have ' + placeData['name']
                continue
        
            html = scraperwiki.scrape(BASE_URL + tds[0].a['href'])
            placeDetails = BeautifulSoup(html)
            inspections = placeDetails.find_all(text='Inspection Type')[0].find_parent('table').find_all('tr')

            placeData['inspections'] = []

            for inspection in inspections:
                inspection_tds = inspection.find_all('td')
        
                if(inspection_tds[0].a is None):
                    continue
                
                violationsUrl = BASE_URL + baseLocalityUrl + '/' + inspection_tds[0].a['href']
                #print 'Violations URL: ' + violationsUrl
                html = scraperwiki.scrape(violationsUrl)
                inspectionDetails = BeautifulSoup(html)
        
                violations = []
                violationsTable = inspectionDetails.find(text='Violations:').find_next('table')
                if violationsTable is not None:
                    inspectionItems = violationsTable.find_all('tr')
                    for item in inspectionItems:
                        item_td = item.find_all('td')
                
                        violations.append({
                            'code': clean(item_td[0].find(text=True)),
                            'observations': item_td[1].find_all(text=True)
                        })
        
                placeData['inspections'].append({
                    'type': clean(inspection_tds[0].find(text=True)),
                    'date': clean(inspection_tds[1].find(text=True)),
                    'violations': violations
                })
                
            print 'Insert ' + placeData['name']
            cityCollection.insert(placeData)

