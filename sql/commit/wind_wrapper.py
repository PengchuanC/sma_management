"""
wind_wrapper
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-09-04
@desc: wind
"""

from functools import wraps

from WindPy import w


def use_wind(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if not w.isconnected():
            w.start()
        ret = func(*args, **kwargs)
        return ret
    return inner
