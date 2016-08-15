import scrapy
from scrapy import Selector, Request
from scraper.helpers import vendor_javascript
from scraper.helpers import inspection_javascript
from scraper.items import VendorItem, VendorItemLoader
from urllib import parse

class HealthSpaceSpider(scrapy.Spider):
    name = "healthspace"
    allowed_domains = ["healthspace.com"]
    start_urls = [
        "http://healthspace.com/Clients/VDH/VDH/web.nsf/module_healthRegions.xsp"
    ]

    def parse(self, response):
        '''
        TODO
        Connect to Mongo
        Group inspections into dicts and add as single vals to the main vendor entry
        Check if entry is present in DB and if not, update
        '''

        '''
        mongodb doc https://realpython.com/blog/python/web-scraping-with-scrapy-and-mongodb/
        '''

        '''
        This runs pretty linearly straight down the file, each function calls the one beneath it
        the final item loader passes a loaded item all the way back up to get output
        '''

        ### Initial parse of district pages
        for district in response.xpath('//tr/td'):

            district_info = {
                'name': district.xpath('./a/text()').extract_first(),
                'url': district.xpath('./a/@href').extract_first(),
                'id': district.xpath('./a/@id').extract_first()
            }

            if district_info['url']:
                # Skip the district splash page
                district_info['url'] = parse.urljoin(district_info['url'], 'web.nsf/module_facilities.xsp?module=Food')

                yield Request(district_info['url'], callback=self.district_catalog_parse,
                                                  meta={'district_info': district_info})


    def district_catalog_parse(self,response):
        '''
        Receives the district_loader and main vendor catalog page
        Extracts all URLs from vendor page, sends each new URL
        to the next step in the pipeline, eventually returning the
        full loaded district_loader back to main parse.
        '''

        district_info = response.meta['district_info']

        # Get HTML links
        urls = response.xpath('//tr/td/a/@href').extract()
        # Get Javascript links
        js_urls = vendor_javascript.get_urls(self,response)
        if js_urls is not None:
            urls.extend(js_urls)

        #Push to Vendor Pages
        for url in urls:
            vendor_url = response.urljoin(url)

            yield Request(vendor_url, callback=self.vendor_parser,
                                    meta={'district_info':district_info})


    def vendor_parser(self,response):
        district_info = response.meta['district_info']

        vendor_loader = VendorItemLoader(response=response)

        vendor_loader.add_value('district_id', district_info['id'])
        vendor_loader.add_value('district_name', district_info['name'])
        vendor_loader.add_value('district_url', district_info['url'])

        vendor_loader.add_xpath('vendor_id', '//tr/td/span[contains(@id,"documentIdCF1")]/text()')
        vendor_loader.add_value('guid', response.url)
        vendor_loader.add_xpath('name', '//tr/td/span[contains(@id,"nameCF1")]/text()')
        vendor_loader.add_value('url', response.url)
        vendor_loader.add_xpath('vendor_location', '//tr/td/span[contains(@id,"facilityAddressCF1")]/text()')
        vendor_loader.add_xpath('last_inspection_date', '//tr/td/span[contains(@id,"lastInspectionCF1")]/text()')
        vendor_loader.add_xpath('vendor_type', '//tr/td/span[contains(@id,"subTypeCF1")]/text()')
        vendor_loader.add_xpath('category', '//tr/td/span[contains(@id,"subTypeCF1")]/text()')
        vendor_loader.add_xpath('vendor_status', '//tr/td/span[contains(@id,"statusCF1")]/text()')
        vendor_loader.add_xpath('vendor_phone', '//tr/td/span[contains(@id,"phoneCF1")]/text()')
        vendor_loader.add_value('slug', vendor_loader.get_output_value('name') + ' ' + vendor_loader.get_output_value('vendor_location'))

        # Push to Inspection Pages.

        # Get HTML links
        urls = response.xpath('//tr/td/a/@href').extract()
        # Get Javascript links
        js_urls = inspection_javascript.get_inspection_urls(self,response)
        if js_urls is not None:
            urls.extend(js_urls)

        #Initiate vendor pipeline for each URL
        for url in urls:

            inspection_url = response.urljoin(url)

'''
            yield Request(inspection_url, callback=self.inspection_parser, meta={'vendor_loader':vendor_loader})


    def inspection_parser(self, response):

        vendor_loader = response.meta['vendor_loader']
        vendor_loader.selector = Selector(response)

        vendor_loader.add_xpath('inspection_date', '//*[contains(@id,"inspectionDateCF1")]/text()')
        vendor_loader.add_xpath('facility_type', '//*[contains(@id,"facilityTypeCF1")]/text()')
        vendor_loader.add_xpath('year_round_status', '//*[contains(@id,"allYearRoundCF1")]/text()')
        vendor_loader.add_xpath('risk_rating', '//*[contains(@id,"riskRatingEB1")]/text()')
        vendor_loader.add_xpath('inspection_type', '//*[contains(@id,"inspTypeCF1")]/text()')
        vendor_loader.add_xpath('followup_required', '//*[contains(@id,"fuiReqCF1")]/text()')

        yield vendor_loader.load_item()
'''
