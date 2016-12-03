#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
聯合報
"""
import scrapy
from datetime import date, timedelta

YESTERDAY = (date.today() - timedelta(1)).strftime('%Y/%m/%d')


class UdnSpider(scrapy.Spider):
    name = "udn"
    start_urls = [
                   'http://udn.com/news/archive/0/0/{}/1'.format(YESTERDAY)
                 ]

    def parse(self, response):
        for news in response.css('td a'):
            url = news.css('a::attr(href)').extract_first()
            yield scrapy.Request(url, callback=self.parse_news)

        # Auto-parse next page
        total_pages = response.css(".pagelink .total::text").extract_first()
        total_pages = int(total_pages[2:-2])  # 共 x 頁
        url_arr = response.url.split('/')
        current_page = int(url_arr[-1])

        if current_page < total_pages:
            next_page = '/'.join(url_arr[:-1]) + '/' + str(current_page+1)
            yield scrapy.Request(next_page, callback=self.parse)

    def parse_news(self, response):
        title = response.css('h1::text').extract_first()
        date = response.css('.story_bady_info_author::text').extract_first()

        content = ""
        for p in response.css('p'):
            p_text = p.css('::text')
            if p_text:
                content += ' '.join(p_text.extract())

        category_links = response.css('div div div.only_web a')
        category = category_links[1].css('::text').extract_first()

        yield {
            'website': "聯合報",
            'url': response.url,
            'title': title,
            'date': date,
            'content': content,
            'category': category
        }
