import scrapy
import re

def get_urls(self,response):
    '''
    Returns absolute URLS from Javascript
    '''

    scripts = response.xpath('//script/text()').extract()

    urls = list(filter(None, map(get_function_urls, scripts)))

    if len(urls) == 1:
        return urls[0]
    else:
        return None

def get_function_urls(script):
    '''
    Extracts URLS from functions and returns as a list
    '''

    url_list = re.findall('(?<=function\s)(.*)(?:\(thisEvent\)\s{\n)(?:location\s\=\s\")(.*)(?:\")', script)

    return [url[1] for url in url_list]
