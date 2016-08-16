import scrapy
import re

def get_inspection_urls(self, response):
    '''
    Returns absolute URLS from Javascript
    '''
    scripts = response.xpath('//script/text()').extract()

    urls = list(filter(None, map(get_function_urls, scripts)))

    if len(urls) == 1:
        return urls[0]

def get_function_urls(script):
    '''
    Extracts broken down URLs from functions, appends them and returns a list
    '''
    facunid = re.findall('(?:facunid\s\=\s\")(.*)(?:\")', script)
    inspunid = re.findall('(?:inspunid\s\=\s\")(.*)(?:\")', script)
    bangstr = re.findall('(?:bangstr\s\=\s\")(.*)(?:\")', script)

    #Need to loop through each index and associate all the parts
    url_list = []
    if bangstr and inspunid and facunid:
        for index in range(len(facunid)):
            turl = 'formInspection.xsp?databaseName=' + str(bangstr[index])
            turl += '&documentId=' + str(inspunid[index])
            turl += '&id=' + str(facunid[index])
            turl += '&action=openDocument'

            url_list.append(turl)
        return [url for url in url_list]

def logger_check(self,response):
    '''
    Just some logging stuff to check
    '''
    scripts = response.xpath('//script/text()').extract()

    
    for script in scripts:
        facunid = re.findall('(?:facunid\s\=\s\")(.*)(?:\")', script)
        inspunid = re.findall('(?:inspunid\s\=\s\")(.*)(?:\")', script)
        bangstr = re.findall('(?:bangstr\s\=\s\")(.*)(?:\")', script)
        #turl = 'formInspection.xps?databaseName=' + bangstr
        #turl += '&documentId=' + inspunid
        #turl += '&id=' + facunid
        #turl += '&action=openDocument'
        self.logger.info('THE SCRIPTS ARE %s', script)
        self.logger.info('FACUNID %s', facunid)
        self.logger.info('INSPUNID %s', inspunid)
        self.logger.info('BANGSTR %s', bangstr)
    return url_list



