import pymongo
import logging
from scrapy.conf import settings
from scrapy.exceptions import DropItem
from scraper.items import VendorItem, InspectionItem

logger = logging.getLogger(__name__)

class MongoDBPipeline(object):

	def __init__(self):
		### Set up database connection (pulled from settings)
		connection = pymongo.MongoClient(
			settings['MONGODB_SERVER'],
			settings['MONGODB_PORT']
		)

		db = connection[settings['MONGODB_DB']]
		self.collection = db[settings['MONGODB_COLLECTION']]


	def process_item(self, item, spider):
		if isinstance(item, VendorItem):
			vendor = dict(item)

			self.collection.update({
				'guid': vendor['guid']
			}, {'$set': vendor}, {'upsert': True})

		if isinstance(item, InspectionItem):
			inspection = dict(item)

			vendor_guid = inspection.pop('vendor_guid')

			if self.collection.find({'guid': vendor_guid}).count() > 0:
				existing = self.collection.find({
					'guid': vendor_guid,
					'inspections': {
						'$elemMatch': {
							'date': inspection['date']
						}
					}
				}, {'inspections': {
						'$elemMatch': {
							'date': inspection['date']
						}
					}
				})

				if existing:
					self.collection.update({
						'guid': vendor_guid,
						'inspections': {
							'$elemMatch': {
								'date': inspection['date']
							}
						}
					}, {'$set': {
						'inspections.$': inspection
						}

					})

				else:
					self.collection.update({
						'guide': vendor_guid
					}, {
						'$push': {inspections: inspection}
					})
