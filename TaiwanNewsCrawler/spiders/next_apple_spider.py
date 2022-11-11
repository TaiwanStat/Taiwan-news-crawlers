#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
# 蘋果日報新聞
the crawl deal with apple's news
apple's news will not update since 2022/09/01
Usage: scrapy crawl apple -o <filename.json>
"""

import datetime as dt
import json
from urllib.parse import urljoin

import scrapy
import scrapy.http

import TaiwanNewsCrawler.utils as utils

ROOT_URL = "https://tw.nextapple.com"
PAGE_URL = "https://tw.nextapple.com/realtime/recommend/{}"


class NextAppleSpider(scrapy.Spider):
    name = "nextapple"

    def __init__(self, start_date: str = None, end_date: str = None):
        super().__init__(start_date=start_date, end_date=end_date)

    def start_requests(self):
        meta = {"iter_time": 1}
        url = PAGE_URL.format(meta["iter_time"])
        yield scrapy.Request(url, callback=self.parse, meta=meta)

    def parse(self, response: scrapy.Selector):
        start_date, end_date = utils.parse_start_date_and_end_date(self.start_date, self.end_date)
        crawl_next = False
        response.meta["iter_time"] += 1

        parse_text_list = ["div.post-hot article"]
        for parse_text in parse_text_list:
            for news in response.css(parse_text):
                news_date = utils.parse_date(news.css("div.post-inner div.post-meta time::text").extract_first())
                crawl_next = utils.can_crawl(news_date, start_date, end_date)

                if crawl_next:
                    url = news.css("a::attr(href)").extract_first()
                    if ROOT_URL not in url:
                        url = urljoin(ROOT_URL, url)
                    yield scrapy.Request(url, callback=self.parse_news)

        if crawl_next:
            url = PAGE_URL.format(response.meta["iter_time"])
            yield scrapy.Request(url, callback=self.parse, meta=response.meta)

    def parse_news(self, response: scrapy.Selector):
        title = response.css("h1::text").extract_first()
        date_str = response.css("meta[property=pubdate]::attr(content)").extract_first()
        if date_str is None:
            date_str = response.css("time::text").extract_first()
        date = utils.parse_date(date_str).replace(tzinfo=None)

        parse_text_list = [
            "div#main-content div.post-content p",
        ]

        for parse_text in parse_text_list:
            article = response.css(parse_text)
            if article is not None:
                break

        content = ""
        for p in article:
            if (len(p.css("::attr(href)")) == 0 and len(p.css("::attr(class)")) == 0) or p.css("::attr(lang)") == "zh-TW":  # fmt: skip
                p_text = p.css("::text")
                content += " ".join(p_text.extract())

        category = response.css("div.category::text").extract_first()

        # description
        try:
            description = response.css("meta[property='og:description']::attr(content)").extract_first()
        except Exception as e:
            description = ""

        # key_word
        try:
            key_word = response.css("meta[name=keywords]::attr(content)").extract_first()
        except Exception as e:
            key_word = ""

        yield {
            "website": "壹蘋新聞網",
            "url": response.url,
            "title": title,
            "date": date,
            "content": content,
            "category": category,
            "description": description,
            "key_word": key_word,
        }
