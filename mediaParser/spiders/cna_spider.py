import scrapy

class EbcSpider(scrapy.Spider):
    
    name = "cna"
    start_urls = [
                  'http://www.cna.com.tw/list/aall-1.aspx'
                  ]
        
    def parse(self,response) :
        for news in response.css('div.article_list li a') :
            cna_url = 'http://www.cna.com.tw'
            url = cna_url + news.css('a::attr(href)').extract_first()
            yield scrapy.Request(url, callback = self.parse_news)

    def parse_news(self, response) :
        title = response.css('h1::text').extract_first()
        date = response.css('div.update_times p::text').extract_first()
        date = date[5:]
        content = ""
        for p in response.css('div.article_box section p') :
            if p.css('::text') :
                content += p.css('::text').extract_first() + "\n"
            else :
                content += ""
        
        a_index = 0
        for a in response.css('div.breadcrumb span a span') :
            if a_index == 1 :
                category = a.css('::text').extract_first()
                break
            a_index += 1

        yield {
            'website':"中央通訊社",
            'url': response.url,
            'title': title,
            'date':date,
            'content': content,
            'category':category
        }





