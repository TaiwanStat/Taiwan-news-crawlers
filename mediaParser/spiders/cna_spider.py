import scrapy


class EbcSpider(scrapy.Spider):
    name = "cna"
    start_urls = [
                  'http://www.cna.com.tw/list/aall-1.aspx'
                 ]

    def parse(self, response):
        cna_url = 'http://www.cna.com.tw'
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
            'date': date,
            'content': content,
            'category': category
        }
