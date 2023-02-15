# -*- coding: utf-8 -*-

from functools import wraps


def set_attr(**attrs):
    """为函数设置属性."""
    def inner1(fn):
        """为函数设置属性."""
        @wraps(fn)
        def inner2(*args, **kargs):
            return fn(*args, **kargs)
        for name, value in attrs.items():
            setattr(inner2, name, value)
        return inner2
    return inner1
