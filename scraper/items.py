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
	locality_id = Field(
		output_processor=TakeFirst()
	)
	locality = Field(
		output_processor=TakeFirst()
	)
	locality_url = Field(
		output_processor=TakeFirst()
	)
	vendor_id = Field(
		output_processor=TakeFirst()
	)
	guid = Field(
		input_processor=MapCompose(vendor_guid),
		output_processor=TakeFirst()
	)
	name = Field(
		output_processor=TakeFirst()
	)
	url = Field(
		output_processor=TakeFirst()
	)
	address = Field(
		input_processor=MapCompose(vendor_address),
		output_processor=TakeFirst()
	)
	city = Field(
		input_processor=MapCompose(vendor_city),
		output_processor=TakeFirst()
	)
	vendor_location = Field(
		output_processor=TakeFirst()
	)
	last_inspection_date = Field(
		input_processor=MapCompose(format_date),
		output_processor=TakeFirst()
	)
	search_name = Field(
		input_processor=MapCompose(vendor_search_name),
		output_processor=TakeFirst()
	)
	type = Field(
		output_processor=TakeFirst()
	)
	status = Field(
		output_processor=TakeFirst()
	)
	phone = Field(
		output_processor=TakeFirst()
	)
	slug = Field(
		input_processor=MapCompose(slugify),
		output_processor=TakeFirst()
	)
	category = Field(
		input_processor=MapCompose(vendor_category),
		output_processor=TakeFirst()
	)
	geo = Field(
		# disable geocoding until SmartyStreets replacement is found
		#input_processor=MapCompose(get_lat_lng),
		#output_processor=TakeFirst()
	)
	needs_geocoding = Field(
		input_processor=MapCompose(needs_geocoding),
		output_processor=TakeFirst()
	)
	needs_geocoding_date = Field(
		input_processor=MapCompose(needs_geocoding_date),
		output_processor=TakeFirst()
	)
	inspections = Field()

class VendorItemLoader(ItemLoader):
	default_item_class = VendorItem

class InspectionItem(Item):
	vendor_guid = Field(
		output_processor=TakeFirst()
	)
	date = Field(
		input_processor=MapCompose(format_date),
		output_processor=TakeFirst()
	)
	type = Field(
		output_processor=TakeFirst()
	)
	risk_rating = Field(
		output_processor=TakeFirst()
	)
	followup_required = Field(
		output_processor=TakeFirst()
	)
	comments = Field(
		input_processor=Join(''),
		output_processor=TakeFirst()
	)
	violations = Field()

class InspectionItemLoader(ItemLoader):
	default_item_class = InspectionItem
