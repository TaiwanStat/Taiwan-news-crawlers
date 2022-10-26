"""
自由時報
the crawl deal with liberty's news
Usage: scrapy crawl liberty -o <filename.json>
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
import scrapy.http
from urllib.parse import urljoin
import json
import TaiwanNewsCrawler.utils as utils

ROOT_URL = 'http://news.ltn.com.tw/'
PAGE_URL = 'http://news.ltn.com.tw/list/breakingnews/all/'
API_URL = "https://news.ltn.com.tw/ajax/breakingnews/all/{}"

class LibertySpider(scrapy.Spider):
    name = "liberty"

    def __init__(self, start_date: str=None, end_date: str=None):
        super().__init__(start_date=start_date, end_date=end_date)

    def start_requests(self):
        meta = {"iter_time": 1}
        url = API_URL.format(meta["iter_time"])
        yield scrapy.http.Request(url, method='GET', callback=self.parse_news_list, meta=meta)

    def parse_news_list(self, response: scrapy.Request):
        start_date, end_date = utils.parse_start_date_and_end_date(self.start_date, self.end_date)
        crawl_next = False
        response.meta['iter_time'] += 1

        response_data = json.loads(response.text)
        if (int(response_data["code"]) == 200):
            for news in response_data["data"]:
                if (type(news) == str):
                    news = response_data["data"][news]
                news_time = utils.parse_date(news["time"], "%H:%M")
                if (news_time is None):
                    news_date = utils.parse_date(news["time"], "%Y/%m/%d %H:%M")
                else:
                    news_date = utils.TODAY
                crawl_next = utils.can_crawl(news_date, start_date, end_date)

                if (crawl_next):
                    url = news["url"]
                    if (not ROOT_URL in url):
                        url = urljoin(ROOT_URL, url)
                    yield scrapy.Request(url, callback=self.parse_news)
        
        if (crawl_next):
            url = API_URL.format(response.meta["iter_time"])
            yield scrapy.http.Request(url, method='GET', callback=self.parse_news_list, meta=response.meta)


    def parse_news(self, response: scrapy.Selector):
        title = response.css('h1::text').extract_first()
        date_str = response.css('meta[property=pubdate]::attr(content)').extract_first()
        if (date_str is None):
            date_str = response.css('span.time::text').extract_first()
        date = utils.parse_date(date_str).replace(tzinfo=None)
        
        parse_text_list = ["div.text p",           # normal
                            "div.text p span",     # other
                            ]
                            
        for parse_text in parse_text_list:
            article = response.css(parse_text)
            if (not article is None):
                break

        content = ""
        for p in article:
            if (len(p.css("::attr(href)")) == 0 or len(p.css("::attr(class)")) == 0 or p.css("::attr(lang)") == "zh-TW"):
                p_text = p.css('::text')
                content += ' '.join(p_text.extract())

        category = response.css('div.breadcrumbs a::text').extract()[-1]

        # description
        try:
            description = response.css("meta[property='og:description']::attr(content)").extract_first()
        except:
            description = ""

        yield {
            'website': "自由時報",
            'url': response.url,
            'title': title,
            'date': date,
            'content': content,
            'category': category,
            "description": description
        }
