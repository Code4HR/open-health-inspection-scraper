import mongolab
from healthspace import scraper

print 'Connect to DB'
db = mongolab.connect()
vaEstablishments = db['va']

print 'Find Cities'
cities = scraper.getCities()

for city in cities:
    print city['name']
    
    establishments = scraper.getEstablishments(city)
    for establishment in establishments:
        
        if vaEstablishments.find_one(establishment) is not None:
            print 'Already have ' + establishment['name']
            continue
        
        print establishment['name']
        establishment = scraper.getEstablishmentDetails(establishment)
        establishment['inspections'] = scraper.getInspections(establishment, city['baseUrl'])
        vaEstablishments.insert(establishment)
