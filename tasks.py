from redis import Redis
from rq import Queue
from scrapy.crawler import CrawlerProcess
from email_spider import EmailSpider

# Initialize Redis connection and RQ queue
redis_conn = Redis()
q = Queue(connection=redis_conn)

def scrape_page(url, email, api_key, webhook_url):
    """
    Scrape a page using Scrapy.

    :param url: URL to scrape
    :param email: Email to search for
    :param api_key: API key
    :param webhook_url: Webhook URL for notifications
    """
    process = CrawlerProcess()
    process.crawl(EmailSpider, email=email, api_key=api_key, webhook_url=webhook_url, start_urls=[url])
    process.start()

def enqueue_scraping_task(url, email, api_key, webhook_url):
    """
    Enqueue a scraping task using RQ.

    :param url: URL to scrape
    :param email: Email to search for
    :param api_key: API key
    :param webhook_url: Webhook URL for notifications
    """
    q.enqueue(scrape_page, url, email, api_key, webhook_url)
