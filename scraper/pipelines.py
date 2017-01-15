import logging
from pymongo import MongoClient
from scrapy.exceptions import DropItem
from scraper.items import VendorItem, InspectionItem
from datetime import datetime
from scrapy.utils.project import get_project_settings

logger = logging.getLogger('Mongo Pipeline')

class MongoDBPipeline(object):

	def __init__(self):
		settings = get_project_settings()

		connection = MongoClient(host=settings['MONGODB_SERVER'],
		                         port=int(settings['MONGODB_PORT']))
								 
		db = connection[settings['MONGODB_DB']]
		if settings['MONGODB_USER'] and settings['MONGODB_PWD']:
			db.authenticate(settings['MONGODB_USER'], settings['MONGODB_PWD'])

		self.collection = db[settings['MONGODB_COLLECTION']]


	def process_item(self, item, spider):
		# Vendor Data
		if isinstance(item, VendorItem):
			vendor = dict(item)

			# Check if vendor exists, if so just update
			if self.collection.find({'guid': item['guid']}).count() > 0:
				# Remove empty inspections array for existing vendors
				vendor.pop('inspections', None)

				self.collection.update({
					'guid': vendor['guid']
				}, {'$set': vendor})

				logger.debug('Updated vendor ' + str(vendor['guid']))

			else:
				# If the vendor is new insert
				self.collection.insert_one(vendor)

				logger.debug('Added new vendor ' + str(vendor['guid']))

		# Inspection Data
		if isinstance(item, InspectionItem):
			inspection = dict(item)

			# Remove vendor_guid because we don't want it in the dict
			# we just passed it to use for lookup
			vendor_guid = inspection.pop('vendor_guid')

			# Make sure the vendor exists, if not log a warning
			if self.collection.find({'guid': vendor_guid}).count() > 0:
				# Check if the inspection exists
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

				# If it exists, update
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
						logger.debug('Updated inspection from ' + inspection['date'].strftime("%m/%d/%Y") + ' for vendor ' + vendor_guid)

				# If it is new, push the inspection into the inspections array
				else:
					result = self.collection.update({
						'guid': vendor_guid
					}, {
						'$push': {'inspections': inspection}
					})

					# Check to see that it inserted correctly
					if result['n'] is not 1:
						logger.warn('Could not add inspection from ' + inspection['date'].strftime("%m/%d/%Y") + ' for vendor ' + vendor_guid)
					else:
						logger.debug('Added new inspection from ' + inspection['date'].strftime("%m/%d/%Y") + ' for vendor ' + vendor_guid)
			else:
				logger.warn('Attempted to add/update inspection but could not find vendor ' + vendor_guid)
