"""
utils
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-09-04
@desc:
"""
import re

from pandas import read_sql

from .connector import oracle


def render(string, flag, value):
    """替换sql templates中的<>标签"""
    return re.sub(flag, value, string)


def read_oracle(sql):
    """读取数据"""
    data = read_sql(sql, con=oracle)
    return data
