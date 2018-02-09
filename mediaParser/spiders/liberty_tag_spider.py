"""
自由時報tag
the crawl deal with tags of liberty's news, which could make the dictionary of jieba
Usage: scrapy crawl liberty_tag -o <filename.json>
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import datetime
import scrapy

ROOT_URL = 'http://news.ltn.com.tw'
OLDEST_DATA_YEAR = 2015
NEWS_DATE_BEGIN = datetime.date(OLDEST_DATA_YEAR, 1, 1)
TODAY = datetime.date.today()
CATEGORY_DIC = {
    'focus': '焦點',
    'politics': '政治',
    'society': '社會',
    'local': '地方',
    'life': '生活',
    'opinion': '言論',
    'world': '國際',
    'business': '財經',
    'entertainment': '娛樂',
    'consumer': '消費',
    'supplement': '副刊',
    'sports': '體育'
}


class LibertySpider(scrapy.Spider):
    name = "liberty_tag"

    def start_requests(self):
        urls = [
            'http://news.ltn.com.tw/list/newspaper/focus/',
            'http://news.ltn.com.tw/list/newspaper/politics/',
            'http://news.ltn.com.tw/list/newspaper/society/',
            'http://news.ltn.com.tw/list/newspaper/local/',
            'http://news.ltn.com.tw/list/newspaper/life/',
            'http://news.ltn.com.tw/list/newspaper/opinion/',
            'http://news.ltn.com.tw/list/newspaper/world/',
            'http://news.ltn.com.tw/list/newspaper/business/',
            'http://news.ltn.com.tw/list/newspaper/sports/',
            'http://news.ltn.com.tw/list/newspaper/entertainment/',
            'http://news.ltn.com.tw/list/newspaper/consumer/',
            'http://news.ltn.com.tw/list/newspaper/supplement/'
        ]

        day = datetime.timedelta(days=1)
        current_time = NEWS_DATE_BEGIN

        while current_time <= TODAY:
            date = current_time.strftime('%Y%m%d')
            for url in urls:
                target = url + date
                yield scrapy.Request(target, callback=self.parse_news_list)
            current_time += day

    def parse_news_list(self, response):
        for news_item in response.css('.list li'):
            relative_url = news_item.css('a.tit::attr(href)').extract_first()
            abs_url = response.urljoin(relative_url)
            yield scrapy.Request(abs_url, callback=self.parse_tag_of_news)

        page_list = [
            int(p) for p in response.css('.pagination a::text').extract()
            if p.isdigit()
        ]
        current_page_extract = response.css(
            '.pagination a.active::text').extract_first()
        current_page = int(
            current_page_extract) if current_page_extract is True else 1
        if (not page_list) or (current_page >= max(page_list)):
            return

        next_page = current_page + 1

        if next_page in page_list:
            prefix = re.search(r'.*\/', response.url).group(0)
            relative_url = prefix + '/' + str(next_page)
            abs_url = response.urljoin(relative_url)
            yield scrapy.Request(abs_url, callback=self.parse_news_list)

    def parse_tag_of_news(self, response):
        tag_string = response.css(
            'head meta[name=keywords]::attr(content)').extract_first()
        tags = tag_string.split(',')

        yield {'tag': tags}
