### Code to parse district page using Item/Field syntax (instead of ItemLoader)
 '''
health_district_item = HealthDistrictItem()
health_district_item['district_name'] = district.xpath('a/text()').extract()
health_district_item['district_link'] = district.xpath('a/@href').extract()
health_district_item['district_id'] = district.xpath('a/@id').extract()
yield health_district_item
'''


### Code to parse distict with itemloader
'''
district_loader = DistrictItemLoader(selector = district)
district_loader.add_xpath('district_name', './a/text()')
district_loader.add_xpath('district_link', './a/@href')
district_loader.add_xpath('district_id', './a/@id')
yield district_loader.load_item()
'''