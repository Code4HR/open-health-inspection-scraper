import mongolab
import config
from healthspace import scraper

c = config.load()

print 'Connect to DB'
db = mongolab.connect()
va_establishments = db[c['state_abb']]

# collection of establishments to fetch
to_fetch = db['establishments_to_fetch']

# print 'Drop it like... well, you know'
# to_fetch.drop()

if to_fetch.find_one() is None:
    print 'Make a list of Establishments to Fetch'
    print 'Finding Cities'
    cities = scraper.get_cities()

    for city in cities:
        print 'Finding Establishments in ' + city['name']

        establishments = scraper.get_establishments(city)
        print 'Found ' + str(len(establishments)) + ' in ' + city['name']

        for establishment in establishments:
            to_fetch.insert(establishment)


print 'Start Fetching Establishment Data'
establishments = to_fetch.find()
added = updated = 0

for establishment in establishments:
    fetch_id = establishment['_id']
    existing = va_establishments.find_one({'url': establishment['url']})
    if existing is not None:
        if 'last_inspected_date' not in existing or \
                existing['last_inspected_date'] < establishment['last_inspected_date']:
            changed_fields = []
            establishment = scraper.get_establishment_details(establishment)
            establishment['inspections'] = scraper.get_inspections(establishment, establishment['baseUrl'])
            del establishment['baseUrl']  # Need to remove 'baseUrl' and 'inserted' before comparing or inserting
            del establishment['inserted']
            establishment['_id'] = existing['_id']  # Must set establishment id to existing or it won't update
                                                    # correctly
            changed_fields = list(o for o in establishment if existing[o] != establishment[o])
        else:
            continue
    else:
        establishment = scraper.get_establishment_details(establishment)
        establishment['inspections'] = scraper.get_inspections(establishment, establishment['baseUrl'])
        establishment['_id'] = None  # This is necessary to get a new ID from mongoDB when inserting
        changed_fields = ['None']

    if changed_fields:
        if any(key in changed_fields for key in ('address', 'city', 'None')):
            #pass
            establishment = scraper.get_establishment_geo(establishment)  # This is required to update coordinates

        va_establishments.update({'_id': establishment['_id']},
                                 establishment,
                                 True)

        if 'None' in changed_fields:
            print '\t' + establishment['name'] + ' Added!'
            added += 1
        else:
            print '\t' + establishment['name'] + ' Updated!'
            updated += 1

    to_fetch.remove({'_id': fetch_id})


print str(added) + ' new vendors added'
print str(updated) + ' existing vendors updated'

