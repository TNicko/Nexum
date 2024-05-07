import scrapy
import time
from scrapy import signals
from bs4 import BeautifulSoup
from app.utils.time_utils import log_time
from scrapy.signalmanager import dispatcher
from app.utils.log_config import setup_colored_logger

logger = setup_colored_logger("spider")
logger.propagate = False

DOMAIN = "https://www.lboro.ac.uk"

class WebsiteSpider(scrapy.Spider):
    name = "websitespider"
    allowed_domains = ["lboro.ac.uk"]
    start_urls = [DOMAIN]

    def __init__(
        self,
        test_mode=False,
        test_url="https://www.lboro.ac.uk/study/undergraduate/courses/computer-science-bsc/",
        *args,
        **kwargs,
    ):
        self.visited_urls = set()
        self.test_mode = test_mode
        if self.test_mode and test_url:
            self.start_urls = [test_url]

        print(self.start_urls)
        dispatcher.connect(self.spider_opened, signal=signals.spider_opened)
        dispatcher.connect(self.spider_closed, signal=signals.spider_closed)

    def spider_opened(self, spider):
        self.start_time = time.time()
        logger.debug(f"{spider.name} started.")

    def spider_closed(self, spider, reason):
        total_time = time.time() - self.start_time
        logger.debug(
            f"{spider.name} closed. Reason: {reason}. Total time: {total_time:.5f} seconds."
        )

    def parse(self, response):
        logger.info(f"Scraping URL: {response.url}")
        parse_start_time = time.time()

        soup = BeautifulSoup(response.body, "lxml")
        urls = extract_urls_from_html(soup)
        text = extract_text(response)
        file_path = response.url.replace("https://www.lboro.ac.uk", "home")
        log_time("Parsing url", parse_start_time)
        yield {"url": response.url, "file_path": file_path, "content": text}

        # Only follow links if not in test mode
        if not self.test_mode:
            for url in urls:
                if url not in self.visited_urls:
                    self.visited_urls.add(url)
                    yield scrapy.Request(url, callback=self.parse)


def extract_urls_from_html(soup: BeautifulSoup):
    # Extracting URLs from <a> tags & categorizing
    a_tags = soup.find_all("a", href=True)
    urls = set()

    for a_tag in a_tags:
        url = a_tag["href"]

        # ignored urls
        if url.startswith("//"):
            continue

        if url.startswith("/"):
            url = f"{DOMAIN}{url}"
            urls.add(url)
        elif url.startswith(DOMAIN):
            urls.add(url)

    return urls


def extract_text(response):
    soup = BeautifulSoup(response.body, "lxml")
    text = soup.get_text(separator=" ", strip=True)
    return text
