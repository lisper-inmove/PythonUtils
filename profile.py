# -*- coding: utf-8 -*-

import asyncio

from functools import wraps
import psutil

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
            logger.info(f"{self._prefix} {fn.__name__} consume {end_time_sec_msec - start_time_msec} milliseconds")
            if end_time_sec_msec - start_time_msec > 0.5:
                logger.warning(f"{self._prefix} {fn.__name__} params {args} {kargs}")
            return result
        return inner


def func_time_expend_async(fn):
    @wraps(fn)
    async def wrapper_async_function(*args, **kargs):
        cpu_percent = psutil.cpu_percent(percpu=True)
        memory_percent = psutil.virtual_memory().percent
        start_time_msec = IDate.now_milliseconds()
        result = await fn(*args, **kargs)
        end_time_sec_msec = IDate.now_milliseconds()
        logger.info(f"{fn.__name__} consume {end_time_sec_msec - start_time_msec} milliseconds {cpu_percent} {memory_percent}")
        if end_time_sec_msec - start_time_msec > 0.5:
            logger.warning(f"{fn.__name__} params {args} {kargs} {end_time_sec_msec - start_time_msec} milliseconds")
        return result

    @wraps(fn)
    async def wrapper_async_generator(*args, **kargs):
        cpu_percent = psutil.cpu_percent(percpu=True)
        memory_percent = psutil.virtual_memory().percent
        start_time_msec = IDate.now_milliseconds()
        async for value in fn(*args, **kargs):
            yield value
        end_time_sec_msec = IDate.now_milliseconds()
        logger.info(f"{fn.__name__} consume {end_time_sec_msec - start_time_msec} milliseconds {cpu_percent} {memory_percent}")
        if end_time_sec_msec - start_time_msec > 0.5:
            logger.warning(f"{fn.__name__} params {args} {kargs} {end_time_sec_msec - start_time_msec} milliseconds")

    if asyncio.iscoroutinefunction(fn):
        return wrapper_async_function
    else:
        return wrapper_async_generator
