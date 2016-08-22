import os

SPIDER_MODULES = ['scraper.spiders']

LOG_LEVEL = 'INFO'
DOWNLOAD_DELAY = 0.5
JOBDIR = 'job'

ITEM_PIPELINES = {'scraper.pipelines.MongoDBPipeline': 300}

MONGODB_SERVER = os.getenv('MONGODB_SERVER', 'localhost')
MONGODB_PORT = os.getenv('MONGODB_PORT', 27017)
MONGODB_DB = os.getenv('MONGODB_DB', 'healthdata')
MONGODB_COLLECTION = os.getenv('MONGODB_COLLECTION', 'va')

SS_ID = os.getenv('SSID', None)
SS_TOKEN = os.getenv('SS_TOKEN', None)
