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


class TvbsSpider(scrapy.Spider):
    name = "tvbs"
    #start_urls = ['http://news.tvbs.com.tw/news/realtime/all']
    start_urls = ['http://news.tvbs.com.tw/news/realtime/all/2017-11-25']
    #start_urls = ['http://udn.com/news/archive/0/0/{}/1'.format(YESTERDAY)]

    def parse(self, response):
        for news in response.css('.realtime_news_content_titel'):
            category = news.css('p::text').extract_first()
            title = news.css('div a p::text').extract_first()
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
        #title = response.css('h1::text').extract_first()
        date_of_news = response.css('.newsdetail-time1 p::text').extract_first()
        content = response.css('.newsdetail-content').extract_first()
        # for p in response.css('p'):
        #     p_text = p.css('::text')
        #     if p_text:
        #         content += ' '.join(p_text.extract())

        # category_links = response.css('div div div.only_web a')
        # category = category_links[1].css('::text').extract_first()

        yield {
            'website': "TVBS",
            'url': response.url,
            'title': title,
            'date': date_of_news,
            'content': content,
            'category': category
        }