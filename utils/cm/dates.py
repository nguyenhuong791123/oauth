
# -*- coding: UTF-8 -*-
import datetime
from .utils import is_empty

class Dates():
    year = '%Y'
    month = '%m'
    day = '%d'
    hour = '%H'
    minute = '%M'
    seconds = '%S'
    f = '%f'

def get_datetime(pattern, msec):
    dt = datetime.datetime.now()
    if pattern is None:
        return dt.strftime('%Y-%m-%d %H:%M')
    if msec is None:
        return dt.strftime(pattern)
    return dt.strftime(pattern)[:msec]

def get_pattern(date, time, regex, msec):
    d = Dates()
    ms = ''
    if msec == True:
        ms = d.f

    if date == True and time == True:
        if is_empty(regex) == False:
            return d.year + regex + d.month + regex + d.day + ' ' + d.hour + ':' + d.minute + ':' + d.seconds + ms
        else:
            return d.year + d.month + d.day + d.hour + d.minute + d.seconds + ms
    elif date == True:
        if is_empty(regex) == False:
            return d.year + regex + d.month + regex + d.day + ms
        else:
            return d.year + d.month + d.day + ms
    elif time == True:
        if is_empty(regex) == False:
            return d.hour + regex + d.minute + regex + d.seconds + ms
        else:
            return d.hour + d.min + d.seconds + ms
    else:
        return d.hour + ':' + d.minute + ':' + d.seconds + ms

def datetime_to_str(dt, pattern):
    if is_empty(pattern):
        return dt.strftime
    return dt.strftime(pattern)

def grant_expires(seconds=600):
    return datetime.datetime.now() + datetime.timedelta(seconds=seconds)

def token_expires(seconds=3600):
    return datetime.datetime.now() + datetime.timedelta(seconds=seconds)
