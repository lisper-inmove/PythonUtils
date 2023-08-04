# -*- coding: utf-8 -*-

import time

from datetime import datetime
from datetime import timedelta
from enum import IntEnum
from typing import List
import pytz


class Weekday(IntEnum):

    MON = 0
    TUE = 1
    WED = 2
    THU = 3
    FRI = 4
    SAT = 5
    SUN = 6


class IDate:

    ONE_SEC = 1
    ONE_MIN = 60 * ONE_SEC
    ONE_HOUR = 60 * ONE_MIN
    ONE_DAY = 24 * ONE_HOUR

    @classmethod
    def now_timestamp(cls) -> int:
        return int(datetime.now().timestamp())

    @classmethod
    def now_milliseconds(cls) -> int:
        return datetime.now().timestamp()

    @classmethod
    def now_withformat(cls, fmt="%Y-%m-%d %H:%M:%S"):
        return datetime.now().strftime(fmt)

    @classmethod
    def today_zero_date(
            cls,
            tz: str = None,
    ) -> datetime:
        """返回今天0点的时间戳."""
        if tz is None:
            tz = pytz.UTC
        now = datetime.now(tz)
        zero = now.replace(hour=0, minute=0, second=0)
        return zero

    @classmethod
    def prev_zero_timestamp(
            cls,
            timestamp: int
    ) -> datetime:
        """某个时间戳之前的一天的零点."""
        return cls.date_zero_timestamp(timestamp) - timedelta(1)

    @classmethod
    def next_zero_timestamp(
            cls,
            timestamp: int
    ) -> datetime:
        """某个时间戳之后的一天的零点."""
        return cls.date_zero_timestamp(timestamp) + timedelta(1)

    @classmethod
    def date_zero_timestamp(
            cls,
            timestamp: int
    ) -> datetime:
        """根据时间戳获取那一天0点的时间戳."""
        date = datetime.fromtimestamp(timestamp, tz=pytz.UTC)
        result = date.replace(hour=0, minute=0, second=0)
        return result

    @classmethod
    def piecewise_time(
            cls,
            start_time_sec: int,
            end_time_sec_sec: int,
    ) -> List:
        """将时间分段.

        Args:
            start_time_sec: 时间戳,开始时间
            end_time_sec_sec: 时间戳,结束时间
        Returns:
            [(start_time_sec, a), (b, c), (d, e), (f, end_time_sec_sec)]: a~f 分别表示0
        Examples:
            start_time_sec 表示 2022-10-12 12:30:39
            end_time_sec_sec 表示 2022-10-14 08:08:19
            [
                ("2022-10-12 12:30:39", "2022-10-13 00:00:00"),
                ("2022-10-13 00:00:00", "2022-10-14 00:00:00"),
                ("2022-10-14 00:00:00", "2022-10-14 08:08:19")
            ]

        """
        start_date = datetime.fromtimestamp(start_time_sec)
        end_date = datetime.fromtimestamp(end_time_sec_sec)
        delta_days = (end_date - start_date).days
        # start_time_sec, end_time_sec_sec都表示在一天之内
        if delta_days == 0:
            return [(start_time_sec, end_time_sec_sec)]
        result = []
        first_zero = start_date.replace(hour=0, minute=0, second=0) + timedelta(1)
        last_zero = end_date.replace(hour=0, minute=0, second=0)
        result.append((start_time_sec, int(first_zero.timestamp())))
        begin_day = first_zero
        for i in range(0, delta_days):
            begin_day = begin_day + timedelta(1)
            end_day = begin_day + timedelta(1)
            result.append(
                (int(begin_day.timestamp()), int(end_day.timestamp()))
            )
        result.append((int(last_zero.timestamp()), end_time_sec_sec))
        return result

    def __init__(
        self,
        fmt: str = None,
        init_str: str = None,
        init_timestamp: int = None,
        tzone: str = None
    ):
        if fmt is None:
            self._fmt = "%Y-%m-%d %H:%M:%S"
        if tzone is None:
            self._tzone = pytz.UTC
        else:
            self._tzone = pytz.timezone(tzone)
        if init_str is not None and init_timestamp is not None:
            raise Exception("init_str and init_timestamp cannot be supplied both")
        if init_str:
            self._date = self.__init_from_str(init_str)
        if init_timestamp:
            self._date = self.__init_from_timestamp(init_timestamp)
        if all([
            init_str is None,
            init_timestamp is None
        ]):
            self._date = self.__init_from_timestamp(int(time.time()))

    def __init_from_str(self, init_str):
        result = datetime.strptime(init_str, self._fmt)
        result.astimezone(self._tzone)
        return result

    def __init_from_timestamp(self, init_timestamp):
        result = datetime.fromtimestamp(init_timestamp, self._tzone)
        return result

    def __str__(self):
        result = f"{self._date} => {self._fmt} => {self._tzone}"
        return result

    def days_add(self, days):
        result = self._date + timedelta(days=days)
        return result

    def hours_add(self, hours):
        result = self._date + timedelta(hours=hours)
        return result

    def minutes_add(self, minutes):
        result = self._date + timedelta(minutes=minutes)
        return result

    def to_timezone(self, tz):
        """时区转换.
        一定会先将当前时区转换成UTC，然后再转成tz
        """
        result = self._date.astimezone(pytz.UTC).astimezone(tz)
        return result

    def next_weekday(self, weekday):
        """下一个周几."""
        _weekday = self._date.weekday()
        # 下一个今天
        if weekday == _weekday:
            return self.days_add(7)
        # 本周的已经过了
        elif weekday > _weekday:
            return self.days_add(weekday - _weekday)
        else:  # 本周的还没过
            return self.days_add(7 - (_weekday - weekday))

    def timestamp(self):
        return int(self._date.timestamp())
