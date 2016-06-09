from scrapy.item import Item, Field
from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import Identity, MapCompose, TakeFirst

class HealthDistrictItem(Item):
	district_name = Field()
	district_link = Field()
	district_id = Field()

	vendor_url = Field()
	vendor_name = Field()
	vendor_location = Field()
	vendor_id = Field()
	last_inspection = Field()
	vendor_type = Field()
	vendor_status = Field()
	vendor_phone = Field()


class DistrictItemLoader(ItemLoader):
	default_item_class = HealthDistrictItem
	default_output_processor = Identity()


