import os

SPIDER_MODULES = ['scraper.spiders']

LOG_LEVEL = 'INFO'
JOBDIR = 'job'
DOWNLOAD_DELAY = 0.15
#AUTOTHROTTLE_ENABLED = True
#AUTOTHROTTLE_START_DELAY = 1.0
#AUTOTHROTTLE_MAX_DELAY = 10.0

ITEM_PIPELINES = {'scraper.pipelines.MongoDBPipeline': 300}

MONGODB_SERVER = os.getenv('MONGODB_SERVER', 'localhost')
MONGODB_PORT = os.getenv('MONGODB_PORT', 27017)
MONGODB_USER = os.getenv('MONGODB_USER', None)
MONGODB_PWD = os.getenv('MONGODB_PWD', None)
MONGODB_DB = os.getenv('MONGODB_DB', 'healthdata')
MONGODB_COLLECTION = os.getenv('MONGODB_COLLECTION', 'va')

SS_ID = os.getenv('SS_ID', None)
SS_TOKEN = os.getenv('SS_TOKEN', None)
