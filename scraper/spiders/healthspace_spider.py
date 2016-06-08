import scrapy
from scrapy import Selector, Request
from scraper.helpers import javascript as js
from scraper.items import HealthDistrictItem, DistrictItemLoader, VendorItem, VendorItemLoader


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

        ### The initial parse of district pages
        for district in response.xpath('//tr/td'):
            ### Load district info into district item
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
            district_loader.add_value('vendor_info', self.vendor_parser(response,url))

        yield district_loader.load_item()


    '''
    Having serious logic issues with this stuff below
    '''

    def vendor_parser(self,response,url):
        '''
        Will extract all vendor info and return
        '''
        vendor_loader = VendorItemLoader(selector=Selector(response))
        vendor_url = response.urljoin(url)
        vendor_request = Request(vendor_url, callback=self.vendor_parse_2,
                                            meta={'vendor_loader': vendor_loader})
        vendor_loader.add_value('vendor_url', vendor_loader.get_output_value('vendor_url'))
        yield vendor_loader.load_item()


    def vendor_parse_2(self, response):
        '''
        Possibly necessary to push a new request
        to access the vendor page itself
        '''
        vendor_loader = response.meta['vendor_loader']
        vendor_loader.add_value('vendor_url', 'test_url')
        vendor_loader.add_value('vendor_name', 'test_name')

        yield vendor_loader.load_item()
