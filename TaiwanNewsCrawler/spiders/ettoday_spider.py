#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
the crawl deal with ettoday's news
Usage: scrapy crawl ettoday -o <filename.json>
"""

import datetime as dt
from urllib.parse import urljoin

import scrapy
import scrapy.http

import TaiwanNewsCrawler.utils as utils

ROOT_URL = "https://www.ettoday.net"
PAGE_URL = "https://www.ettoday.net/news/news-list-{}-0.htm"
API_URL = "https://www.ettoday.net/show_roll.php"


class EttodaySpider(scrapy.Spider):
    name = "ettoday"

    def __init__(self, start_date: str = None, end_date: str = None):
        super().__init__(start_date=start_date, end_date=end_date)

    def start_requests(self):
        start_date, end_date = utils.parse_start_date_and_end_date(self.start_date, self.end_date)
        date = start_date

        while date < end_date:
            meta = {"iter_time": 0, "date": date, "start_date": date, "end_date": date + dt.timedelta(days=1)}
            url = PAGE_URL.format(date.strftime("%Y-%m-%d"))
            yield scrapy.Request(url, callback=self.parse_news_list, meta=meta)
            date += dt.timedelta(days=1)

    def parse_news_list(self, response):
        start_date, end_date = response.meta["start_date"], response.meta["end_date"]
        crawl_next = False
        response.meta["iter_time"] += 1
        is_first_iter = response.meta["iter_time"] == 1
        prefix = ".part_list_2" if is_first_iter else ""
        date_str = response.meta["date"].strftime("%Y/%m/%d")

        for news in response.css(prefix + " h3"):
            news_date = utils.parse_date(news.css("span::text").extract_first())
            crawl_next = utils.can_crawl(news_date, start_date, end_date)

            url = news.css("a::attr(href)").extract_first()
            if ROOT_URL not in url:
                url = urljoin(ROOT_URL, url)
            category = news.css("em::text").extract_first()

            if crawl_next:
                response.meta["category"] = category
                yield scrapy.Request(url, callback=self.parse_news, meta=response.meta)

        if crawl_next:
            date_str = response.meta["date"].strftime("%Y%m%d")
            tFile = f"{date_str}-1.xml"
            yield scrapy.FormRequest(
                url=API_URL,
                callback=self.parse_news_list,
                meta=response.meta,
                formdata={
                    "offset": str(response.meta["iter_time"]),
                    "tPage": "3",
                    "tFile": tFile,
                    "tOt": "0",
                    "tSi": "100",
                    "tAr": "0",
                },
            )

    def parse_news(self, response):
        title = response.css("h1.title::text").extract_first()
        date = response.meta["date"].strftime("%Y-%m-%d")
        if not title:
            title = response.css("h2.title::text").extract_first()
            if not title:
                title = response.css("h1.title_article::text").extract_first()

        p_list = response.css(".story p::text").extract()

        content = ""
        for p in p_list:
            content += p

        category = response.meta["category"]

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
            "website": "東森新聞雲",
            "url": response.url,
            "title": title,
            "date": date,
            "content": content,
            "category": category,
            "description": description,
            "key_word": key_word,
        }
