"""
三立新聞
the crawl deal with setn's news
Usage: scrapy crawl setn -o <filename.json> -s DOWNLOAD_DELAY=0.1
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
from urllib.parse import urljoin
import TaiwanNewsCrawler.utils as utils

ROOT_URL = "http://www.setn.com"
PAGE_URL = "http://www.setn.com/ViewAll.aspx?p={}"

class SetnSpider(scrapy.Spider):
    name = "setn"

    def __init__(self, start_date: str=None, end_date: str=None):
        super().__init__(start_date=start_date, end_date=end_date)

    def start_requests(self):
        meta = {"iter_time": 1}
        url = PAGE_URL.format(meta["iter_time"])
        yield scrapy.Request(url, callback=self.parse, meta=meta)

    def parse(self, response: scrapy.Selector):
        crawl_next = False
        response.meta['iter_time'] += 1

        parse_text_list = ["#NewsList div.newsItems"]
        for parse_text in parse_text_list:
            for news in response.css(parse_text):
                crawl_next = True

                url = news.css("h3 a::attr(href)").extract_first()
                if (not ROOT_URL in url):
                    url = urljoin(ROOT_URL, url)
                yield scrapy.Request(url, callback=self.parse_news)
        
        if (crawl_next):
            url = PAGE_URL.format(response.meta['iter_time'])
            yield scrapy.Request(url, callback=self.parse, meta=response.meta)


    def parse_news(self, response: scrapy.Selector):
        start_date, end_date = utils.parse_start_date_and_end_date(self.start_date, self.end_date)
        title = response.css('h1::text').extract_first()
        date_str = response.css('meta[name=pubdate]::attr(content)').extract_first()
        if (date_str is None):
            date_str = response.css('time::text').extract_first()
        if (date_str is None):
            date_str = response.css("meta[property='article:published_time']::attr(content)").extract_first()
        date = utils.parse_date(date_str).replace(tzinfo=None)

        crawl = utils.can_crawl(date, start_date, end_date)
        if (not crawl):
            return
        
        parse_text_list = ["article p",
                            ]
                            
        for parse_text in parse_text_list:
            article = response.css(parse_text)
            if (not article is None):
                break

        content = ""
        for p in article:
            if ((len(p.css("::attr(href)")) == 0 and len(p.css("::attr(class)")) == 0 and len(p.css("::attr(style)")) == 0) or p.css("::attr(lang)") == "zh-TW"):
                p_text = p.css('::text')
                content += ' '.join(p_text.extract())

        category = response.css("meta[name=section]::attr(content)").extract_first()
        if (category is None):
            category = response.css("meta[property='article:section']::attr(content)").extract_first()

        # description
        try:
            description = response.css("meta[property='og:description']::attr(content)").extract_first()
        except:
            description = ""

        yield {
            'website': "三立新聞",
            'url': response.url,
            'title': title,
            'date': date,
            'content': content,
            'category': category,
            "description": description
        }
