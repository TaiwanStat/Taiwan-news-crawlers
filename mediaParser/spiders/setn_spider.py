"""
三立新聞
the crawl deal with setn's news
Usage: scrapy crawl setn -o <filename.json>
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from datetime import date, timedelta
import scrapy

YESTERDAY = (date.today() - timedelta(1)).strftime('%m/%d/%Y')

class SetnSpider(scrapy.Spider):
    name = "setn"
    start_urls = ['http://www.setn.com/ViewAll.aspx?date={}&p=1'.format(YESTERDAY)]

    def parse(self, response):
        for news in response.css('.box ul li'):
            category = news.css('.tab_list_type span::text').extract_first()
            meta = {'category': category}
            url = news.css('a::attr(href)').extract_first()
            url = response.urljoin(url)
            yield scrapy.Request(url, callback=self.parse_news, meta=meta)

        # Auto-parse next page
        # total_pages = response.css('.realtime_news_underbtn li:last-child::text').extract_first()
        # total_pages_num = int(total_pages[1:-1])
        # url_arr = response.url.split('/')
        # current_page_index = int(url_arr[-1])

        # if current_page_index < total_pages_num:
        #     next_page_url = '/'.join(url_arr[:-1]) + \
        #         '/' + str(current_page_index + 1)
        #     yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_news(self, response):
        title = response.css('.title h1::text').extract_first()
        date_of_news = response.css('.date::text').extract_first()[:10]
        content = response.css('#Content1 p::text').extract()
        content = ''.join(content)

        yield {
            'website': "三立新聞",
            'url': response.url,
            'title': title,
            'date': date_of_news,
            'content': content,
            'category': response.meta['category']
        }
