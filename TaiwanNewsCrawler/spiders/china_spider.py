"""
中國時報
the crawl deal with chinatimes's news
Usage: scrapy crawl china -o <filename.json>
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
import TaiwanNewsCrawler.utils as utils


ROOT_URL = 'http://www.chinatimes.com'
PAGE_URL = 'http://www.chinatimes.com/newspapers/2601'

class ChinaSpider(scrapy.Spider):
    name = "china"
    start_urls = ['http://www.chinatimes.com/newspapers/2601']

    def __init__(self, start_date: str=None, end_date: str=None):
        super().__init__(start_date=start_date, end_date=end_date)

    def parse(self, response: scrapy.Selector):
        start_date, end_date = utils.parse_start_date_and_end_date(self.start_date, self.end_date)

        crawl_next = False
        news_in_page = response.css('ul.vertical-list li')
        if not news_in_page:
            return

        for news in news_in_page:
            news_date = utils.parse_date(news.css('time::attr(datetime)').extract_first())
            if (news_date is None):
                continue
            crawl_next = utils.can_crawl(news_date, start_date, end_date)
            
            if (crawl_next):
                url = news.css('a::attr(href)').extract_first()
                if (not ROOT_URL in url):
                    url = ROOT_URL + url
                url = response.urljoin(url)
                yield scrapy.Request(url, callback=self.parse_news)
        
        if ('next_page' in response.meta):
            meta = {'next_page': response.meta['next_page'] + 1}
        else:
            meta = {'next_page': 2}
        
        if (crawl_next):
            next_url = PAGE_URL + '?page=' + str(meta['next_page'])
            yield scrapy.Request(next_url, callback=self.parse, meta=meta)

    def parse_news(self, response: scrapy.Selector):
        title = response.css('h1::text').extract_first()
        date_of_news_str = response.css('time::attr(datetime)').extract_first()
        date_of_news = utils.parse_date(date_of_news_str, '%Y-%m-%d %H:%M')
        content = ""
        for p in response.css('div.article-body p'):
            p_text = p.css('::text')
            if p_text:
                content += ''.join(p_text.extract())

        category = response.css('meta[name=section]::attr(content)').extract_first()

        yield {
            'website': "中國時報",
            'url': response.url,
            'title': title,
            'date': date_of_news,
            'content': content,
            'category': category
        }
