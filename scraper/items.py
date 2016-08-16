from scrapy.item import Item, Field
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Identity, MapCompose, TakeFirst, Join
from scraper.helpers.vendor_helpers import *
from slugify import slugify
from datetime import datetime
import re

def format_date(date_string):
	return datetime.strptime(date_string, "%b %d, %Y")


class VendorItem(Item):
	locality_id = Field()
	locality = Field()
	locality_url = Field()
	vendor_id = Field()
	guid = Field(
		input_processor=MapCompose(vendor_guid)
	)
	name = Field()
	url = Field()
	address = Field(
		input_processor=MapCompose(vendor_address)
	)
	city = Field(
		input_processor=MapCompose(vendor_city)
	)
	vendor_location = Field()
	last_inspection_date = Field(
		input_processor=MapCompose(format_date)
	)
	search_name = Field(
		input_processor=MapCompose(vendor_search_name)
	)
	type = Field()
	status = Field()
	phone = Field()
	slug = Field(
		input_processor=MapCompose(slugify)
	)
	category = Field(
		input_processor=MapCompose(vendor_category)
	)

class VendorItemLoader(ItemLoader):
	default_item_class = VendorItem
	default_output_processor = TakeFirst()

class InspectionItem(Item):
	vendor_guid = Field()
	date = Field(
		input_processor=MapCompose(format_date)
	)
	type = Field()
	risk_rating = Field()
	followup_required = Field()
	comments = Field(
		input_processor=Join('')
	)
	violations = Field()

class InspectionItemLoader(ItemLoader):
	default_item_class = InspectionItem
	default_output_processor = TakeFirst()
