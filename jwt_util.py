# -*- coding: utf-8 -*-

import jwt


class JWTUtil:

    alg = "HS256"
    headers = {
        "alg": alg,
        "typ": "JWT"
    }
    salt = "c30002929a1314f4e7cb105d9482d44b"

    def generate_token(self, payload):
        token = jwt.encode(
            payload=payload,
            key=self.salt,
            algorithm=self.alg,
            headers=self.headers
        )
        return token

    def decode(self, token):
        result = jwt.decode(token, self.salt, self.alg)
        return result


if __name__ == '__main__':
    obj = JWT()
    token = obj.generate_token({"name": "inmove"})
    print(token)
    print(obj.decode(token))
