from bs4 import BeautifulSoup
import scraperwiki
import json
import urllib
import re
import config


def clean(data):
    if data is not None:
        return data.replace(u'\xa0', '')
    return data


def getContent(url):
    html = scraperwiki.scrape(url)
    html = str.replace(html, '</=', '&le;')
    html = str.replace(html, '>/=', '&ge;')
    return BeautifulSoup(html)


def getText(element):
    return clean(element.find(text=True))


def getAllText(element):
    text = element.find_all(text=True)
    return [ clean(t) for t in text ]


def getLatLng(address, city):
    c = config.load()

    # If address is a PO Box, skip
    if re.search('P(\.)?O(\.)?(\sBox\s)[0-9]+', address) is not None:
        return None
    else:
        url = 'https://api.smartystreets.com/street-address?'
        url += 'state=Virginia'
        url += '&city=' + urllib.quote(str(city))
        url += '&auth-id=' + c['ss_id']
        url += '&auth-token=' + c['ss_token']
        url += '&street=' + urllib.quote_plus(str(address))

        print url
        result = json.load(urllib.urlopen(url))

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