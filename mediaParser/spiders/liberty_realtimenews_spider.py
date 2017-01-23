#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自由時報即時新聞
"""
import scrapy
import time
import re
from datetime import datetime, date, time

ROOT_URL = 'http://news.ltn.com.tw/'
Realtime_NEWS_URL = 'http://news.ltn.com.tw/list/BreakingNews'
today = date.today()

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
    'sports': '體育',
    'car': '汽車',
    '3c': '3c',
    'istyle': 'istyle'
}


class LibertySpider(scrapy.Spider):
    name = "libertyRealtime"
    start_urls = [
        'http://news.ltn.com.tw/list/BreakingNews'
    ]

    def parse(self, response):
        regex = '\?page\=(\d+)'
        current_index = re.search(regex, response.url)
        if current_index:
            next_index = int(current_index.group(1))+1
        else:
            next_index = 2
        date_of_news = response.css('#newslistul span::text').extract()
        last_page = False
        for d in date_of_news:
            d = datetime.strptime(d, '%Y-%m-%d %H:%M')
            d = d.date()
            if d != today:
                last_page = True
                break

        if current_index == '1':
            url = response.css('.NsFcrt a::attr(href)').extract_first()
            url = ROOT_URL + url
            yield scrapy.Request(url, callback=self.parse_news, meta=meta)

        for news_item in response.css('#newslistul li'):
            news_date = news_item.css('span::text').extract_first()
            news_date = datetime.strptime(news_date, '%Y-%m-%d %H:%M')
            news_date = news_date.date()
            if news_date == today:
                relative_url = news_item.css('a::attr(href)').extract()[1]
                abs_url = response.urljoin(relative_url)
                yield scrapy.Request(abs_url, callback=self.parse_news)

        if not last_page:
            next_target = Realtime_NEWS_URL+'?page='+str(next_index)
            yield scrapy.Request(next_target, callback=self.parse)

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
        elif category == 'car':
            content = get_news_content(response, '.con h4::text',
                                            '.con p')
        elif category == '3c':
            content = get_news_content(response, '.cont h4::text',
                                            '.cont p')
        elif category == 'istyle':
            content = get_news_content(response, '.boxTitle h4::text',
                                            '.boxTitle p')
        else:
            content = get_news_content(response, '#newstext h4::text',
                                            '#newstext p')
        print('debug: '+'\''+category+'\'')
        yield {
            'website': "自由時報",
            'url': response.url,
            'title': title,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'content': content,
            'category': CATEGORY_DIC[category]
        }


def get_news_category(response):
    searched_category = re.search('\/news\/([a-z]*)\/breakingnews\/', response.url)

    if searched_category and searched_category.group(1) != 'paper':
        return searched_category.group(1)
    elif 'talk' in response.url:
        return 'opinion'
    elif 'sports' in response.url:
        return 'sports'
    elif 'ent' in response.url:
        return 'entertainment'
    elif 'auto' in response.url:
        return 'car'
    elif '3c' in response.url:
        return '3c'
    elif 'istyle' in response.url:
        return 'istyle'


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
