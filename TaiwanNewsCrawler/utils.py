import datetime as dt
from typing import Tuple, Union

TODAY = dt.datetime.strptime(dt.datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d")
YESTERDAY = TODAY - dt.timedelta(days=1)
PARSE_DATE_FORMAT_LIST = ["", "%Y-%m-%d", "%Y/%m/%d", "%Y %m %d"]
PARSE_INTERVAL_FORMAT_LIST = ["", " ", "T"]
PARSE_TIME_FORMAT_LIST = ["", "%H %M", "%H:%M", "%H %M %S", "%H:%M:%S"]
PARSE_TIMEZONE_FORMAT_LIST = ["", "%z"]


def parse_start_date_and_end_date(
    start_date: Union[str, None],
    end_date: Union[str, None],
    start_date_default: dt.datetime = TODAY,
    end_date_default: dt.datetime = TODAY,
) -> Tuple[dt.datetime, dt.datetime]:
    if start_date is not None:
        start_date = dt.datetime.strptime(start_date, "%Y-%m-%d")
    else:
        start_date = start_date_default

    if end_date is not None:
        end_date = dt.datetime.strptime(end_date, "%Y-%m-%d")
    else:
        end_date = end_date_default
    end_date += dt.timedelta(days=1)
    return (start_date, end_date)


def parse_date(date_str: str, parse_format: str = None) -> dt.datetime:
    if parse_format is not None:
        try:
            date = dt.datetime.strptime(date_str, parse_format)
        except Exception as e:
            date = None
        return date

    date = None
    for date_format in PARSE_DATE_FORMAT_LIST:
        if date is not None:
            break
        for interval_format in PARSE_INTERVAL_FORMAT_LIST:
            if date is not None:
                break
            for time_format in PARSE_TIME_FORMAT_LIST:
                if date is not None:
                    break
                for timezone_format in PARSE_TIMEZONE_FORMAT_LIST:
                    try:
                        date = dt.datetime.strptime(
                            date_str, f"{date_format}{interval_format}{time_format}{timezone_format}"
                        )
                        break
                    except Exception as e:
                        date = None
    return date


def can_crawl(date: dt.datetime, start_date: dt.datetime, end_date: dt.datetime) -> bool:
    if date >= start_date and date <= end_date:
        return True
    else:
        return False
