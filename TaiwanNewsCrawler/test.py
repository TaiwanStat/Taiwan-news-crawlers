import os
from datetime import datetime


def run():
    day = datetime.today().strftime('%Y-%m-%d')
    test_crawler_name = ["china", "cna", "cts", "ettoday", "liberty", "pts", "setn", "tvbs", "udn"]
    for name in test_crawler_name:
        cmd = f"scrapy crawl {name} -o {name}_{day}.json -L ERROR"
        print(cmd)
        os.system(cmd)


if (__name__ == "__main__"):
    run()