import os
import logging
from celery import Celery
from dotenv import load_dotenv
from scrapy.crawler import CrawlerProcess
from app.scrapy_app.scrapy_app.spiders.website_spider import WebsiteSpider
from celery.utils.log import get_task_logger
from celery.app.log import TaskFormatter
from celery.signals import after_setup_task_logger

load_dotenv()

REDIS_URL = os.getenv("CELERY_BROKER_REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(__name__, broker=REDIS_URL, backend=REDIS_URL)

@after_setup_task_logger.connect
def setup_task_logger(logger, *args, **kwargs):
    for handler in logger.handlers:
        handler.setFormatter(
            TaskFormatter("%(asctime)s - %(task_id)s - %(task_name)s - %(name)s - %(levelname)s - %(message)s"))


logger = get_task_logger("task")
logger.setLevel(logging.INFO)

@celery_app.task
def run_scrapy_spider():
    logger.info("Running scraping task...")
    process = CrawlerProcess()
    process.crawl(WebsiteSpider)
    process.start()
