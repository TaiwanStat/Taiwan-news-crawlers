"""
中央社
the crawl deal with cna's news
Usage: scrapy crawl cna -o <filename.json>
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
import scrapy.http
from urllib.parse import urljoin
import TaiwanNewsCrawler.utils as utils


ROOT_URL = 'https://www.cna.com.tw'
API_URL = 'https://www.cna.com.tw/cna2018api/api/WNewsList'
API_POST_DATA = {"action": "0", "category": "aall", "pagesize": "20", "pageidx": 1}

class CnaSpider(scrapy.Spider):
    name = "cna"
    start_urls = ['https://www.cna.com.tw/list/aall.aspx']

    def __init__(self, start_date: str=None, end_date: str=None):
        super().__init__(start_date=start_date, end_date=end_date)

    def parse(self, response: scrapy.Selector):
        start_date, end_date = utils.parse_start_date_and_end_date(self.start_date, self.end_date)

        crawl_next = False
        all_news = response.css('ul#jsMainList li')
        if not all_news:
            return

        for news in all_news:
            news_date = utils.parse_date(news.css('div.date::text').extract_first())
            if (news_date is None):
                continue
            crawl_next = utils.can_crawl(news_date, start_date, end_date)

            if (crawl_next):
                url = news.css('a::attr(href)').extract_first()
                if (not ROOT_URL in url):
                    url = urljoin(ROOT_URL, url)
                yield scrapy.Request(url, callback=self.parse_news)

        if (crawl_next):
            API_POST_DATA["pageidx"] += 1
            # use api to get more news
            # yield scrapy.http.Request(API_URL, method='POST', body=json.dumps(API_POST_DATA), callback=self.parse_api, headers={'Content-Type':'application/json'})

    def parse_news(self, response: scrapy.Selector):
        title = response.css('h1 span::text').extract_first()
        date_str = response.css('div.updatetime span::text').extract_first()
        date = utils.parse_date(date_str, "%Y/%m/%d %H:%M")
        content = ''
        for p in response.css('div.centralContent div.paragraph p'):
            p_text = p.css('::text')
            if p_text:
                content += ' '.join(p_text.extract())

        category = response.css('article.article::attr(data-origin-type-name)').extract_first()

        # description
        try:
            description = response.css("meta[property='og:description']::attr(content)").extract_first()
        except:
            description = ""

        yield {
            'website': "中央通訊社",
            'url': response.url,
            'title': title,
            'date': date,
            'content': content,
            'category': category,
            'description': description
        }

    # TODO: can use api to get more news
    def parse_api(self, response):
        pass