#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
東森時報
"""
import scrapy
from scrapy.selector import Selector
import time
import re

TODAY = time.strftime('%m/%d')


class EttodaySpider(scrapy.Spider):
    name = "ettoday"

    def start_requests(self):
        urls = [
            'http://www.ettoday.net/news/news-list.htm'
        ]

        for url in urls:
            yield scrapy.Request(url, callback=self.parse_news_list)

    def parse_news_list(self, response):
        for news_item in response.css('#all-news-list h3'):
            url = news_item.css('a::attr(href)').extract_first()
            category = news_item.css('em::text').extract_first()
            date_time = news_item.css('span::text').extract_first()

            if TODAY not in date_time:
                continue

            meta = {'category': category}
            yield scrapy.Request(url, callback=self.parse_news, meta=meta)

        page_list = []
        for p in response.css('.menu_page a').extract():
            sel = Selector(text=p)
            try:
                page_list.append({
                    'num': int(sel.xpath('//text()').extract_first()),
                    'link': sel.xpath('//@href').extract_first()
                })
            except:
                pass

        current_page = int(response.css('.menu_page .current::text')
                                   .extract_first())

        max_page_num = page_list[-1]['num']
        if not page_list or current_page >= max_page_num:
            return

        next_page = current_page + 1

        for page in page_list:
            if page['num'] > current_page:
                url = response.urljoin(page['link'])
                yield scrapy.Request(url, callback=self.parse_news_list)
                break

    def parse_news(self, response):
        title = response.css('h1.title::text').extract_first()
        if not title:
            title = response.css('h2.title::text').extract_first()
            if not title:
                title = response.css('h1::text').extract_first()

        p_list = response.css('.story p::text').extract()

        content = ''
        for p in p_list:
            content += p

        yield {
            'website': "東森新聞雲",
            'url': response.url,
            'title': title,
            'date': time.strftime('%Y-%m-%d'),
            'content': content,
            'category': response.meta['category']
        }
