from bs4 import BeautifulSoup
import scraperwiki
import json
import urllib
import re

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

    api_url = "http://maps.googleapis.com/maps/api/geocode/json?sensor=false" \
              "&components=country:US|administrative_area_level_1:VA" \
              "&address="
    # If address is a PO Box, search for just city/state
    if re.search('P(\.)?O(\.)?(\sBox\s)[0-9]+', address) is not None:
        url = api_url + urllib.quote_plus(city + ", VA")
    else:
        url = api_url + urllib.quote_plus(str(address).replace('.', '') + " " + city + ", VA")
    print url
    result = json.load(urllib.urlopen(url))

    if result['status'] == 'OK':
        lat_lng = {'lat': result['results'][0]['geometry']['location']['lat'], 'lng': result['results'][0]['geometry']['location']['lng']}
        return lat_lng
    elif result['status'] == 'ZERO_RESULTS':
        # return generic lat/lng if zero results so we can come back later to fix it
        lat_lng = {'lat': 36.0, 'lng': -76.0}
        return lat_lng
    else:
        print result['status']
        if 'error_message' in result: print result['error_message']
        exit(-1)