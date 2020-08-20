# dependency
from datetime import datetime, timedelta
import re

# datetime object => yymmdd timestamp


def datetime_to_datestamp(datetime_obj):
    """
    A utility function that converts datetime object to yymmdd timestamp.
    Currently used in data_collection.py
    @param      datetime_obj    datetime(date)  A datetime object of date obj contain y, m, d info.
    @return     timestamp       str             A corresonding yymmdd timestamp.
    """
    year = datetime_obj.year
    month = datetime_obj.month
    month = f"0{month}" if month < 10 else month
    date = datetime_obj.day
    date = f"0{date}" if date < 10 else date
    return f"{year}{month}{date}"


def trimNewsURL(raw_url):
    """
    A utility function that replaces html & representation into real &
    Currently used in data_collection.py
    @param  raw_url str     A url with "&" written as "&amp"
    @return url     str     A proper url
    """
    return re.sub("&amp", "&", raw_url)


def ntimestamp_to_datetime(timestamp, time_standard):
    unit_dict = {unit: 0 for unit in ['초전', '분전', '시간전', '일전']}
    unit_part = re.sub("[0-9.]", "", timestamp)
    number_part = re.sub("[^0-9.]", "", timestamp)
    unit_dict[unit_part] = int(number_part)
    result = time_standard - \
        timedelta(days=unit_dict['일전'], hours=unit_dict['시간전'],
                  minutes=unit_dict['분전'], seconds=unit_dict['초전'])
    return result


def convert_to_mobile(pc_url):
    url_dict = {part[0]: part[1] for part in map(
        lambda x: x.split("="), pc_url[pc_url.index("?")+1:].split("&"))}
    return f"https://n.news.naver.com/mnews/article/{url_dict['oid']}/{url_dict['aid']}"
