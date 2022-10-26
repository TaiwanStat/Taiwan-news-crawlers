"""
公視新聞
the crawl deal with pts's news
Usage: scrapy crawl pts -o <filename.json>
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
from urllib.parse import urljoin
import json
import TaiwanNewsCrawler.utils as utils

ROOT_URL = 'https://news.pts.org.tw/'
PAGE_URL = "https://news.pts.org.tw/dailynews?page={}"

class PtsSpider(scrapy.Spider):
    name = "pts"

    def __init__(self, start_date: str=None, end_date: str=None):
        super().__init__(start_date=start_date, end_date=end_date)

    def start_requests(self):
        meta = {"iter_time": 1}
        url = PAGE_URL.format(meta["iter_time"])
        yield scrapy.Request(url, callback=self.parse, meta=meta)

    def parse(self, response: scrapy.Selector):
        start_date, end_date = utils.parse_start_date_and_end_date(self.start_date, self.end_date)
        crawl_next = False
        response.meta['iter_time'] += 1

        parse_text_list = ["div.break-news-container div.breakingnews", "div.break-news-container ul.news-list li.d-flex"]
        for parse_text in parse_text_list:
            for news in response.css(parse_text):
                news_date = utils.parse_date(news.css("time::attr(datetime)").extract_first())
                crawl_next = utils.can_crawl(news_date, start_date, end_date)

                if (crawl_next):
                    url = news.css("h2 a::attr(href)").extract_first()
                    yield scrapy.Request(url, callback=self.parse_news)
        
        if (crawl_next):
            url = PAGE_URL.format(response.meta['iter_time'])
            yield scrapy.Request(url, callback=self.parse, meta=response.meta)


    def parse_news(self, response: scrapy.Selector):
        title = response.css('h1::text').extract_first()
        date_str = response.css('meta[property=pubdate]::attr(content)').extract_first()
        if (date_str is None):
            date_str = response.css('time::text').extract_first()
        date = utils.parse_date(date_str).replace(tzinfo=None)
        
        parse_text_list = ["article.post-article p",
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

        category = response.css('ol.breadcrumb li.breadcrumb-item')[-1].css("a::text").extract()[-1]

        # description
        try:
            description = response.css("meta[property='og:description']::attr(content)").extract_first()
        except:
            description = ""

        yield {
            'website': "公視",
            'url': response.url,
            'title': title,
            'date': date,
            'content': content,
            'category': category,
            "description": description
        }
