"""
TVBS
the crawl deal with tvbs's news
Usage: scrapy crawl tvbs -o <filename.json>
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import date, timedelta
import scrapy

YESTERDAY = (date.today() - timedelta(1)).strftime('%Y/%m/%d')
YESTERDAY = YESTERDAY.replace('/','-')

class TvbsSpider(scrapy.Spider):
    name = "tvbs"
    start_urls = ['http://news.tvbs.com.tw/news/realtime/all/{}/1'.format(YESTERDAY)]

    def parse(self, response):
        for news in response.css('.realtime_news_content_titel'):
            category = news.css('p::text').extract_first()
            meta = {'category': category}
            url = news.css('div a::attr(href)').extract_first()
            url = response.urljoin(url)
            yield scrapy.Request(url, callback=self.parse_news)

        # Auto-parse next page
        total_pages = response.css('.realtime_news_underbtn li:last-child::text').extract_first()
        total_pages = int(total_pages[1:-1])  # 共xx頁
        url_arr = response.url.split('/')
        current_page = int(url_arr[-1])

        if current_page < total_pages:
            next_page = '/'.join(url_arr[:-1]) + '/' + str(current_page+1)
            yield scrapy.Request(next_page, callback=self.parse)

    def parse_news(self, response):
        title = response.css('.newsdetail-h2 p strong::text').extract_first()
        date_of_news = response.css('.newsdetail-time1 p::text').extract_first()
        content = response.css('.newsdetail-content').extract_first()
        content = content[content.index('>\n\t\t')+8:content.index('<strong>')-8]
        content = content.replace('<br>','')

        yield {
            'website': "TVBS",
            'url': response.url,
            'title': title,
            'date': date_of_news,
            'content': content,
            'category': response.meta['category']
        }