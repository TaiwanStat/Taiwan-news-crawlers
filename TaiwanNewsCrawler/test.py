import os
import datetime as dt
import utils

CRAWL_TODAY = True
START_DAY = utils.YESTERDAY.strftime('%Y-%m-%d')
END_DAY = utils.YESTERDAY.strftime('%Y-%m-%d')

def run():
    if (CRAWL_TODAY):
        crawler_name_list = ["china", "cna", "cts", "ettoday", "liberty", "pts", "setn", "tvbs", "udn"]
        start_date = utils.TODAY
        end_date = utils.TODAY
    else:
        crawler_name_list = ["cts", "ettoday", "tvbs"]
        start_date = utils.parse_date(START_DAY)
        end_date = utils.parse_date(END_DAY)
    
    date = start_date
    while (date <= end_date):
        for name in crawler_name_list:
            date_str = date.strftime('%Y-%m-%d')
            if (CRAWL_TODAY):
                cmd = f"scrapy crawl {name} -o {name}_{date_str}.json -L ERROR"
            else:
                cmd = f"scrapy crawl {name} -o {name}_{date_str}.json -a start_date={date_str} -a end_date={date_str} -L ERROR"
            print(cmd)
            os.system(cmd)
        date += dt.timedelta(days=1)


if (__name__ == "__main__"):
    run()