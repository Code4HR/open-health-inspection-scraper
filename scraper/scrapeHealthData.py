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

import sys
import mongolab
import config
from healthspace import scraper


c = config.load()

print 'Connect to DB'
db = mongolab.connect()
dest_collection = db[c['state_abb']]

# collection of establishments to fetch
to_fetch = db['establishments_to_fetch']

if to_fetch.find_one() is None:
    print 'Make a list of Establishments to Fetch'
    print 'Finding Cities'
    cities = scraper.get_cities()

    for city in cities:
        print 'Finding Establishments in {0} ({1})'.format(city['name'], city['locality'])
        establishments = scraper.get_establishments(city)
        print 'Found {0} in {1} ({2})'.format(len(establishments), city['name'], city['locality'])

        for establishment in establishments:
            to_fetch.insert(establishment)


print 'Start Fetching Establishment Data'
count_to_fetch = to_fetch.count()
establishment = to_fetch.find_one()
added = updated = 0


while establishment is not None:
    fetch_id = establishment['_id']
    existing = dest_collection.find_one({'url': establishment['url']})
    if existing is not None:
        if 'last_inspection_date' not in existing or \
                existing['last_inspection_date'] is None or \
                establishment['last_inspection_date'] is None or \
                existing['last_inspection_date'] < establishment['last_inspection_date']:
            changed_fields = []
            establishment = scraper.get_establishment_details(establishment)
            establishment['inspections'] = scraper.get_inspections(establishment, establishment['baseUrl'])
            del establishment['baseUrl']  # Need to remove 'baseUrl' and 'inserted' before comparing or inserting
            del establishment['inserted']
            establishment['_id'] = existing['_id']  # Must set establishment id to existing or it won't update
                                                    # correctly
            changed_fields = list(o for o in establishment if existing[o] != establishment[o])
        else:
            sys.stdout.write(str(to_fetch.count()) + '\r')
            sys.stdout.flush()
            to_fetch.remove({'_id': fetch_id})
            establishment = to_fetch.find_one()
            continue
    else:
        establishment = scraper.get_establishment_details(establishment)
        establishment['inspections'] = scraper.get_inspections(establishment, establishment['baseUrl'])
        establishment['_id'] = mongolab.new_id()
        changed_fields = ['None']

    if changed_fields:
        establishment = scraper.get_establishment_geo(establishment)  # This is required to update coordinates
        dest_collection.update({'_id': establishment['_id']},
                           establishment,
                           True)
    
    percentage_done = str(100 - int(float(to_fetch.count()) / float(count_to_fetch) * 100))
    if 'None' in changed_fields:
        print '\t' + establishment['name'] + ' Added! (' + percentage_done + '%)'
        added += 1
    else:
        print '\t' + establishment['name'] + ' Updated! (' + percentage_done + '%)'
        updated += 1

    to_fetch.remove({'_id': fetch_id})
    establishment = to_fetch.find_one()


print str(added) + ' new establishments added'
print str(updated) + ' existing establishments updated'

