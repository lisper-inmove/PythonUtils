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
            start_time = IDate.now_millseconds()
            result = fn(*args, **kargs)
            finish_time = IDate.now_millseconds()
            logger.info(f"{self._prefix} {fn.__name__} 耗时 {finish_time - start_time}毫秒")
            if finish_time - start_time > 0.5:
                logger.info(f"{self._prefix} {fn.__name__} 参数 {args} {kargs}")
            return result
        return inner
