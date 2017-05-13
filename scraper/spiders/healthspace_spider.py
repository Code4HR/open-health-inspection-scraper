import scrapy
import logging
import shutil
from scrapy import Selector, Request
from scraper.helpers import vendor_helpers, inspection_helpers
from scraper.helpers.scoring import Scoring
from scraper.items import VendorItemLoader, InspectionItemLoader
from urllib import parse

logger = logging.getLogger('Healthspace Spider')

class HealthSpaceSpider(scrapy.Spider):
    name = "healthspace"
    allowed_domains = ["healthspace.com"]
    start_urls = [
        "http://healthspace.com/Clients/VDH/VDH/web.nsf/module_healthRegions.xsp"
    ]

    def closed(self, reason):
        # If the spider completes successfully, cleanup the job
        # so we can start fresh the next time
        if reason == 'finished' and 'JOBDIR' in self.settings:
                shutil.rmtree(self.settings['JOBDIR'])
                scoring = Scoring(self.settings)
                scoring.score_vendors()

    def parse(self, response):
        # Initial parse of district pages
        localities = response.xpath('//tr/td')

        for locality in localities:

            locality_info = {
                'name': locality.xpath('./a/text()').extract_first(),
                'url': locality.xpath('./a/@href').extract_first(),
                'id': locality.xpath('./a/@id').extract_first()
            }

            if locality_info['url']:
                #Skip the locality splash page
                locality_info['url'] = parse.urljoin(locality_info['url'], 'web.nsf/module_facilities.xsp?module=Food')

                yield Request(locality_info['url'], callback=self.locality_catalog_parse,
                                                    meta={'locality_info': locality_info,
                                                          'page_num': 1,
                                                          'cookiejar': locality_info['name']})
                                                          # Each locality needs a separate cookiejar
                                                          # so that paging works correctly in the
                                                          # catalog parse.


    def locality_catalog_parse(self,response):
        '''
        Receives the locality_info and main vendor catalog page
        Extracts all URLs from vendor page, sends each new URL
        to the vendor parser.
        '''

        locality_info = response.meta['locality_info']

        logger.info('Parsing ' + str(locality_info['name']) + ' Page ' + str(response.meta['page_num']))

        # Check if another page is available for this locality, if so send
        # it back to the parser. Uses the 'Next' button on the locality
        # page, which triggers a POST request to get more vendors.
        if response.xpath('//a[contains(@id, "Next__lnk")]'):
            ajax_id = 'view:_id1:_id228:panel1'

            page_body = {
            '$$viewid': response.xpath('//form/input[@name="$$viewid"]/@value').extract_first(),
            '$$xspexecid': response.xpath('//a[contains(@id, "Next__lnk")]/parent::span/parent::div/@id').extract_first(),
            '$$xspsubmitid': response.xpath('//a[contains(@id, "Next__lnk")]/parent::span/@id').extract_first(),
            '$$xspsubmitscroll': '0|0',
            '$$xspsubmitvalue': response.xpath('//form/input[@name="$$xspsubmitvalue"]/@value').extract_first(),

            }

            # POST body includes a field that references it's own value.
            page_body[response.xpath('//form/@id').extract_first()] = response.xpath('//form/@id').extract_first()

            page_url = response.url + '&$$ajaxid=' + parse.quote('view:_id1:_id228:panel1')

            yield Request(response.url, callback=self.locality_catalog_parse,
                                        method='POST',
                                        body=parse.urlencode(page_body),
                                        meta={'locality_info':locality_info,
                                              'page_num': response.meta['page_num']+1,
                                              'cookiejar': response.meta['cookiejar']},
                                        dont_filter=True) # Need dont_filter so the job
                                                          # tracker will accept the same
                                                          # URL more than once

        # Get HTML links
        urls = response.xpath('//tr/td/a/@href').extract()

        # Get Javascript links
        js_urls = vendor_helpers.get_urls(self,response)
        if js_urls is not None:
            urls.extend(js_urls)

        #Push to Vendor Pages
        for url in urls:
            vendor_url = response.urljoin(url)

            yield Request(vendor_url, callback=self.vendor_parser,
                                      meta={'locality_info':locality_info,
                                            'cookiejar': 'vendors'})
                                            # Create a separate cookiejar for
                                            # vendors so that the locality pages
                                            # don't lose state.


    def vendor_parser(self,response):
        '''
        Extracts core vendor information from pages which is then processed into MongoDB.
        Also extracts links to inspections and passes that to the inspection parser.
        '''
        locality_info = response.meta['locality_info']

        vendor_loader = VendorItemLoader(response=response)

        vendor_loader.add_value('locality_id', locality_info['id'])
        vendor_loader.add_value('locality', locality_info['name'])
        vendor_loader.add_value('locality_url', locality_info['url'])

        vendor_loader.add_xpath('vendor_id', '//tr/td/span[contains(@id,"documentIdCF1")]/text()')
        vendor_loader.add_value('guid', response.url)
        vendor_loader.add_xpath('name', '//tr/td/span[contains(@id,"nameCF1")]/text()')
        vendor_loader.add_value('search_name', vendor_loader.get_output_value('name'))
        vendor_loader.add_value('url', response.url)
        vendor_loader.add_xpath('vendor_location', '//tr/td/span[contains(@id,"facilityAddressCF1")]/text()')
        vendor_loader.add_value('address', vendor_loader.get_output_value('vendor_location'))
        vendor_loader.add_value('city', vendor_loader.get_output_value('vendor_location'))
        vendor_loader.add_xpath('last_inspection_date', '//tr/td/span[contains(@id,"lastInspectionCF1")]/text()')
        vendor_loader.add_xpath('type', '//tr/td/span[contains(@id,"subTypeCF1")]/text()')
        vendor_loader.add_xpath('category', '//tr/td/span[contains(@id,"subTypeCF1")]/text()')
        vendor_loader.add_xpath('status', '//tr/td/span[contains(@id,"statusCF1")]/text()')
        vendor_loader.add_xpath('phone', '//tr/td/span[contains(@id,"phoneCF1")]/text()')
        vendor_loader.add_value('slug', vendor_loader.get_output_value('name') + ' ' + vendor_loader.get_output_value('vendor_location'))

        address = {
            'guid': vendor_loader.get_output_value('guid'),
            'street': vendor_loader.get_output_value('address'),
            'city': vendor_loader.get_output_value('city'),
            'state': 'VA'
        }

        # Removed geocoding until a SmartyStreets replacement is found
        #vendor_loader.add_value('geo', address)
        vendor_loader.add_value('needs_geocoding', address)
        vendor_loader.add_value('needs_geocoding_date', address)

        # Load vendor info
        yield vendor_loader.load_item()

        # Grab inspection links and hand to parser.

        # Get HTML links
        urls = response.xpath('//tr/td/a/@href').extract()
        # Get Javascript links
        js_urls = inspection_helpers.get_inspection_urls(self,response)
        if js_urls is not None:
            urls.extend(js_urls)

        # Parse vendor inspections
        for url in urls:

            inspection_url = response.urljoin(url)

            yield Request(inspection_url, callback=self.inspection_parser,
                                          meta={'vendor_guid':vendor_loader.get_output_value('guid'),
                                                'cookiejar': 'inspections'})
                                                # Create a separate cookiejar for
                                                # inspections so that the locality pages
                                                # don't lose state.


    def inspection_parser(self, response):
        '''
        Extracts core inspection and violation data which is processed into MongoDB.
        '''

        inspection_loader = InspectionItemLoader(response=response)

        inspection_loader.add_value('vendor_guid', response.meta['vendor_guid'])
        inspection_loader.add_xpath('date', '//*[contains(@id,"inspectionDateCF1")]/text()')
        inspection_loader.add_xpath('type', '//*[contains(@id,"inspTypeCF1")]/text()')
        inspection_loader.add_xpath('risk_rating', '//*[contains(@id,"riskRatingEB1")]/text()')
        inspection_loader.add_xpath('followup_required', '//*[contains(@id,"fuiReqCF1")]/text()')
        inspection_loader.add_xpath('comments', '//*[contains(@id, "commentsCF1")]/div/font/text()')

        violations = []

        violation_items = response.xpath('//div[contains(@class,"violation-panel")]')

        for violation_item in violation_items:
            observation_title = violation_item.xpath('.//span[contains(@id, "violationCF3")]/text()').extract_first()
            critical = violation_item.xpath('.//a[contains(@id,"violationCritSetLink1")]/text()').extract_first()

            violations.append({
                'code': violation_item.xpath('.//span[contains(@id,"violationCodeCF1")]/text()').extract_first(),
                'description': violation_item.xpath('.//span[contains(@id, "violationCF9")]/text()').extract_first(),
                'observation': violation_item.xpath('.//span[contains(@id, "violationCF4")]/text()').extract_first(),
                'correction': violation_item.xpath('.//span[contains(@id, "violationCF9")]/text()').extract_first(),
                'corrected': "(CORRECTED DURING INSPECTION)" in observation_title,
                'critical': critical is "critical",
                'repeat': "(REPEAT)" in observation_title
            })

        inspection_loader.add_value('violations', violations)

        yield inspection_loader.load_item()
