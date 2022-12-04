# -*- coding: utf-8 -*-

import os


class Sysutil:

    def __getattr__(self, key: str) -> str:
        """Return System Enviroment value.

        @key: 会被转换成全大写
        """
        value = os.environ.get(key.upper())
        if value is None:
            return value
        if value.upper() == "TRUE":
            return True
        if value.upper() == "FALSE":
            return False
        return value

    def __setattr__(self, key: str, value: str) -> None:
        os.environ[key.upper()] = str(value)


if __name__ == '__main__':
    obj = Sysutil()
    print(obj.lang)
    obj.user = "inmove"
    print(obj.user)
