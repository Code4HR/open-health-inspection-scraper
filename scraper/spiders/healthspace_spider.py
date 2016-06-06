import scrapy
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
        
        ### The initial parse of district pages
        for district in response.xpath('//tr/td'):
            ### Load district info into district item
            district_loader = DistrictItemLoader(selector = district)
            district_loader.add_xpath('district_name', './a/text()')
            district_loader.add_xpath('district_link', './a/@href')
            district_loader.add_xpath('district_id', './a/@id')

            splash_url = district.xpath('./a/@href').extract()

            if splash_url:
                request_dist =  scrapy.Request(splash_url[0], callback=self.district_splash_page,
                                                        meta={'loader':district_loader})
                yield request_dist
            ### Uncomment to output when only extracting district items
            #yield district_loader.load_item()     


    def district_splash_page(self,response):
        loader = response.meta['loader']
        post_splash = response.urljoin('web.nsf/module_facilities.xsp?module=Food')

        yield scrapy.Request(post_splash, callback=self.vendor_parse,
                                            meta={'loader':loader})
        

    def vendor_parse(self,response):
        loader = response.meta['loader']
        # Get HTML links 
        urls = response.xpath('//tr/td/a/@href').extract()

        # Get Javascript links
        js_urls = js.get_urls(response)
        if js_urls is not None:
            urls.extend(js_urls)

        for url in urls:
            loader.add_value('splash_link', str(url))
            yield loader.load_item()

####
#### Can get past carousel page by appending "module_facilities.xsp?module=Food" to the end of
#### "http://healthspace.com/Clients/VDH/$REGIONNAME/web.nsf/"


'''
# Get HTML links for district pages
        urls = response.xpath('//tr/td/a/@href').extract()

        # Get Javascript links
        js_urls = js.get_urls(response)
        if js_urls is not None:
            urls.extend(js_urls)
'''








