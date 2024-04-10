import logging
from app.celery_app import celery_app
from app.scrapy_app.scrapy_app.spiders.website_spider import WebsiteSpider
from celery.utils.log import get_task_logger
from scrapy.crawler import CrawlerProcess

logger = get_task_logger("uni_website_task")
logger.setLevel(logging.INFO)

@celery_app.task(name="uni-website")
def run_scrapy_spider():
    logger.info("Running scraping task...")
    process = CrawlerProcess()
    process.crawl(WebsiteSpider)
    process.start()
