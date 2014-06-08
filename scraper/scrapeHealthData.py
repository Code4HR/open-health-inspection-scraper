import mongolab
import config
from healthspace import scraper

c = config.load()

print 'Connect to DB'
db = mongolab.connect()
va_establishments = db[c['state_abb']]

print 'Find Cities'
cities = scraper.get_cities()

for city in cities:

    print city['name']
    
    establishments = scraper.get_establishments(city)
    added = updated = 0

    for establishment in establishments:

        existing = va_establishments.find_one({'url': establishment['url']})

        if existing is not None:
            if 'last_inspected_date' not in existing or \
                            existing['last_inspected_date'] < establishment['last_inspected_date']:
                changed_fields = []
                establishment = scraper.get_establishment_details(establishment)
                establishment['inspections'] = scraper.get_inspections(establishment, city['baseUrl'])
                establishment['_id'] = existing['_id']
                changed_fields = list(o for o in establishment if existing[o] != establishment[o])
            else:
                continue
        else:
            establishment = scraper.get_establishment_details(establishment)
            establishment['inspections'] = scraper.get_inspections(establishment, city['baseUrl'])
            establishment['_id'] = None
            changed_fields = ['None']

        if changed_fields:
            if any(key in changed_fields for key in ('address', 'city', 'None')):
                establishment = scraper.get_establishment_geo(establishment)

            va_establishments.update({'_id': establishment['_id']},
                                     establishment,
                                     True)

            if 'None' in changed_fields:
                print establishment['name'] + ' Added!'
                added += 1
            else:
                print establishment['name'] + ' Updated!'
                updated += 1

    print str(added) + ' new vendors added'
    print str(updated) + ' existing vendors updated'

