# Taiwan-news-crawlers

🐞 [Scrapy](https://scrapy.org)-based Crawlers for news of Taiwan including 10 media companies:
1. 中國時報
2. 中央社
3. 華視
4. 東森新聞雲
5. 自由時報
6. 壹蘋新聞網(原蘋果日報)
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

- Python3.7+
- Scrapy >= 1.3.0 ~ 2.7.0
- Twisted >= 16.6.0 ~ 22.8.0
- isort
- flake8
- black

## Usage

```python
# normal
scrapy crawl <spider> -o <output_name>

# if can crawl assign day
# example want to crawl 2022-10-26
scrapy crawl <spider> -o <output_name> -a start_date=2022-10-26 -a end_date=2022-10-26

# if can crawl old day
# example today is 2022-10-27
# will crawl '2022-10-25'~'2022-10-27'
scrapy crawl <spider> -o <output_name> -a start_date=2022-10-25
```

### Available spiders (all 10)

| Spider name | Rewrite finished and can crawl | Can crawl assign day | Can crawl old day | Key word(tag) | note |
| :--------: | :--------: | :--------: | :--------: | :--------: | :--------: |
| china | :heavy_check_mark: | :x: | :x: | :heavy_check_mark: |  |
| cna | :heavy_check_mark: | :x: | :x: | :white_check_mark: | not always crawl key word |
| cts | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | always crawl yesterday |
| ettoday | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |  |
| liberty | :heavy_check_mark: | :x: | :x: | :heavy_check_mark: |  |
| nextapple(origin of apple) | :heavy_check_mark: | :x: | :heavy_check_mark: | :heavy_check_mark: |  |
| pts | :heavy_check_mark: | :x: | :x: | :heavy_check_mark: |  |
| setn | :heavy_check_mark: | :x: | :x: | :heavy_check_mark: |  |
| tvbs | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |  |
| udn | :heavy_check_mark: | :x: | :heavy_check_mark: | :heavy_check_mark: |  |

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
