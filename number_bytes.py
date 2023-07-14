"""
使用struct在数字与字节数组之间互换
https://docs.python.org/3/library/struct.html
"""

import struct
import sys


class NumberBytes:

    """
    数字大小端转换, 将本地端转换成指定端
    >>> obj = NumberBytes()
    >>> obj.reset_format(2)
    >>> obj.to_big(30)
    reset_format必须先调用
    """

    big = ">"
    little = "<"
    network = "!"  # 等同于big
    native_native = "@"
    native_standard = "="
    default = native_native
    native = sys.byteorder

    def reset_format(self, digit, is_unsigned=False, is_float=False):
        """
        digit: 数字占用的位数
        is_unsigned: 是否是无符号
        is_float: 是否是
        """
        _format = None
        if not is_float:
            if digit == 1:
                _format = 'b'
            if digit == 2:
                _format = 'h'
            if digit == 4:
                _format = 'i'
            if digit == 8:
                _format = 'q'
            if is_unsigned:
                _format = _format.upper()
        else:
            if digit == 4:
                _format = 'f'
            if digit == 8:
                _format = 'd'
        if _format is None:
            msg = """
            digit must in (1, 2, 4, 8) if is_float is False
            digit must in (4, 8)  if is_float is True
            """
            raise Exception(f'Format Error: {msg}')
        self._format = _format

    def to_big(self, number):
        if self.native == "big":
            return number
        input_format = f"{self.little}{self._format}"
        output_format = f"{self.big}{self._format}"
        result = struct.unpack(output_format, struct.pack(input_format, number))
        return result[0]

    def to_little(self, number):
        if self.native == "little":
            return number
        input_format = f"{self.big}{self._format}"
        output_format = f"{self.little}{self._format}"
        result = struct.unpack(output_format, struct.pack(input_format, number))
        return result[0]

    def n2b(self, number):
        s = struct.pack(self._format, number)
        b = ''.join(format(c, '08b') for c in s)
        tmp = [f'({len(b)})']
        tmpv = ''
        for i in b:
            tmpv += i
            if len(tmpv) == 8:
                tmp.append(tmpv)
                tmpv = ''
        b = ','.join(tmp)
        return b


if __name__ == '__main__':
    obj = NumberBytes()
    _slash_t = '\t'
    _nl = '\n'

    test_value = 127
    digit = 2
    obj.reset_format(digit)
    print(">>>>>>>>>>>>>>>>>> test1 <<<<<<<<<<<<<<<<<<<<<<<<")
    result = obj.to_big(test_value)
    print(f"{test_value}{_nl}{_slash_t}{obj.n2b(test_value)}")
    print(f"{result}{_nl}{_slash_t}{obj.n2b(result)}")
    result = obj.to_little(test_value)
    print(f"{test_value}{_nl}{_slash_t}{obj.n2b(test_value)}")
    print(f"{result}{_nl}{_slash_t}{obj.n2b(result)}")

    digit = 4
    test_value = 127.8
    obj.reset_format(digit, is_float=True)
    print(">>>>>>>>>>>>>>>>>> test2 <<<<<<<<<<<<<<<<<<<<<<<<")
    result = obj.to_big(test_value)
    print(f"{test_value}{_nl}{_slash_t}{obj.n2b(test_value)}")
    print(f"{result}{_nl}{_slash_t}{obj.n2b(result)}")
    result = obj.to_little(test_value)
    print(f"{test_value}{_nl}{_slash_t}{obj.n2b(test_value)}")
    print(f"{result}{_nl}{_slash_t}{obj.n2b(result)}")

    test_value = 128
    digit = 2
    obj.reset_format(digit, is_unsigned=True)
    result = obj.to_big(test_value)
    print(">>>>>>>>>>>>>>>>>> test3 <<<<<<<<<<<<<<<<<<<<<<<<")
    print(f"{test_value}{_nl}{_slash_t}{obj.n2b(test_value)}")
    print(f"{result}{_nl}{_slash_t}{obj.n2b(result)}")
    result = obj.to_little(test_value)
    print(f"{test_value}{_nl}{_slash_t}{obj.n2b(test_value)}")
    print(f"{result}{_nl}{_slash_t}{obj.n2b(result)}")
