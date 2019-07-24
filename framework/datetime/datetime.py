from datetime import datetime,timedelta
import time
import re
import pdb
import calendar

UTC_MASK = "%Y-%m-%dT%H-%M-%SZ"


def datetime_to_str(date_raw=None, mask=None, exception_value=None):
    """
    Converts a datetime object into a time on format if possible.
    Returns the exception value optional parameter otherwise.

    :param date_raw: the datetime object to be converted
    :param exception_value: an optional value to be returned on exception cases
    :return:
    """
    if isinstance(date_raw, datetime):
        try:
            return date_raw.strftime(mask)
        except Exception as e:
            return exception_value
    return exception_value


def now_to_str():
    return datetime_to_str(date_raw=datetime.utcnow(), mask=UTC_MASK, exception_value="")