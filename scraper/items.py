from scrapy.item import Item, Field
from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import Identity, MapCompose, TakeFirst

class HealthDistrictItem(Item):
	district_name = Field()
	district_link = Field()
	district_id = Field()
	vendor_info = Field(
		output_processor=Identity())

class VendorItem(Item):
	vendor_url = Field()
	vendor_name = Field()

class InspectionItem(Item):
	pass

class ViolationItem(Item):
	pass

class DistrictItemLoader(ItemLoader):
	default_item_class = HealthDistrictItem
	default_output_processor = Identity()

class VendorItemLoader(ItemLoader):
	default_item_class = VendorItem
	default_output_processor = Identity()
