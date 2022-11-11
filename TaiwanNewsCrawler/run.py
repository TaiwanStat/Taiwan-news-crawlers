import datetime as dt
import os
import sys

import utils

ENV_PATH = "/home/localadmin/news-crawler-last-ver/Taiwan-news-crawlers/env/bin/python"
CRAWL_TODAY = True
START_DAY = utils.YESTERDAY.strftime("%Y-%m-%d")
END_DAY = utils.YESTERDAY.strftime("%Y-%m-%d")


def run(test):
    if CRAWL_TODAY:
        crawler_name_list = ["china", "cna", "cts", "ettoday", "liberty", "pts", "setn", "tvbs", "udn"]
        start_date = utils.TODAY
        end_date = utils.TODAY
    else:
        crawler_name_list = ["cts", "ettoday", "tvbs"]
        start_date = utils.parse_date(START_DAY)
        end_date = utils.parse_date(END_DAY)

    date = start_date
    while date <= end_date:
        for name in crawler_name_list:
            date_str = date.strftime("%Y-%m-%d")
            if CRAWL_TODAY:
                cmd = f"scrapy crawl {name} -o all-crawl-news/{name}/{name}_{date_str}.json -L ERROR"
            else:
                cmd = f"scrapy crawl {name} -o all-crawl-news/{name}/{name}_{date_str}.json -a start_date={date_str} -a end_date={date_str} -L ERROR"  # fmt: skip
            if len(ENV_PATH) > 0:
                cmd = f"{ENV_PATH} -m {cmd}"
            if test:
                cmd = f"{ENV_PATH} -m scrapy list"
            print(cmd)
            os.system(cmd)
        date += dt.timedelta(days=1)


if __name__ == "__main__":
    test = True
    if len(sys.argv) > 1:
        para = sys.argv[1]
        if para == "test":
            test = True
    else:
        run(test)
