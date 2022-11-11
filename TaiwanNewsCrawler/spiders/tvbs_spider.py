#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TVBS
the crawl deal with tvbs's news
Usage: scrapy crawl tvbs -o <filename.json>
"""
import datetime as dt
from urllib.parse import urljoin

import scrapy

import TaiwanNewsCrawler.utils as utils

ROOT_URL = "https://news.tvbs.com.tw"
PAGE_URL = "https://news.tvbs.com.tw/realtime/news/{}"


class TvbsSpider(scrapy.Spider):
    name = "tvbs"

    def __init__(self, start_date: str = None, end_date: str = None):
        super().__init__(start_date=start_date, end_date=end_date)

    def start_requests(self):
        start_date, end_date = utils.parse_start_date_and_end_date(self.start_date, self.end_date)
        date = start_date

        while date < end_date:
            url = PAGE_URL.format(date.strftime("%Y-%m-%d"))
            yield scrapy.Request(url, method="GET", callback=self.parse)
            date += dt.timedelta(days=1)

    def parse(self, response):
        parse_text_list = ["main article div.list li"]
        for parse_text in parse_text_list:
            for news in response.css(parse_text):
                url = news.css("a::attr(href)").extract_first()
                if url is None:
                    continue
                if ROOT_URL not in url:
                    url = urljoin(ROOT_URL, url)
                yield scrapy.Request(url, callback=self.parse_news)

    def parse_news(self, response: scrapy.Selector):
        title = response.css("h1::text").extract_first()
        date_str = response.css("meta[name=pubdate]::attr(content)").extract_first()
        if date_str is None:
            date_str = response.css("meta[property='article:published_time']::attr(content)").extract_first()
        date = utils.parse_date(date_str).replace(tzinfo=None)

        parse_text_list = [
            "div[itemprop=articleBody] div.article_content",
        ]

        for parse_text in parse_text_list:
            article = response.css(parse_text)
            if article is not None:
                break

        content = ""
        for p in article.css("::text").extract():
            if len(p) > 0 and p[0] != "\n":
                content += p

        category = response.css("meta[name=section]::attr(content)").extract_first()
        if category is None:
            category = response.css("meta[property='article:section']::attr(content)").extract_first()

        # description
        try:
            description = response.css("meta[property='og:description']::attr(content)").extract_first()
        except Exception as e:
            description = ""

        # key_word
        try:
            key_word = response.css("meta[name=news_keywords]::attr(content)").extract_first()
        except Exception as e:
            key_word = ""

        yield {
            "website": "TVBS",
            "url": response.url,
            "title": title,
            "date": date,
            "content": content,
            "category": category,
            "description": description,
            "key_word": key_word,
        }
