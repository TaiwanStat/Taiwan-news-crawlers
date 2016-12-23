#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
蘋果日報
"""
import scrapy
import urllib.request
import re
import time
import w3lib.url


class AppleSpider(scrapy.Spider):
    name = "apple"
    start_urls = [
        'http://www.appledaily.com.tw/appledaily/todayapple',  # 蘋果每日新聞總覽
    ]

    def parse(self, response):
        headline_url = 'http://ent.appledaily.com.tw/section/article/headline/'

        section = response.css('section.nclnbx.slvl.clearmen, article.nclns')
        for part in section:
            if part.css('header.schh h1::text'):
                category = part.css('header.schh h1::text').extract_first()
                category = category.strip()
            else:
                meta = {'category': category}
                for news in part.css('ul.fillup li'):
                    if 'eat-travel' in news.css("a::attr(href)").extract_first():
                        continue
                    elif 'ent.appledaily' in news.css("a::attr(href)").extract_first():
                        # Get redirected url
                        url = news.css("a::attr(href)").extract_first()
                        url = w3lib.url.canonicalize_url(url)
                        url = urllib.request.urlopen(url, None, 1).geturl()
                        postfix = re.search('entertainment\/(\d*\/\d*\/)',
                                            url).group(1)
                        url = headline_url + postfix
                    else:
                        url = "http://www.appledaily.com.tw{}".format(
                                    news.css("a::attr(href)").extract_first())
                    if url:
                        url = response.urljoin(url)
                        yield scrapy.Request(url, callback=self.parse_news, meta=meta)

    def parse_news(self, response):
        date = time.strftime('%Y-%m-%d')
        category = response.css('meta[name=\"keywords\"]::attr(content)')\
                           .extract_first()
        title = ""
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
