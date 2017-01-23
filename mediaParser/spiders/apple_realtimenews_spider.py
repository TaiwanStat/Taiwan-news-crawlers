#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
蘋果日報即時新聞
"""
import scrapy
import re
import time
from datetime import datetime, date, time

today = date.today()
ROOT_URL = 'http://www.appledaily.com.tw/realtimenews/section/new/'

class AppleRealtimenewsSpider(scrapy.Spider):
    name = 'appleRealtime'
    start_urls = [
        ROOT_URL + '1'
    ]

    def parse(self, response):
        regex = 'section\/new\/(\d+)'
        current_index = re.search(regex, response.url).group(1)
        next_index = int(current_index)+1
        current_date = response.css('h1 time::text').extract_first()
        current_date = datetime.strptime(current_date, "%Y / %m / %d")
        if today != current_date.date():
            return
        for news_item in response.css('ul.rtddd li'):
            category = news_item.css('h2::text').extract_first()
            meta = {'category': category}
            relative_url = news_item.css('a::attr(href)').extract_first()
            abs_url = response.urljoin(relative_url)
            yield scrapy.Request(abs_url, callback=self.parse_news, meta=meta)

        next_targe = ROOT_URL+str(next_index)
        yield scrapy.Request(next_targe, callback=self.parse)

    def parse_news(self, response):
        title = ""
        date = today.strftime('%Y-%m-%d')
        news_date = response.css('article div time::attr(datetime)').extract_first()
        news_date = datetime.strptime(news_date, "%Y/%m/%d/")
        if today != news_date.date():
            return
        t_h1 = response.css('hgroup h1::text')
        if t_h1:
            title += t_h1.extract_first()
        t_h2 = response.css('hgroup h2::text')
        if t_h2:
            title += t_h2.extract_first()

        h2 = response.css("div.articulum h2::text").extract()
        h2_num = len(h2)
        content = ""
        counter = 0
        category = response.meta['category']
        if category == '動物':
            for p in response.css(".trans::text").extract():
                content += ' '+p
        else:
            for p in response.css("div.articulum p"):
                if p.css("p::text"):
                    content += ' '.join(p.css("p::text").extract())
                if counter < h2_num:
                    content += " " + h2[counter]
                    counter += 1
        yield {
            'website': "蘋果日報",
            'url': response.url,
            'title': title,
            'date': date,
            'content': content,
            'category': response.meta['category']
        }
