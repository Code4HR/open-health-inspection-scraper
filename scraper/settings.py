import os

SPIDER_MODULES = ['scraper.spiders']

LOG_LEVEL = 'INFO'
JOBDIR = 'job'
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1.0
AUTOTHROTTLE_MAX_DELAY = 10.0

ITEM_PIPELINES = {'scraper.pipelines.MongoDBPipeline': 300}

MONGODB_SERVER = os.getenv('MONGODB_SERVER', 'localhost')
MONGODB_PORT = os.getenv('MONGODB_PORT', 27017)
MONGODB_DB = os.getenv('MONGODB_DB', 'healthdata')
MONGODB_COLLECTION = os.getenv('MONGODB_COLLECTION', 'va')

SS_ID = os.getenv('SSID', None)
SS_TOKEN = os.getenv('SS_TOKEN', None)
