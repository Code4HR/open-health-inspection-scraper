#!/usr/bin/env python3

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scraper.spiders.healthspace_spider import HealthSpaceSpider
from scraper.helpers.scoring import Scoring

settings = get_project_settings()

process = CrawlerProcess(settings)

process.crawl(HealthSpaceSpider)
process.start()

scoring = Scoring()
scoring.score_vendors()
