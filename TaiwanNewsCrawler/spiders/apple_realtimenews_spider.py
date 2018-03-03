"""
蘋果日報即時新聞
the crawl deal with apple's realtime news
Usage: scrapy crawl appleRealtime -o <filename.json>
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from datetime import datetime
from datetime import date

import scrapy

TODAY = date.today()
ROOT_URL = 'https://tw.appledaily.com/new/realtime/'


class AppleRealtimenewsSpider(scrapy.Spider):
    name = 'appleRealtime'
    start_urls = [ROOT_URL + '1']

    def parse(self, response):
        regex = r'realtime\/(\d+)'
        current_index = re.search(regex, response.url).group(1)
        next_index = int(current_index) + 1
        current_date = response.css('h1 time::text').extract_first()
        current_date = datetime.strptime(current_date, "%Y / %m / %d")
        if TODAY != current_date.date():
            return
        for news_item in response.css('ul.rtddd li'):
            category = news_item.css('h2::text').extract_first()
            meta = {'category': category}
            relative_url = news_item.css('a::attr(href)').extract_first()
            abs_url = response.urljoin(relative_url)
            yield scrapy.Request(abs_url, callback=self.parse_news, meta=meta)

        next_targe = ROOT_URL + str(next_index)
        yield scrapy.Request(next_targe, callback=self.parse)

    def parse_news(self, response):
        news_date = response.css('.ndArticle_creat::text').extract_first()[5:
                                                                           -6]
        news_date = datetime.strptime(news_date, "%Y/%m/%d")
        if TODAY != news_date.date():
            return
        title = ""
        title_sel_prefix = 'hgroup'
        p_sel_prefix = '.ndArticle_margin'

        if 'home' in response.url:
            title_sel_prefix = '.ncbox_cont'
            p_sel_prefix = '.articulum'

        t_h1 = response.css(title_sel_prefix + '>h1::text')
        if t_h1:
            title += t_h1.extract_first()
        t_h2 = response.css(title_sel_prefix + '>h2::text')
        if t_h2:
            title += t_h2.extract_first()

        h2 = response.css(title_sel_prefix + '>h2::text').extract()
        h2_num = len(h2)
        content = ""
        counter = 0
        for p in response.css(p_sel_prefix + '>p'):
            if p.css('p::text'):
                content += ' '.join(p.css('p::text').extract())
            if counter < h2_num:
                content += " " + h2[counter]
                counter += 1

        yield {
            'website': "蘋果日報",
            'url': response.url,
            'title': title,
            'date': news_date,
            'content': content,
            'category': response.meta['category']
        }
