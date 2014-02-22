from bs4 import BeautifulSoup
import pymongo
from pymongo import MongoClient
import scraperwiki

def clean(data):
    if data is not None:
        return data.replace(u'\xa0', ' ')
    return data

print 'Connect to DB'

client = MongoClient('mongodb://cfa:cfa123@ds033639.mongolab.com:33639/healthdata')
db = client.healthdata
portsmouthHealthData = db.portsmouth

print 'Start scraping!'

html = scraperwiki.scrape('http://www.healthspace.ca/Clients/VDH/Portsmouth/Portsmouth_Website.nsf/Food-List-ByName?OpenView&Count=1000&RestrictToCategory=70897540482179BC0538F63E883AEA74')

places = BeautifulSoup(html)

for place in places.find_all('tr'):

    #place = places.find_all('tr')[3]

    tds = place.find_all('td')

    if len(tds) == 4 and tds[0] is not None and tds[0].a is not None:
    
        placeData = {
            'name' : clean(tds[0].find(text=True)),
            'address' : clean(tds[2].find(text=True)),
            'last_inspection_date' : clean(tds[3].find(text=True))
        }
        
        if portsmouthHealthData.find_one(placeData) is not None:
            print 'Already have ' + placeData['name']
            continue
        
        html = scraperwiki.scrape('http://www.healthspace.ca/' + tds[0].a['href'])
        placeDetails = BeautifulSoup(html)
        inspections = placeDetails.find_all(text='Inspection Type')[0].find_parent('table').find_all('tr')

        placeData['inspections'] = []

        for inspection in inspections:
            inspection_tds = inspection.find_all('td')
        
            if(inspection_tds[0].a is None):
                continue
        
            html = scraperwiki.scrape('http://www.healthspace.ca/Clients/VDH/Portsmouth/Portsmouth_Website.nsf/' + inspection_tds[0].a['href'])
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
        portsmouthHealthData.insert(placeData)

