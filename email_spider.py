import scrapy
from osint_tools import extract_entities, analyze_sentiment, generate_summary, send_webhook_notification
from elasticsearch import Elasticsearch

class EmailSpider(scrapy.Spider):
    name = 'email_spider'
    
    def __init__(self, email, api_key, webhook_url, *args, **kwargs):
        super(EmailSpider, self).__init__(*args, **kwargs)
        self.email = email
        self.api_key = api_key
        self.webhook_url = webhook_url
        self.es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        self.breaches = check_haveibeenpwned(email, api_key)

    def parse(self, response):
        page_content = response.body.decode('utf-8')
        if self.email in page_content:
            entities = extract_entities(page_content)
            sentiment = analyze_sentiment(page_content)
            summary = generate_summary(page_content)
            
            doc = {
                'page_url': response.url,
                'email': self.email,
                'entities': entities,
                'sentiment': sentiment,
                'summary': summary
            }
            self.es.index(index='email_occurrences', doc_type='_doc', body=doc)

            message = f"Email {self.email} found on {response.url} with entities: {entities}"
            send_webhook_notification(self.webhook_url, message)

        for next_page in response.css('a::attr(href)').getall():
            if next_page is not None:
                yield response.follow(next_page, self.parse)           
