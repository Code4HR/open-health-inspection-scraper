from scrapy.item import Item, Field
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Identity, MapCompose, TakeFirst, Join
from slugify import slugify
import re

def vendor_guid(url):
	if url:
		matches = re.match('(http://healthspace.com/Clients/VDH/)(.*)(/web.nsf/formFacility.xsp\?id=)(.*)',url, flags=re.I)
		if matches:
			return matches.group(4)

	return None

def vendor_category(type):
	categories = {'Seasonal Fast Food Restaurant': 'Restaurant',
              'Fast Food Restaurant': 'Restaurant',
              'Full Service Restaurant': 'Restaurant',
              'Public Middle or High School Food Service': 'Education',
              'Mobile Food Unit': 'Mobile Food',
              'Private Elementary School Food Service': 'Education',
              'Child Care Food Service': 'Education',
              'Other Food Service': 'Other',
              'Mobile food unit': 'Mobile Food',
              'Public Elementary School Food Service': 'Education',
              'Dept. of Juvenile Justice Food Service': 'Government',
              'Carry Out Food Service Only': 'Grocery',
              'Commissary': 'Grocery',
              'Hotel Continental Breakfast': 'Hospitality',
              'Full Service Restaurant/Caterer': 'Restaurant',
              'Hospital Food Service': 'Medical',
              'Caterer': 'Restaurant',
              'State College Food Service': 'Education',
              'Convenience Store Food Service': 'Grocery',
              'Private Middle or High School Food Service': 'Education',
              'Bed & Breakfast Food Service': 'Hospitality',
              'Adult Care Home Food Service': 'Medical',
              'Fast Food Restaurant/Caterer': 'Restaurant',
              'Adult Day Care Food Service': 'Medical',
              'Nursing Home Food Service': 'Medical',
              'Summer Food Service Program Feeding Site': 'Education',
              'Jail Food Service': 'Government',
              'Private College Food Service': 'Education',
              'Group Home Food Service': 'Medical',
              'Seasonal Full Service Restaurant': 'Restaurant',
              'Summer Camp Food Service': 'Education',
              'Grocery Store Food Service': 'Grocery',
              'Public Elementry School Food Service': 'Education',
              'Public Primary School Food Service': 'Education',
              'Private High School Food Service': 'Education',
              'State Institution Food Service': 'Government',
              'Summer camp kitchen': 'Education',
              'Institution': 'Government',
              'Residential Child Care Institution Food Service': 'Education',
              'Summer Food Service Program Kitchen': 'Education',
              'Hotel continental breakfast': 'Hospitality',
              'Public school kitchen': 'Education',
              'Snack Bar': 'Grocery',
              'Bed & Breakfast': 'Hospitality',
              'Restaurant': 'Restaurant',
              'Private Elementry School Food Service': 'Education',
              'Adult care home food service': 'Medical'}
	return categories[type]

class VendorItem(Item):
	district_id = Field()
	district_name = Field()
	district_url = Field()
	vendor_id = Field()
	guid = Field(
		input_processor=MapCompose(vendor_guid)
	)
	name = Field()
	url = Field()
	address = Field()
	city = Field()
	vendor_location = Field()
	last_inspection_date = Field()
	search_name = Field()
	vendor_type = Field()
	vendor_status = Field()
	vendor_phone = Field()
	slug = Field(
		input_processor=MapCompose(slugify)
	)
	category = Field(
		input_processor=MapCompose(vendor_category)
	)

	inspection_date = Field()
	facility_type = Field()
	year_round_status = Field()
	risk_rating = Field()
	inspection_type = Field()
	followup_required = Field()

class VendorItemLoader(ItemLoader):
	default_item_class = VendorItem
	default_output_processor = TakeFirst()
