from bs4 import BeautifulSoup
import scraperwiki

def clean(data):
    if data is not None:
        return data.replace(u'\xa0', '')
    return data

def getContent(url):
    html = scraperwiki.scrape(url)
    return BeautifulSoup(html)

def getText(element):
    return clean(element.find(text=True))

def getAllText(element):
    text = element.find_all(text=True)
    return [ clean(t) for t in text ]
