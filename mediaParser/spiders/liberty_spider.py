#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自由時報
"""
import scrapy
import time
import re

ROOT_URL = 'http://news.ltn.com.tw'
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
    name = "liberty"

    def start_requests(self):
        urls = [
            'http://news.ltn.com.tw/newspaper/focus/',
            'http://news.ltn.com.tw/newspaper/politics/',
            'http://news.ltn.com.tw/newspaper/society/',
            'http://news.ltn.com.tw/newspaper/local/',
            'http://news.ltn.com.tw/newspaper/life/',
            'http://news.ltn.com.tw/newspaper/opinion/',
            'http://news.ltn.com.tw/newspaper/world/',
            'http://news.ltn.com.tw/newspaper/business/',
            'http://news.ltn.com.tw/newspaper/sports/',
            'http://news.ltn.com.tw/newspaper/entertainment/',
            'http://news.ltn.com.tw/newspaper/consumer/',
            'http://news.ltn.com.tw/newspaper/supplement/'
        ]

        date = time.strftime('%Y%m%d')
        for url in urls:
            target = url + date
            yield scrapy.Request(target, callback=self.parse_news_list)

    def parse_news_list(self, response):
        for news_item in response.css('a.picword'):
            relative_url = news_item.css('a::attr(href)').extract_first()
            abs_url = response.urljoin(relative_url)
            yield scrapy.Request(abs_url, callback=self.parse_news)

        page_list = [int(p) for p in response.css('#page a::text').extract()]
        current_page = int(response.css('#page strong::text').extract_first())

        if not page_list or current_page >= max(page_list):
            return

        for page in page_list:
            if page > current_page:
                if 'page' in response.url:
                    relative_url = response.url[:-1] + str(page)
                else:
                    relative_url = response.url + '?page='+str(page)

                abs_url = response.urljoin(relative_url)
                yield scrapy.Request(abs_url, callback=self.parse_news_list)

    def parse_news(self, response):
        category = get_news_category(response)

        if category == 'opinion':
            title = response.css('h2::text').extract_first()
        else:
            title = response.css('h1::text').extract_first()

        if category == 'opinion':
            content = get_news_content(response,
                                            '.cont h4::text', '.cont p')
        elif category == 'sports':
            content = get_news_content(response,
                                            '.news_p h4::text', '.news_p p')
        elif category == 'entertainment':
            content = get_news_content(response, '.news_content h4::text',
                                            '.news_content p')
        else:
            content = get_news_content(response, '#newstext h4::text',
                                            '#newstext p')

        yield {
            'website': "自由時報",
            'url': response.url,
            'title': title,
            'date': time.strftime('%Y-%m-%d'),
            'content': content,
            'category': CATEGORY_DIC[category]
        }

def get_news_category(response):
    searched_category = re.search('\/news\/([a-z]*)\/', response.url)

    if searched_category and searched_category.group(1) != 'paper':
        return searched_category.group(1)
    elif 'talk' in response.url:
        return 'opinion'
    elif 'sports' in response.url:
        return 'sports'
    elif 'ent' in response.url:
        return 'entertainment'

def get_news_content(response, h4_query, p_query):
    h4 = response.css(h4_query).extract()
    h4_num = len(h4)
    counter = 0
    content = ""
    for p in response.css(p_query):
        if counter < h4_num:
            content += " " + h4[counter]
            counter += 1
        if p.css("p::text"):
            content += ' '.join(p.css("p::text").extract())
    return content
