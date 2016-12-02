import scrapy
import urllib.request
import re
import w3lib.url
# -- coding: utf-8 --

class AppleSpider(scrapy.Spider):
    name = "apple"
    start_urls = [
        'http://www.appledaily.com.tw/appledaily/todayapple',#蘋果每日新聞總覽
    ]

    def parse(self, response):
        #response.css("h2.nust").extract() #蘋果新聞分類
        #response.css("ul.fillup li a::attr(title)").extract() #新聞標題
        for news in response.css("ul.fillup li"):
            if news.css("a::attr(href)").extract_first().find("http://www.eat-travel.com.tw/") > -1:
                # url = news.css("a::attr(href)").extract_first()
                continue
            elif news.css("a::attr(href)").extract_first().find("http://ent.appledaily.com.tw/") > -1 :
                url = news.css("a::attr(href)").extract_first()
                url = w3lib.url.canonicalize_url(url)
                url = urllib.request.urlopen(url, None, 1).geturl()
                m = re.search('entertainment\/(\d*\/\d*\/)', url).group(1);
                url = 'http://ent.appledaily.com.tw/section/article/headline/'+m;
            else:
                url = "http://www.appledaily.com.tw" + news.css("a::attr(href)").extract_first()
            if url is not None:
                url = response.urljoin(url)
                yield scrapy.Request(url, callback = self.parse_news)

    def parse_news(self, response):
        h2 = response.css("div.articulum h2::text").extract();
        h2_num = len(h2)
        counter = 0;
        content = "";
        title = "";
        date =  time.strftime('%Y-%m-%d')
        for p in response.css("div.articulum p"):
            content += " "+(p.css("::text").extract_first() if ((p.css("p::text")).extract_first()) else "");
            if(counter<h2_num):
                content += " "+h2[counter];
                counter = counter +1
        if response.css("hgroup h1::text"):
            title += response.css("hgroup h1::text").extract_first()
        if response.css("hgroup h2::text"):
            title += response.css("hgroup h2::text").extract_first()
        yield{
            'website':"蘋果日報",
            'url': response.url,
            'title': title,
            'date':date,
            'content': content,
            'category':response.css("meta[name=\"keywords\"]::attr(content)").extract_first()
        }
