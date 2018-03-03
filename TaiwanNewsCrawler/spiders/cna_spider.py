"""
中央社
the crawl deal with cna's news
Usage: scrapy crawl cna -o <filename.json>
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
import scrapy

ROOT_URL = 'http://www.cna.com.tw'
TODAY = datetime.today().date()


class CnaSpider(scrapy.Spider):
    name = "cna"
    start_urls = ['http://www.cna.com.tw/list/aall-1.aspx']

    def parse(self, response):
        current_page_index = int(
            response.css('.pagination li.current a::text').extract_first())

        newses_time_str = response.css('.article_list li span::text').extract()
        newses_time = [
            datetime.strptime(i, '%Y/%m/%d %H:%M').date()
            for i in newses_time_str
        ]
        is_over_today = False

        for t in newses_time:
            if t < TODAY:
                is_over_today = True

        if not is_over_today:
            next_url = 'http://www.cna.com.tw/list/aall-' + str(
                current_page_index + 1) + '.aspx'
            yield scrapy.Request(next_url, callback=self.parse)

        for news in response.css('div.article_list li a'):
            url = response.urljoin(news.css('a::attr(href)').extract_first())
            yield scrapy.Request(url, callback=self.parse_news)

    def parse_news(self, response):
        title = response.css('h1::text').extract_first()
        date = response.css('div.update_times p::text').extract_first()[5:]
        content = ''
        for p in response.css('div.article_box section p'):
            p_text = p.css('::text')
            if p_text:
                content += ' '.join(p_text.extract())

        category_links = response.css('div.breadcrumb span a span')
        category = category_links[1].css('::text').extract_first()

        yield {
            'website': "中央通訊社",
            'url': response.url,
            'title': title,
            'date': date[:10].replace('/', '-'),
            'content': content,
            'category': category
        }
