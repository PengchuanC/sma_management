"""
wind_wrapper
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-09-04
@desc: wind
"""

from functools import wraps


def use_wind(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            from WindPy import w
            if not w.isconnected():
                w.start()
            ret = func(*args, **kwargs)
        except ImportError:
            ret = func(*args, **kwargs)
        return ret
    return inner
