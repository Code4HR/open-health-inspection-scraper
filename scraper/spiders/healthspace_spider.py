import scrapy
from scrapy import Selector, Request
from scraper.helpers import vendor_javascript
from scraper.helpers import inspection_javascript
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
        '''

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
        
        #### Push past district splash page.
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
        js_urls = vendor_javascript.get_urls(self,response)
        if js_urls is not None:
            urls.extend(js_urls)

        #Push to Vendor Pages
        for url in urls:

            #Extract items from loader as is
            district_name_temp = district_loader.get_output_value('district_name')
            district_link_temp = district_loader.get_output_value('district_link')
            district_id_temp = district_loader.get_output_value('district_id')

            #OUT WITH THE OLD IN WITH THE NEW! This is so hideously inefficient
            district_loader = DistrictItemLoader(selector = Selector(response))
            district_loader.add_value('district_name', district_name_temp)
            district_loader.add_value('district_link', district_link_temp)
            district_loader.add_value('district_id', district_id_temp)

            vendor_url = response.urljoin(url)
            yield Request(vendor_url, callback=self.vendor_parser,
                                        meta={'district_loader':district_loader})


    def vendor_parser(self,response):
        '''
        Will extract all vendor info and return
        '''

        district_loader = response.meta['district_loader']
        district_loader.selector = Selector(response)

        district_loader.add_value('vendor_url', response.url)
        district_loader.add_xpath('vendor_name', '//tr/td/span[contains(@id,"nameCF1")]/text()')
        district_loader.add_xpath('vendor_location', '//tr/td/span[contains(@id,"facilityAddressCF1")]/text()')
        district_loader.add_xpath('vendor_id', '//tr/td/span[contains(@id,"documentIdCF1")]/text()')
        district_loader.add_xpath('last_inspection', '//tr/td/span[contains(@id,"lastInspectionCF1")]/text()')
        district_loader.add_xpath('vendor_type', '//tr/td/span[contains(@id,"subTypeCF1")]/text()')
        district_loader.add_xpath('vendor_status', '//tr/td/span[contains(@id,"statusCF1")]/text()')
        district_loader.add_xpath('vendor_phone', '//tr/td/span[contains(@id,"phoneCF1")]/text()')
        
        '''
        Push to Inspection Pages.
        '''

        # Get HTML links
        urls = response.xpath('//tr/td/a/@href').extract()
        # Get Javascript links
        js_urls = inspection_javascript.get_inspection_urls(self,response)
        if js_urls is not None:
            urls.extend(js_urls)

        #Initiate vendor pipeline for each URL
        for url in urls:

            inspection_url = response.urljoin(url)

            #This is insane
            district_name_temp = district_loader.get_output_value('district_name')
            district_link_temp = district_loader.get_output_value('district_link')
            district_id_temp = district_loader.get_output_value('district_id')
            vendor_url_temp = district_loader.get_output_value('vendor_url')
            vendor_name_temp = district_loader.get_output_value('vendor_name')
            vendor_location_temp = district_loader.get_output_value('vendor_location')
            vendor_id_temp = district_loader.get_output_value('vendor_id')
            last_inspection_temp = district_loader.get_output_value('last_inspection')
            vendor_type_temp = district_loader.get_output_value('vendor_type')
            vendor_status_temp = district_loader.get_output_value('vendor_status')
            vendor_phone_temp = district_loader.get_output_value('vendor_phone')

            #When I figure out the clean solution for this I'm gonna feel so stupid
            district_loader = DistrictItemLoader(selector = Selector(response))
            district_loader.add_value('district_name', district_name_temp)
            district_loader.add_value('district_link', district_link_temp)
            district_loader.add_value('district_id', district_id_temp)
            district_loader.add_value('vendor_url', vendor_url_temp)
            district_loader.add_value('vendor_name', vendor_name_temp)
            district_loader.add_value('vendor_location', vendor_location_temp)
            district_loader.add_value('vendor_id', vendor_id_temp)
            district_loader.add_value('last_inspection', last_inspection_temp)
            district_loader.add_value('vendor_type', vendor_type_temp)
            district_loader.add_value('vendor_status', vendor_status_temp)
            district_loader.add_value('vendor_phone', vendor_phone_temp)

            yield Request(inspection_url, callback=self.inspection_parser, meta={'district_loader':district_loader})


    def inspection_parser(self, response):

        district_loader = response.meta['district_loader']
        district_loader.selector = Selector(response)

        district_loader.add_xpath('inspection_date', '//*[contains(@id,"inspectionDateCF1")]/text()')
        district_loader.add_xpath('facility_type', '//*[contains(@id,"facilityTypeCF1")]/text()')
        district_loader.add_xpath('year_round_status', '//*[contains(@id,"allYearRoundCF1")]/text()')
        district_loader.add_xpath('risk_rating', '//*[contains(@id,"riskRatingEB1")]/text()')
        district_loader.add_xpath('inspection_type', '//*[contains(@id,"inspTypeCF1")]/text()')
        district_loader.add_xpath('followup_required', '//*[contains(@id,"fuiReqCF1")]/text()')
        
        yield district_loader.load_item()

    






        







