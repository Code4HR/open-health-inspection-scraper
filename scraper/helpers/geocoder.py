#!/usr/bin/env python3

import re
import json
from pymongo import MongoClient
from urllib import parse, request
from scrapy.utils.project import get_project_settings

settings = get_project_settings()
google_api_key = settings['GOOGLE_API_KEY']

if google_api_key is not None:
    connection = MongoClient(host=settings['MONGODB_SERVER'],
                             port=int(settings['MONGODB_PORT']))

    db = connection[settings['MONGODB_DB']]
    if settings['MONGODB_USER'] and settings['MONGODB_PWD']:
        db.authenticate(settings['MONGODB_USER'], settings['MONGODB_PWD'])

    collection = db[settings['MONGODB_COLLECTION']]

    vendors = collection.find({'needs_geocoding': True}).limit(2500)

    for vendor in vendors:

        if vendor['address'] is not None and vendor['city'] is not None:

            if re.search('P(\.)?O(\.)?(\sBox\s)[0-9]+', vendor['address']) is None and vendor['address'] != '':
                print(vendor['guid'])
                url = 'https://maps.googleapis.com/maps/api/geocode/json?'
                url += 'address=' + parse.quote_plus(vendor['address']) + '+' + parse.quote_plus(vendor['city']) + ',+VA'
                url += '&key=' + google_api_key

                response = request.urlopen(url)
                data = json.loads(response.read().decode('utf-8'))

                if len(data['results']) == 1:
                    lat_lng = {'type': 'Point',
                               'coordinates': [data['results'][0]['geometry']['location']['lng'], data['results'][0]['geometry']['location']['lat']]}

                    print(lat_lng)

                    collection.update({
                        'guid': vendor['guid']
                    }, {'$set': {
                            'geo': lat_lng,
                            'needs_geocoding': False,
                            'needs_geocoding_date': None}})

                else:

                    print('Geocoding returned ' + str(len(data['results'])) + ' results')
                    collection.update({
                        'guid': vendor['guid']
                    }, {'$set': {
                            'needs_geocoding': False,
                            'needs_geocoding_date': None}})
