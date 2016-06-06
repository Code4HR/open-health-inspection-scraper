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
        
        for district in response.xpath('//tr/td'):
            district_loader = DistrictItemLoader(selector = district)
            district_loader.add_xpath('district_name', './a/text()')
            district_loader.add_xpath('district_link', './a/@href')
            district_loader.add_xpath('district_id', './a/@id')
            yield district_loader.load_item()

    
        # Get HTML links
        urls = response.xpath('//tr/td/a/@href').extract()

        # Get Javascript links
        js_urls = js.get_urls(response)
        if js_urls is not None:
            urls.extend(js_urls)


        # Iterate over URLs and send them back to parse
        #for url in urls:
            #yield scrapy.Request(response.urljoin(url), callback=self.parse) 
     
