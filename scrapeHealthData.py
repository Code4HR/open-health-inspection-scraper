#!/usr/bin/env python3

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scraper.spiders.healthspace_spider import HealthSpaceSpider
import os

try:
	os.remove('result.json')
except Exception:
	pass

settings = get_project_settings()
settings.set('FEED_FORMAT', 'json')
settings.set('FEED_URI', 'result.json')

process = CrawlerProcess(settings)

process.crawl(HealthSpaceSpider)
process.start()
