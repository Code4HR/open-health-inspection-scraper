from scrapy.item import Item, Field

class HealthDistrictItem(Item):
	district_name = Field()
	district_link = Field()
	district_id = Field()

class VendorItem(Item):
	pass

class InspectionItem(Item):
	pass

class ViolationItem(Item):
	pass
