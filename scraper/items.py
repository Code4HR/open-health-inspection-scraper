from scrapy.item import Item, Field
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Identity, MapCompose, TakeFirst, Join

'''
TakeFirst stops the items from being formatted as single-valued arrays, which is hell in Mongo.
However, if TakeFirst is used on the URLs (which are extracted in the spider to keep crawling)
everything breaks. The most straightforward solution would be to use two separate fields for the
same URL item and then insert the URL through TakeFirst in the final item load.
'''

class HealthDistrictItem(Item):
	district_name = Field()
	district_link = Field(
		output_processor=Identity()
		)
	district_id = Field()

	vendor_url = Field(
		output_processor=Identity()
		)
	vendor_name = Field()
	vendor_location = Field()
	vendor_id = Field()
	last_inspection = Field()
	vendor_type = Field()
	vendor_status = Field()
	vendor_phone = Field()

	inspection_date = Field()
	facility_type = Field()
	year_round_status = Field()
	risk_rating = Field()
	inspection_type = Field()
	followup_required = Field()



class DistrictItemLoader(ItemLoader):
	default_item_class = HealthDistrictItem
	default_output_processor = TakeFirst()


