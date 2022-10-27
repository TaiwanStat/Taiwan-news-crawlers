# Taiwan-news-crawlers

🐞 [Scrapy](https://scrapy.org)-based Crawlers for news of Taiwan including 10 media companies:
1. 蘋果日報(2022/09/01開始不再更新)
2. 中國時報
3. 中央社
4. 華視
5. 東森新聞雲
6. 自由時報
7. 公視
8. 三立
9. TVBS
10. UDN


## Getting Started

```
$ git clone https://github.com/cool9203/Taiwan-news-crawlers.git
$ cd Taiwan-news-crawlers
$ pip install -r requirements.txt
$ scrapy crawl apple -o apple_news.json
```

## Prerequisites

- Python3
- Scrapy >= 1.3.0 ~ 2.7.0
- Twisted >= 16.6.0 ~ 22.8.0

## Usage
```scrapy crawl <spider> -o <output_name>```

### Available spiders (all 11)

| Spider name | Rewrite finished | Can crawl old day | Key word(tag) | note |
| :--------: | :--------: | :--------: | :--------: | :--------: |
| apple | :x: | :x: | :x: | stop update since 2022/09/01 |
| appleRealtime | :x: | :x: | :x: | stop update since 2022/09/01 |
| china | :heavy_check_mark: | :x: | :heavy_check_mark: |  |
| cna | :heavy_check_mark: | :x: | :white_check_mark: | not always crawl key word |
| cts | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | always crawl yesterday |
| ettoday | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |  |
| liberty | :heavy_check_mark: | :x: | :heavy_check_mark: |  |
| pts | :heavy_check_mark: | :x: | :heavy_check_mark: |  |
| setn | :heavy_check_mark: | :x: | :heavy_check_mark: |  |
| tvbs | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |  |
| udn | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |  |

## Output
| Key | Value |
| :---      |          :--- |
| website   | the publisher|
| url       | the origin web|
| title     | the news title|
| content   | the news content      |
| category  | the category of news |
| description  | the description of news |
| key_word  | the key_word of news |

## License
The MIT License
