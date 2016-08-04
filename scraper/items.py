from scrapy.item import Item, Field
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Identity, MapCompose, TakeFirst, Join


class HealthDistrictItem(Item):
	district_name = Field()
	district_link = Field()
	district_id = Field()

	vendor_link = Field()
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

	### These are used to move through the pages but will be added to the final entry with _link suffix
	### So they are not entered in dictionary form.
	### The scraper breaks if we extract them with TakeFirst(), which also forces it into an array and is clumsy.
	vendor_url = Field(
		output_processor=Identity()
		)
	district_url = Field(
		output_processor=Identity()
		)

class DistrictItemLoader(ItemLoader):
	default_item_class = HealthDistrictItem
	default_output_processor = TakeFirst()


