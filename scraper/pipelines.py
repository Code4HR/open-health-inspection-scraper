import pymongo
import logging
from scrapy.conf import settings
from scrapy.exceptions import DropItem
from scraper.items import VendorItem, InspectionItem
from datetime import datetime

logger = logging.getLogger(__name__)

class MongoDBPipeline(object):

	def __init__(self):
		### Set up database connection (pulled from settings)
		connection = pymongo.MongoClient(
			host=settings['MONGODB_SERVER'],
			port=int(settings['MONGODB_PORT'])
		)

		db = connection[settings['MONGODB_DB']]
		self.collection = db[settings['MONGODB_COLLECTION']]


	def process_item(self, item, spider):
		# Vendor Data
		if isinstance(item, VendorItem):
			vendor = dict(item)

			if self.collection.find({'guid': item['guid']}).count() > 0:
				# Remove empty inspections array for existing vendors
				vendor.pop('inspections', None)

				self.collection.update({
					'guid': vendor['guid']
				}, {'$set': vendor})

				logger.info('Updated vendor ' + str(vendor['guid']))

			else:
				self.collection.insert_one(vendor)

				logger.info('Added new vendor ' + str(vendor['guid']))

		# Inspection Data
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

				if existing.count() > 0:
					result = self.collection.update({
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

					if result['n'] is not 1:
						logger.warn('Could not update inspection from ' + inspection['date'].strftime("%m/%d/%Y") + ' for vendor ' + vendor_guid)
					else:
						logger.info('Updated inspection from ' + inspection['date'].strftime("%m/%d/%Y") + ' for vendor ' + vendor_guid)


				else:
					result = self.collection.update({
						'guid': vendor_guid
					}, {
						'$push': {'inspections': inspection}
					})

					if result['n'] is not 1:
						logger.warn('Could not add inspection from ' + inspection['date'].strftime("%m/%d/%Y") + ' for vendor ' + vendor_guid)
					else:
						logger.info('Added new inspection from ' + inspection['date'].strftime("%m/%d/%Y") + ' for vendor ' + vendor_guid)
			else:
				logger.warn('Attempted to add/update inspection but could not find vendor ' + vendor_guid)
