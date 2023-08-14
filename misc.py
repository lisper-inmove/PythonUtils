# -*- coding: utf-8 -*-

import uuid
from .idate import IDate


class IDWithDateError(Exception):
    ...


class Misc:

    PRIME_NUMBER_ARRAYS = [
        [211, 223, 461, 601, 607, 487],
        [631, 907, 511, 277, 7, 877],
        [883, 179, 83, 613, 773, 941],
        [269, 853, 643, 101, 653, 659],
        [421, 193, 569, 587, 787, 13],
        [509, 971, 337, 53, 149, 73],
        [557, 89, 257, 499, 919, 109],
        [67, 797, 419, 683, 701, 829],
        [197, 37, 311, 947, 239, 617]
    ]

    # 2	        3	5	7	11	13	17	19	23	29	31	37	41	43	47	53	59	61	67
    # 71	73	79	83	89	97	101	103	107	109	113	127	131	137	139	149	151	157	163
    # 167	173	179	181	191	193	197	199	211	223	227	229	233	239	241	251	257	263	269
    # 271	277	281	283	293	307	311	313	317	331	337	347	349	353	359	367	373	379	383
    # 389	397	401	409	419	421	431	433	439	443	449	457	461	463	467	479	487	491	499
    # 503	509	521	523	541	547	557	563	569	571	577	587	593	599	601	607	613	617	619
    # 631	641	643	647	653	659	661	673	677	683	691	701	709	719	727	733	739	743	751
    # 757	761	769	773	787	797	809	811	821	823	827	829	839	853	857	859	863	877	881
    # 883	887	907	911	919	929	937	941	947	953	967	971	977	983	991	997

    @staticmethod
    def uuid():
        return str(uuid.uuid4())

    @staticmethod
    def uuid_no_strike():
        _uuid = Misc.uuid()
        _uuid = _uuid.replace("-", "")
        return _uuid

    @classmethod
    def id_with_date(cls, try_times=None):
        if try_times is None:
            try_times = 1
        if try_times == 0:
            raise IDWithDateError("Generate id_with_date Error")
        _id = Misc.uuid_no_strike()
        _id = [i for i in _id]
        try:
            _positions = cls.__get_prime(_id)
        except IDWithDateError:
            return cls.id_with_date(try_times=try_times - 1)
        now = IDate.now_withformat("%y%m%d")
        for index, _position in enumerate(_positions):
            _id[_position] = str(now[index])
        return "".join(_id)

    @classmethod
    def extract_date(cls, id):
        _positions = cls.__get_prime(id)
        date = []
        for _position in _positions:
            date.append(str(id[_position]))
        return "".join(date)

    @classmethod
    def __get_prime(cls, id):
        _index = ord(id[-1]) % (len(Misc.PRIME_NUMBER_ARRAYS))
        _init_index = _index
        # 最后一个位必须用于寻找prime_array,所以不能变
        _id_len = len(id) - 1
        while True:
            _primes = Misc.PRIME_NUMBER_ARRAYS[_index]
            _positions = [
                a % _id_len for a in _primes
            ]
            if len(set(_positions)) != len(_primes):
                _index = (_index + 1) % len(Misc.PRIME_NUMBER_ARRAYS)
                if _init_index == _index:
                    raise IDWithDateError(f"this id: {id} cannot add date in it")
                continue
            return _positions
