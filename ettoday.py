"""
東森新聞雲
"""
import sys
import json

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import date


def write_json(file_name, content):
    with open(file_name, 'w') as output_file:
        json.dump(content, output_file, ensure_ascii=False, indent=4)


def get_news_content(url):
    content = ''
    response = requests.get(url)
    news_soup = BeautifulSoup(response.text, 'html.parser')

    div = news_soup.find('div', 'story')
    if div:
        p_list = div.find_all('p')
    else:
        print ('Unable to parse content:', url)

    for p in p_list:
        content += p.get_text()
    return content


today = date.today().strftime("%Y%m%d")
today_slash = date.today().strftime("%Y/%m/%d")
today_dash = date.today().strftime("%Y-%m-%d")

output_dir = sys.argv[1]
output = []
offset = 0
is_finish = False

while not is_finish:
    print('Offset', offset)
    r = requests.post('http://www.ettoday.net/show_roll.php',
                      data={'offset': offset, 'tPage': 3,
                            'tFile': today + '.xml',
                            'tOt': 0, 'tSi': 100})

    soup = BeautifulSoup(r.text, 'html.parser')
    news_list = soup.find_all('h3')
    for news in news_list:
        news_date = news.span.get_text()
        is_today_news = today_slash in news_date

        if is_today_news:
            title = news.a.get_text()
            category = news.em.get_text()
            url = news.a.get('href')
            if url[0] == '/':
                url = 'http://www.ettoday.net' + url

            content = get_news_content(url)
            output.append({
                'website': '東森新聞雲',
                'title': title,
                'url': url,
                'category': category,
                'date': news_date,
                'content': content
            })
        # history news
        else:
            is_finish = True
            break
    offset += 1

print('Total news count:', len(output))
output_filename = '{}/ettoday_{}.json'.format(output_dir, today_dash)
write_json(output_filename, output)
