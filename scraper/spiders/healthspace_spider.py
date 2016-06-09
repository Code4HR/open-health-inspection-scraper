import scrapy
from scrapy import Selector, Request
from scraper.helpers import javascript as js
from scraper.items import HealthDistrictItem, DistrictItemLoader


class HealthSpaceSpider(scrapy.Spider):
    name = "healthspace"
    allowed_domains = ["healthspace.com"]
    start_urls = [
        "http://healthspace.com/Clients/VDH/VDH/web.nsf/module_healthRegions.xsp"
    ]

    def parse(self, response):
        '''
        parse performs three tasks:
        1) Categorize what kind of page this is (district, vendor, etc.)
           and send it off to an appropriate parsing function
        2) Identify any anchor URLs and return them to the parse function
        3) Extract and identify any Javascript URLs in span tags and return
           them to the parse function
        TODO: Read HTML body;
        Identify URL's in <span> tags
        Extract URL from JS Function
        Pass URL list
        '''

        ### Initial parse of district pages
        for district in response.xpath('//tr/td'):
            
            district_loader = DistrictItemLoader(selector = district)

            district_loader.add_xpath('district_name', './a/text()')
            district_loader.add_xpath('district_link', './a/@href')
            district_loader.add_xpath('district_id', './a/@id')

            district_splash_url = district_loader.get_output_value('district_link')

            if district_splash_url:

                yield Request(district_splash_url[0], callback=self.district_splash_page,
                                                        meta={'district_loader': district_loader})


    def district_splash_page(self,response):
        '''
        Receives the main district_loader itemloader
        and passes it to the correct vendor catalog for
        the district.
        '''
        
        district_loader = response.meta['district_loader']
        vendor_catalog_url = response.urljoin('web.nsf/module_facilities.xsp?module=Food')

        yield Request(vendor_catalog_url, callback=self.vendor_catalog_parse,
                                            meta={'district_loader': district_loader})


    def vendor_catalog_parse(self,response):
        '''
        Receives the district_loader and main vendor catalog page
        Extracts all URLs from vendor page, sends each new URL
        to the next step in the pipeline, eventually returning the
        full loaded district_loader back to main parse.
        '''

        district_loader = response.meta['district_loader']

        # Get HTML links
        urls = response.xpath('//tr/td/a/@href').extract()
        # Get Javascript links
        js_urls = js.get_urls(response)
        if js_urls is not None:
            urls.extend(js_urls)

        #Initiate vendor pipeline for each URL
        for url in urls:
            district_name_to_vendor = district_loader.get_output_value('district_name')
            district_link_to_vendor = district_loader.get_output_value('district_link')

            district_loader = DistrictItemLoader(selector = Selector(response))
            district_loader.add_value('district_name', district_name_to_vendor)
            district_loader.add_value('district_link', district_link_to_vendor)

            vendor_url = response.urljoin(url)
            yield Request(vendor_url, callback=self.vendor_parser,
                                        meta={'district_loader':district_loader})


    def vendor_parser(self,response):
        '''
        Will extract all vendor info and return
        '''

        district_loader = response.meta['district_loader']
        district_loader.selector = Selector(response)

        test_url = response.url

        district_loader.add_value('vendor_url', test_url)
        district_loader.add_xpath('vendor_name', '//tr/td/span[@id="view:_id1:_id175:nameCF1"]/text()')
        district_loader.add_xpath('vendor_location', '//tr/td/span[@id="view:_id1:_id175:facilityAddressCF1"]/text()')
        district_loader.add_xpath('vendor_id', '//tr/td/span[@id="view:_id1:_id175:documentIdCF1"]/text()')
        district_loader.add_xpath('last_inspection', '//tr/td/span[@id="view:_id1:_id175:lastInspectionCF1"]/text()')
        district_loader.add_xpath('vendor_type', '//tr/td/span[@id="view:_id1:_id175:subTypeCF1"]/text()')
        district_loader.add_xpath('vendor_status', '//tr/td/span[@id="view:_id1:_id175:statusCF1"]/text()')
        district_loader.add_xpath('vendor_phone', '//tr/td/span[@id="view:_id1:_id175:phoneCF1"]/text()')

        yield district_loader.load_item()


