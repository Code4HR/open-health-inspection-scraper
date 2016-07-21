import pymongo

from scrapy.conf import settings
from scrapy.exceptions import DropItem

import logging
logger = logging.getLogger(__name__)


class MongoPipeline(object):

	def __init__(self):

		### ???Involved in duplicate handling???
		self.ids_seen = set()

		### Set up database connection (pulled from settings)
		connection = pymongo.MongoClient(
			settings['MONGODB_SERVER'],
			settings['MONGODB_PORT']
		)

		db = connection[settings['MONGODB_DB']]
		self.collection = db[settings['MONGODB_COLLECTION']]


	def process_item(self, item, spider):

		valid = True

		for data in item:

			if not data:
				valid = False
				raise DropItem("Missing {0}!".format(data))

		if valid:

			### This stuff is iffy
			if item['id'] in self.ids_seen:

				raise DropItem("Duplicate item found: %s" % item)

			else:

				self.collection.insert(dict(item))
				return item
	