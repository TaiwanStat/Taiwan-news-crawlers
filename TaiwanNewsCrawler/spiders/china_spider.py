"""
中國時報
the crawl deal with chinatimes's news
Usage: scrapy crawl china -o <filename.json>
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
import time
import scrapy

TODAY = time.strftime('%Y-%m-%d')
ROOT_URL = 'http://www.chinatimes.com'
PAGE_URL = 'http://www.chinatimes.com/newspapers/2601'


class ChinaSpider(scrapy.Spider):
    name = "china"
    start_urls = ['http://www.chinatimes.com/newspapers/2601']

    def parse(self, response):
        has_next_page = False
        news_in_page = response.css('ul.vertical-list li')
        if not news_in_page:
            return

        for news in news_in_page:
            url = news.css('a::attr(href)').extract_first()
            date_time_1 = news.css('time::attr(datetime)').extract_first()
            date_time_2 = news.css('time span.date::text').extract_first()
            if TODAY in date_time_1 or TODAY in date_time_2:
                has_next_page = True
                
                if ROOT_URL not in url:
                    url = ROOT_URL + url
                url = response.urljoin(url)
                yield scrapy.Request(url, callback=self.parse_news)
        if 'next_page' in response.meta:
            meta = {'next_page': response.meta['next_page'] + 1}
        else:
            meta = {'next_page': 2}
        if has_next_page:
            next_url = PAGE_URL + '?page=' + str(meta['next_page'])
            yield scrapy.Request(next_url, callback=self.parse, meta=meta)

    def parse_news(self, response):
        title = response.css('h1::text').extract_first()
        date_of_news_str = response.css('time::attr(datetime)').extract_first()
        date_of_news = datetime.strptime(date_of_news_str, '%Y-%m-%d %H:%M')
        content = ""
        for p in response.css('div.article-body p'):
            p_text = p.css('::text')
            if p_text:
                content += ''.join(p_text.extract())

        category = response.css('meta[name=section]::attr(content)').extract_first()

        yield {
            'website': "中國時報",
            'url': response.url,
            'title': title,
            'date': date_of_news,
            'content': content,
            'category': category
        }
