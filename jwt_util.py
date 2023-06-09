# -*- coding: utf-8 -*-

import random

import jwt

from .idate import IDate


class PayloadNotDictException(Exception):

    def __init__(self):
        super().__init__("payload must a dict")


class TokenExpiredException(Exception):

    def __init__(self):
        super().__init__("Token Epxired")


class JWTUtil:

    alg = "HS256"
    headers = {
        "alg": alg,
        "typ": "JWT"
    }
    salt = "c30002929a1314f4e7cb105d9482d44b"

    TOKEN_VALID_TIME_PERIOD = IDate.ONE_DAY * 7

    def generate_token(self, payload: dict) -> str:
        if not isinstance(payload, dict):
            raise PayloadNotDictException()
        payload.update({
            'create_time': IDate.now_timestamp(),
            'expire_at': IDate.now_timestamp() + self.TOKEN_VALID_TIME_PERIOD,
            'need_login': False,
            'random_value1': random.randint(1, 999999), # 增加两个随机数，减少生成相同token的概率
            'random_value2': random.randint(1, 999999)
        })
        token = jwt.encode(
            payload=payload,
            key=self.salt,
            algorithm=self.alg,
            headers=self.headers
        )
        return token

    def decode(self, token):
        result = jwt.decode(token, self.salt, self.alg)
        now = IDate.now_timestamp()
        # 已超过expire_at5分钟,已过期
        if now - result.get('expire_at') > IDate.ONE_MIN * 5:
            raise TokenExpiredException()
        # 已超过expire_at,但是还不足5分钟,提示用户需要重新登陆
        if 0 < now - result.get('expire_at') < IDate.ONE_MIN * 5:
            result.update({
                'need_login': True
            })
        return result


if __name__ == '__main__':
    obj = JWTUtil()
    token = obj.generate_token({"name": "inmove"})
    print(token)
    print(obj.decode(token))
