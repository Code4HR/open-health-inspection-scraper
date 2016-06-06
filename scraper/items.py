from scrapy.item import Item, Field
from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import Identity, MapCompose, TakeFirst

class HealthDistrictItem(Item):
	district_name = Field()
	district_link = Field()
	district_id = Field()
	splash_link = Field(
		output_processor=TakeFirst())

class VendorItem(Item):
	pass

class InspectionItem(Item):
	pass

class ViolationItem(Item):
	pass

class DistrictItemLoader(ItemLoader):
	default_item_class = HealthDistrictItem
	default_output_processor = Identity()
