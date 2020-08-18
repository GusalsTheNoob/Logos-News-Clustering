# dependency
from datetime import datetime

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
