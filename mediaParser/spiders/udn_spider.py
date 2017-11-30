"""
聯合報
the crawl deal with udn's news
Usage: scrapy crawl udn -o <filename.json>
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import scrapy

TODAY_STR = datetime.now().strftime('%m-%d')

class UdnSpider(scrapy.Spider):
    name = "udn"

    def start_requests(self):
        urls = ['https://udn.com/news/breaknews/1']
        for url in urls:
            meta = {'iter_time': 1}
            yield scrapy.Request(url, callback=self.parse, meta=meta)

    def parse(self, response):
        has_next_page = True
        isFirstIter = response.meta['iter_time'] == 1
        response.meta['iter_time'] += 1
        elSelector = '#breaknews_body dt' if isFirstIter else 'dt'
        target = response.css(elSelector)
        if not target:
            has_next_page = False
        for news in target:
            url = news.css('a::attr(href)').extract_first()
            url = response.urljoin(url)
            date_time = news.css('.info .dt::text').extract_first()

            if TODAY_STR not in date_time:
                has_next_page = False
                break

            yield scrapy.Request(url, callback=self.parse_news)


        if has_next_page:
            iter_time = response.meta['iter_time']
            yield scrapy.FormRequest(url='https://udn.com/news/get_breaks_article/%d/1/0' % iter_time,
                                        callback=self.parse, meta=response.meta)


    def parse_news(self, response):
        title = response.css('h1::text').extract_first()
        date_of_news = response.css('.story_bady_info_author span::text').extract_first()[:10]

        content = ""
        for p in response.css('p'):
            p_text = p.css('::text')
            if p_text:
                content += ' '.join(p_text.extract())

        category_links = response.css('div div div.only_web a')
        category = category_links[1].css('::text').extract_first()

        yield {
            'website': "聯合報",
            'url': response.url,
            'title': title,
            'date': date_of_news,
            'content': content,
            'category': category
        }
