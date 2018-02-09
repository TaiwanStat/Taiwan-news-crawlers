"""
華視
the crawl deal with cts's news
Usage: scrapy crawl cts -o <filename.json>
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import date
from datetime import timedelta
import scrapy

YESTERDAY = (date.today() - timedelta(1)).strftime('%Y/%m/%d')


class CtsSpider(scrapy.Spider):
    name = "cts"
    start_urls = [
        'http://news.cts.com.tw/daylist/{}/index.html'.format(YESTERDAY)
    ]

    def parse(self, response):
        for news in response.css('.news_right'):
            url = news.css('a::attr(href)').extract_first()
            yield scrapy.Request(url, callback=self.parse_news)

        page_desc = response.css('.page-desc::text').extract_first()
        total_pages = page_desc.split('/')[1]
        total_pages = int(total_pages[2:-2])
        url_arr = response.url.split('/')
        url_suffix = url_arr[-1]
        current_page_index = url_suffix[5:-5]
        if current_page_index is '':
            current_page_index = 1
        else:
            current_page_index = int(current_page_index)

        if current_page_index < total_pages:
            next_page = '/'.join(url_arr[:-1]) + '/index' + str(
                current_page_index + 1) + '.html'
            yield scrapy.Request(next_page, callback=self.parse)

    def parse_news(self, response):
        title = response.css('.newsbigtitle::text').extract_first().strip(
            ' \t\n\r')
        date_of_news = response.css('.timebar::text').extract_first().strip(
            ' \t\n\r')
        date_of_news = date_of_news[:10]
        category = response.css('.active a::text').extract()[-1]
        content = response.css('.newscontents p::text').extract()
        content = ' '.join(content)

        yield {
            'website': "華視",
            'url': response.url,
            'title': title,
            'date': date_of_news,
            'content': content,
            'category': category
        }
