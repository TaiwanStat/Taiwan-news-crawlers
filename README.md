# Taiwan-news-crawlers

🐞 [Scrapy](https://scrapy.org)-based Crawlers for news of Taiwan including 10 media companies:
1. 蘋果日報
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
$ git clone https://github.com/TaiwanStat/Taiwan-news-crawlers.git
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
- [ ] apple (not update since 2022/09/01)
- [ ] appleRealtime (not update since 2022/09/01)
- [X] china
- [X] cna
- [X] cts(can select date)
- [X] ettoday(can select date)
- [X] liberty
- [ ] libertyRealtime
- [ ] pts
- [ ] setn
- [ ] tvbs
- [ ] udn

## Output
| Key | Value |
| :---      |          :--- |
| website   | the publisher|
| url       | the origin web|
| title     | the news title|
| content   | the news content      |
| category  | the category of news |

## License
The MIT License
