"""
華視
the crawl deal with cts's news
Usage: scrapy crawl cts -o <filename.json>
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
import scrapy.http
import datetime as dt
import json
import TaiwanNewsCrawler.utils as utils

ROOT_URL = "https://news.cts.com.tw"
API_URL = "https://news.cts.com.tw/api/news/{}/daylist-news.json"

class CtsSpider(scrapy.Spider):
    name = "cts"

    def __init__(self, start_date: str=None, end_date: str=None):
        super().__init__(start_date=start_date, end_date=end_date)

    def start_requests(self):
        start_date, end_date = utils.parse_start_date_and_end_date(self.start_date, self.end_date, utils.YESTERDAY, utils.YESTERDAY)
        date = start_date

        while (date < end_date):
            url = API_URL.format(date.strftime("%Y/%m/%d"))
            yield scrapy.http.Request(url, method='GET', callback=self.parse)
            date += dt.timedelta(days=1)

    def parse(self, response: scrapy.Request):
        response = json.loads(response.text)
        for news in response:
            url = news["news_url"]
            if (not ROOT_URL in url):
                url = ROOT_URL + url
            yield scrapy.Request(url, callback=self.parse_news)

    def parse_news(self, response: scrapy.Selector):
        title = response.css('div.artical-titlebar h1.artical-title::text').extract_first()
        date_str = response.css('div.news-artical div.titlebar-top time.artical-time::text').extract_first()
        date = utils.parse_date(date_str, "%Y/%m/%d %H:%M")
        content = ""
        for p in response.css('artical.news-artical div.artical-content p'):
            if (len(p.css("::attr(href)")) == 0 or len(p.css("::attr(class)"))):
                p_text = p.css('::text')
                content += ' '.join(p_text.extract())

        category = response.css('meta[name=section]::attr(content)').extract_first()

        # description
        try:
            description = response.css('meta[name=description]::attr(content)').extract_first()
        except:
            description = ""

        yield {
            'website': "華視",
            'url': response.url,
            'title': title,
            'date': date,
            'content': content,
            'category': category,
            "description": description
        }

    