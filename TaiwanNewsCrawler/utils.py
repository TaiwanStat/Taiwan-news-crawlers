from typing import (Union, Tuple)
import datetime as dt

TODAY = dt.datetime.strptime(dt.datetime.now().strftime("%Y-%m-%d"), '%Y-%m-%d')
PARSE_DATE_FORMAT_LIST = ["%Y-%m-%d", "%Y/%m/%d", "%Y %m %d"]
PARSE_TIME_FORMAT_LIST = ["%H %M", "%H:%M", "%H %M %S", "%H:%M:%S"]


def parse_start_date_and_end_date(start_date: Union[str, None], end_date: Union[str, None]) -> Tuple[dt.datetime, dt.datetime]:
    if (not start_date is None):
        start_date = dt.datetime.strptime(start_date, '%Y-%m-%d')
    else:
        start_date = TODAY

    if (not end_date is None):
        end_date = dt.datetime.strptime(end_date, '%Y-%m-%d')
    else:
        end_date = TODAY
    end_date += dt.timedelta(days=1)
    return (start_date, end_date)


def parse_date(date_str: str, parse_format: str=None) -> dt.datetime:
    if (not parse_format is None):
        return dt.datetime.strptime(date_str, parse_format)
    
    for date_format in PARSE_DATE_FORMAT_LIST:
        for time_format in PARSE_TIME_FORMAT_LIST:
            try:
                date = dt.datetime.strptime(date_str, f"{date_format} {time_format}")
                break
            except:
                date = None
        if (not date is None):
            break
    return date


def can_crawl(date: dt.datetime, start_date: dt.datetime, end_date: dt.datetime) -> bool:
    if (date >= start_date and date <= end_date):
        return True
    else:
        return False