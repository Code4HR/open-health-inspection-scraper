
SPIDER_MODULES = ['scraper.spiders']
NEWSPIDER_MODULE = 'tutorial.spiders'

ITEM_PIPELINES = {'scraper.pipelines.MongoPipeline': 300}

MONGODB_SERVER = "localhost"
MONGODB_PORT = 27017
MONGODB_DB = "ohi_test"
MONGODB_COLLECTION = "health"

DEPTH_LIMIT = 0