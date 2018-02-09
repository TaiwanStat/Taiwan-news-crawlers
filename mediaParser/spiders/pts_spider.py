"""
the crawl deal with pts's news
Usage: scrapy crawl pts -o <filename.json>
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import time

import scrapy

TODAY = time.strftime('%Y-%m-%d')
ROOT_URL = 'https://news.pts.org.tw/list/'
ARTICLE_PREFIX = 'http://news.pts.org.tw/article/'


class EttodaySpider(scrapy.Spider):
    name = "pts"

    def start_requests(self):
        url = 'https://news.pts.org.tw/list/0'
        meta = {'iter_time': 0}
        yield scrapy.Request(url, callback=self.parse_news_list, meta=meta)

    def parse_news_list(self, response):
        response.meta['iter_time'] = 1
        for news_item in response.css('ul.list-news li'):
            url = news_item.css('h2 a::attr(href)').extract_first()
            date_time = news_item.css('.list-news-time::text').extract_first()
            title = news_item.css('h2 a::text').extract_first()
            content = news_item.css(
                '.list-news-description::text').extract_first()
            category = news_item.css(
                '.list-news-program::text').extract_first()

            if TODAY in date_time:
                yield {
                    'website': '公視',
                    'url': url,
                    'title': title,
                    'date': date_time,
                    'content': content,
                    'category': category
                }

        yield scrapy.FormRequest(
            url='https://news.pts.org.tw/list/getmore.php',
            callback=self.get_news,
            meta=response.meta,
            formdata={
                'page': '1'
            })

    def get_news(self, response):
        response.meta['iter_time'] += 1
        news_items = json.loads(response.text)

        if news_items:
            for n in news_items:
                yield {
                    'website': '公視',
                    'url': ARTICLE_PREFIX + n['news_id'],
                    'title': n['subject'],
                    'date': n['news_date'],
                    'content': n['content'],
                    'category': n['program_name']
                }
            yield scrapy.FormRequest(
                url="https://news.pts.org.tw/list/getmore.php",
                callback=self.get_news,
                meta=response.meta,
                formdata={
                    'page': str(response.meta['iter_time'])
                })
