import scrapy
import time
import re

class LibertySpider(scrapy.Spider):
    name = "liberty"

    def start_requests(self):
        url = [
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

        date =time.strftime('%Y%m%d')
        #date = '20161202'
        for urls in url:
            target = urls + date
            yield scrapy.Request(target, callback = self.parse)

    def parse(self, response):
        now_page = int ( response.css('div#page strong::text').extract_first() )
        pages = response.css('div#page a::text').extract()
        
        pages_int = []
        isTheEnd = 1

        for page in pages:
            pages_int.append(int(page))

        for element in pages_int:
            if element > now_page:
                isTheEnd = 0
                now_page = now_page +1
                break

        if (response.url.find("page") > -1) & (isTheEnd == 0):
            url = response.url[:-1]+str(now_page)
            if url is not None:
                url = response.urljoin(url)
                yield scrapy.Request(url, callback=self.parse)

        if (response.url.find("page") == -1) & (isTheEnd == 0):
            url = response.url+'?page='+str(now_page)
            if url is not None:
                url = response.urljoin(url)
                yield scrapy.Request(url, callback=self.parse)

        for news in response.css('a.picword'):
            url = 'http://news.ltn.com.tw'+news.css('a::attr(href)').extract_first();
            if url is not None:
                url = response.urljoin(url)
                yield scrapy.Request(url, callback = self.parse_news)

    def parse_news(self, response):

        if((re.search('\/news\/([a-z]*)\/', response.url) is not None) and (re.search('\/news\/([a-z]*)\/', response.url).group(1)!='paper')):
            category = re.search('\/news\/([a-z]*)\/', response.url).group(1)
        elif ( response.url.find("talk") > -1 ):
            category = 'opinion'
        elif ( response.url.find("sports") > -1 ):
            category = 'sports'
        elif ( response.url.find("ent") > -1 ):
            category = 'entertainment'

        if category=='talk':
            title = response.css('h2::text').extract_first()
        else:
            title = response.css('h1::text').extract_first()

        date = time.strftime('%Y-%m-%d')
        

        if category=='opinion':
            h4 = response.css('.cont h4::text').extract()
            h4_num = len(h4)
            counter = 0
            content = ""
            for p in response.css(".cont p"):
                if(counter<h4_num):
                    content += " "+h4[counter]
                    counter = counter +1
                content += " "+(p.css('p::text').extract_first() if ((p.css("p::text")).extract_first()) else "");
        elif category == 'sports':
            h4 = response.css('.news_p h4::text').extract()
            h4_num = len(h4)
            counter = 0
            content = ""
            for p in response.css(".news_p p"):
                if(counter<h4_num):
                    content += " "+h4[counter]
                    counter = counter +1
                content += " "+(p.css('p::text').extract_first() if ((p.css("p::text")).extract_first()) else "");
        elif category == 'entertainment':
            h4 = response.css('.news_content p').extract()
            h4_num = len(h4)
            counter = 0
            content = ""
            for p in response.css(".news_content p"):
                if(counter<h4_num):
                    content += " "+h4[counter]
                    counter = counter +1
                content += " "+(p.css('p::text').extract_first() if ((p.css("p::text")).extract_first()) else "");
        else:
            h4 = response.css('div#newstext h4::text').extract()
            h4_num = len(h4)
            counter = 0
            content = ""
            for p in response.css("div#newstext p"):
                if(counter<h4_num):
                    content += " "+h4[counter]
                    counter = counter +1
                content += " "+(p.css('p::text').extract_first() if ((p.css("p::text")).extract_first()) else "");
        
        if category == 'focus':
            category = '焦點'
        elif category == 'politics':
            category = '政治'
        elif category == 'society':
            category = '社會'
        elif category == 'local':
            category = '地方'
        elif category == 'life':
            category = '生活'
        elif category == 'opinion':
            category = '言論'
        elif category == 'world':
            category = '國際'
        elif category == 'business':
            category = '財經'
        elif category == 'entertainment':
            category = '娛樂'
        elif category == 'consumer':
            category = '消費'
        elif category == 'supplement':
            category = '副刊'
        elif category == 'sports':
            category = '體育'
           

        yield{
            'website':"自由時報",
            'url': response.url,
            'title': title,
            'date':date,
            'content': content,
            'category': category
        }