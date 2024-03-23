from scrapy.crawler import CrawlerRunner
from app.scrapy_app.scrapy_app.spiders.website_spider import WebsiteSpider
from app.celery_app.config import celery_app

@celery_app.task(name="run_scrapy_spider")
def run_scrapy_spider():
    process = CrawlerRunner()
    process.crawl(WebsiteSpider)
    process.start()


