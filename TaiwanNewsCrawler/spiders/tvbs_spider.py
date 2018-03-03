"""
TVBS
the crawl deal with tvbs's news
Usage: scrapy crawl tvbs -o <filename.json>
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from datetime import date
from datetime import timedelta

import scrapy

YESTERDAY = (date.today() - timedelta(1)).strftime('%Y/%m/%d')
YESTERDAY = YESTERDAY.replace('/', '-')


class TvbsSpider(scrapy.Spider):
    name = "tvbs"
    start_urls = [
        'http://news.tvbs.com.tw/news/realtime/all/{}/1'.format(YESTERDAY)
    ]

    def parse(self, response):
        for news in response.css('.realtime_news_content_titel'):
            category = news.css('p::text').extract_first()
            meta = {'category': category}
            url = news.css('div a::attr(href)').extract_first()
            url = response.urljoin(url)
            yield scrapy.Request(url, callback=self.parse_news, meta=meta)

        total_pages = response.css(
            '.realtime_news_underbtn li:last-child::text').extract_first()
        total_pages_num = int(total_pages[1:-1])
        url_arr = response.url.split('/')
        current_page_index = int(url_arr[-1])

        if current_page_index < total_pages_num:
            next_page_url = '/'.join(url_arr[:-1]) + \
                '/' + str(current_page_index + 1)
            yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_news(self, response):
        title = response.css('.newsdetail-h2 p strong::text').extract_first()
        date_of_news = response.css(
            '.newsdetail-time1 p::text').extract_first()[:10]
        raw_content = response.css('.newsdetail-content').extract_first()

        TAG_RE = re.compile(r'<[^>]+>([^<]*</[^>]+>)?')

        content_prefix = '<!-- 新聞主內容 -->'
        content_suffix1 = '<strong>'
        content_suffix2 = '<!--'

        content = raw_content.split(content_prefix)[1]

        if content_suffix1 in content:
            content = content.split(content_suffix1)[0]
        elif content_suffix2 in content:
            content = content.split(content_suffix2)[0]

        content = content.replace('<br>', ' ')
        content = content.replace('\n', ' ')
        content = content.replace('\t', ' ')
        content = TAG_RE.sub(' ', content)
        content = content.strip()

        yield {
            'website': "tvbs",
            'url': response.url,
            'title': title,
            'date': date_of_news,
            'content': content,
            'category': response.meta['category']
        }
