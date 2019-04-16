# -*- coding:utf-8 -*-
import time
import datetime
import functools
from .log import log


def print_run_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        local_time = time.time()
        ret = func(*args, **kw)
        log.info('[{}] run time is {:0.4f} seconds.'.format(func.__name__, time.time() - local_time))
        return ret
    return wrapper


class TimerCount(object):
    def __init__(self, msg):
        self.msg = msg

    def __enter__(self):
        self.start = time.clock()
        return self

    def __exit__(self, *args):
        self.end = time.clock()
        self.secs = self.end - self.start
        self.msecs = self.secs * 1000
        log.info('Run time of {0}: {1:0.3f} seconds.'.format(self.msg, self.secs))


def time2int(date=None):
    if date is None:
        date = datetime.date.today()
    y, m, d = map(int, date.split('-'))
    dd = datetime.datetime(y, m, d)
    return int(dd.timestamp() * 1000)


def int2time(timestamp):
    datearr = datetime.datetime.utcfromtimestamp(timestamp)
    timestr = datearr.strftime("%Y-%m-%d")
    return timestr


def add_one_day(date):
    ds = datetime.datetime.strptime(date, '%Y-%m-%d') + datetime.timedelta(days=1)
    ds = ds.strftime('%Y-%m-%d')
    return ds


def time_str(fine=True):
    if fine:
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    else:
        return time.strftime('%Y-%m-%d', time.localtime())


def sleep(secs):
    time.sleep(secs)


def unix_timestamp():
    return int(time.mktime(datetime.datetime.now().timetuple()))


def stamp2datetime(stamp):
    return datetime.datetime.fromtimestamp(stamp)
