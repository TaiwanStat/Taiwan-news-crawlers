import scrapy

class UdnSpider(scrapy.Spider):
    
    name = "udn"
    start_urls = [
                  'http://udn.com/news/archive/0/0/2016/11/09/1'
                  ]
                  
    def parse(self,response) :
        for news in response.css('td a') :
            url = news.css('a::attr(href)').extract_first()
            yield scrapy.Request(url, callback = self.parse_news)
        
        #####Auto parse next page#####
        total_pages = response.css("div.pagelink span.total::text").extract_first()
        total_pages = int(total_pages[2:-2])
        current_page = int(response.url[response.url.rindex('/')+1:])+1
        if current_page <= total_pages :
            next_page = response.url[0:response.url.rindex('/')+1] + str(current_page)
            yield scrapy.Request(next_page, callback=self.parse)
        #for i in range( 2,total_pages+1 ) :
        #    next_page = response.url + '/' + str(i)

        #####Auto parse next page#####

    def parse_news(self, response) :
        title = response.css('h1::text').extract_first()
        date = response.css('div.story_bady_info_author::text').extract_first()
        content = ""
        for p in response.css('p') :
            if p.css('::text') :
                content += p.css('::text').extract_first() + "\n"
            else :
                content += ""

        a_index = 0
        for a in response.css('div div div.only_web a') :
            if a_index == 1 :
                category = a.css('::text').extract_first()
                break
            a_index += 1

        yield {
            'website':"聯合報",
            'url': response.url,
            'title': title,
            'date':date,
            'content': content,
            'category':category
        }





