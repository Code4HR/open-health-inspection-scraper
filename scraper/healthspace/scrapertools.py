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

from bs4 import BeautifulSoup
import scraperwiki
import json
import urllib2
import re
import config


def clean(data):
    if data is not None:
        return data.replace(u'\xa0', '')
    return data


def get_content(url):
    try:
        html = scraperwiki.scrape(url)
    except urllib2.URLError, e:
        print e.reason
        exit(1)
    html = str.replace(html, '</=', '&le;')
    html = str.replace(html, '>/=', '&ge;')
    return BeautifulSoup(html)


def get_text(element):
    return clean(element.find(text=True))


def get_all_text(element):
    text = element.find_all(text=True)
    return [ clean(t) for t in text ]


def get_lat_lng(address, city, state):
    c = config.load()

    # If address is a PO Box, skip
    if re.search('P(\.)?O(\.)?(\sBox\s)[0-9]+', address) is not None or address == '':
        return None
    else:
        url = 'https://api.smartystreets.com/street-address?'
        url += 'state=' + urllib2.quote(str(state))
        url += '&city=' + urllib2.quote(str(city))
        url += '&auth-id=' + c['ss_id']
        url += '&auth-token=' + c['ss_token']
        url += '&street=' + urllib2.quote(str(address))

        result = json.load(urllib2.urlopen(url))

        if len(result) == 1:
            lat_lng = {'lat': result[0]['metadata']['latitude'], 'lng': result[0]['metadata']['longitude']}
            return lat_lng
        elif len(result) == 0:
            # return generic lat/lng if zero results so we can come back later to fix it
            lat_lng = {'lat': 36.0, 'lng': -76.0}
            return lat_lng
        else:
            print result
            exit(-1)
