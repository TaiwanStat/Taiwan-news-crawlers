#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
聯合報
the crawl deal with udn's news
Usage: scrapy crawl udn -o <filename.json>
"""
import json
from urllib.parse import urljoin

import scrapy
import scrapy.http

import TaiwanNewsCrawler.utils as utils

ROOT_URL = "https://udn.com"
API_URL = "https://udn.com/api/more?page={}&channelId={}&type={}&cate_id={}&totalRecNo=20490"


class UdnSpider(scrapy.Spider):
    name = "udn"

    def __init__(self, start_date: str = None, end_date: str = None):
        super().__init__(start_date=start_date, end_date=end_date)

    def start_requests(self):
        """crawl news with api

        meta-example:
            # 這邊只有看'即時'這大分類的, 大分類指的是UDN最上面那排的. 然後切換底下小分類, 底下'XX-XX'指的就是'大分類-小分類'
            # 因為其他大分類又有不同的API下法, 差異很大
            prototype: https://udn.com/news/{type}/{channelId}/{cate_id}
            即時-精選: https://udn.com/news/breaknews/1/0#breaknews
                type: breaknews
                channelId: 1
                cate_id: 0
            即時-不分類: https://udn.com/news/breaknews/1/99#breaknews
                type: breaknews
                channelId: 1
                cate_id: 99
            即時-要聞: https://udn.com/news/breaknews/1/1#breaknews
                type: breaknews
                channelId: 1
                cate_id: 1

        Yields:
            _type_: _description_
        """
        meta = {"iter_time": 1, "channel_id": 1, "type_str": "breaknews", "cate_id": 0}
        page = meta["iter_time"]
        channel_id = meta["channel_id"]
        type_str = meta["type_str"]
        cate_id = meta["cate_id"]

        url = API_URL.format(page, channel_id, type_str, cate_id)
        yield scrapy.http.Request(url, method="GET", callback=self.parse_news_list, meta=meta)

    def parse_news_list(self, response: scrapy.Request):
        start_date, end_date = utils.parse_start_date_and_end_date(self.start_date, self.end_date)
        crawl_next = False
        response.meta["iter_time"] += 1

        response_data = json.loads(response.text)
        if response_data["state"] is True:
            for news in response_data["lists"]:
                if type(news) == str:
                    news = response_data["data"][news]
                news_date = utils.parse_date(news["time"]["date"])
                crawl_next = utils.can_crawl(news_date, start_date, end_date)

                if crawl_next:
                    url = news["titleLink"]
                    if ROOT_URL not in url:
                        url = urljoin(ROOT_URL, url)
                    yield scrapy.Request(url, callback=self.parse_news)

        if crawl_next:
            page = response.meta["iter_time"]
            channel_id = response.meta["channel_id"]
            type_str = response.meta["type_str"]
            cate_id = response.meta["cate_id"]
            url = API_URL.format(page, channel_id, type_str, cate_id)
            yield scrapy.http.Request(url, method="GET", callback=self.parse_news_list, meta=response.meta)

    def parse_news(self, response: scrapy.Selector):
        # 處理頁面轉跳的問題
        all_script_text = response.css("script[language=javascript]::text").extract()
        for script_text in all_script_text:
            if "window.location" in script_text:
                url = script_text.split('"')[-2]
                yield scrapy.Request(url, callback=self.parse_news)
                return

        title = response.css("h1::text").extract()[-1]
        date_str = response.css("meta[name=date]::attr(content)").extract_first()
        if date_str is None:
            date_str = response.css("time.article-content__time::text").extract_first()
        date = utils.parse_date(date_str).replace(tzinfo=None)

        parse_text_list = [
            "section.article-content__editor p",
        ]

        for parse_text in parse_text_list:
            article = response.css(parse_text)
            if article is not None:
                break

        content = ""
        for p in article:
            p_text = p.css("::text")
            content += " ".join(p_text.extract())

        category = response.css("section.article-content__cate a::text").extract_first()  # 聯合報頁面用
        if category is None:
            category = "/".join(response.css("a.breadcrumb-items::text").extract()[1:])  # 聯合新聞網頁面用

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
            "website": "聯合報",
            "url": response.url,
            "title": title,
            "date": date,
            "content": content,
            "category": category,
            "description": description,
            "key_word": key_word,
        }
