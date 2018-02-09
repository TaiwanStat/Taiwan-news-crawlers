"""
蘋果日報新聞
the crawl deal with apple's news
Usage: scrapy crawl apple -o <filename.json>
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import time

import w3lib.url

import scrapy


class AppleSpider(scrapy.Spider):
    name = "apple"
    start_urls = [
        'https://tw.appledaily.com/daily',
    ]

    def parse(self, response):
        section = response.css('section.nclnbx.slvl.clearmen, article.nclns')
        for part in section:
            if part.css('header.schh h1::text'):
                category = part.css('header.schh h1::text').extract_first()
                category = category.strip()
            else:
                meta = {'category': category}
                for news in part.css('ul.fillup li'):
                    if 'eat-travel' in news.css(
                            "a::attr(href)").extract_first():
                        continue
                    elif 'entertainment.appledaily' in news.css(
                            "a::attr(href)").extract_first():
                        url = news.css("a::attr(href)").extract_first()
                    elif 'http' in news.css("a::attr(href)").extract_first():
                        url = news.css("a::attr(href)").extract_first()
                    else:
                        url = "http://www.appledaily.com.tw{}".format(
                            news.css("a::attr(href)").extract_first())
                    if url:
                        url = response.urljoin(url)
                        yield scrapy.Request(
                            url, callback=self.parse_news, meta=meta)

    def parse_news(self, response):
        date = time.strftime('%Y-%m-%d')
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
            'date': date,
            'content': content,
            'category': response.meta['category']
        }
