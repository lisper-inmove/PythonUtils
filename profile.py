# -*- coding: utf-8 -*-

from functools import wraps

from .logger import Logger
from .idate import IDate

logger = Logger()


class TimeExpand:

    def __init__(self, prefix=None):
        self._prefix = prefix


class FuncTimeExpend(TimeExpand):

    def __call__(self, fn):
        @wraps(fn)
        def inner(*args, **kargs):
            start_time_msec = IDate.now_milliseconds()
            result = fn(*args, **kargs)
            end_time_sec_msec = IDate.now_milliseconds()
            logger.info(f"{self._prefix} {fn.__name__} 耗时 {end_time_sec_msec - start_time_msec}毫秒")
            if end_time_sec_msec - start_time_msec > 0.5:
                logger.info(f"{self._prefix} {fn.__name__} 参数 {args} {kargs}")
            return result
        return inner
