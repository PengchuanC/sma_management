"""
utils
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-09-04
@desc:
"""
import re
from math import ceil

from pandas import read_sql
from django.db.models import Max

from .connector import oracle, datayes
from sql import models


def render(string, flag, value):
    """替换sql templates中的<>标签"""
    return re.sub(flag, value, string)


def read_oracle(sql):
    """读取数据"""
    data = read_sql(sql, con=oracle)
    return data


def read_datayes(sql):
    """从barra因子数据库读取数据"""
    data = read_sql(sql, con=datayes)
    return data


def latest_update_date(model) -> dict:
    """model中证券的最后更新日期"""
    ret = model.objects.values('secucode').annotate(mdate=Max('date'))
    ret = {x['secucode']: x['mdate'] for x in ret}
    return ret


def replace_fund_instance(data):
    """
    将数据中的secucode替换为Fund实例
    Args:
        data: pandas dataframe object

    Returns:

    """
    instance = models.Funds.objects.all()
    instance = {x.secucode: x for x in instance}
    data['secucode'] = data['secucode'].apply(lambda x: instance.get(x))
    data = data[data['secucode'].notnull()]
    return data


def chunk(array, size=1):
    """Creates a list of elements split into groups the length of `size`. If
    `array` can't be split evenly, the final chunk will be the remaining
    elements.

    Args:
        array (list): List to chunk.
        size (int, optional): Chunk size. Defaults to ``1``.

    Returns:
        list: New list containing chunks of `array`.

    Example:

        >>> chunk([1, 2, 3, 4, 5], 2)
        [[1, 2], [3, 4], [5]]

    .. versionadded:: 1.1.0
    """
    chunks = int(ceil(len(array) / float(size)))
    return [array[i * size:(i + 1) * size] for i in range(chunks)]


def commit_by_chunk(data, model, size=50000):
    """
    为避免数据库一次插入数据过多，导致性能下降，分段提交数据
    Args:
        size: 一次提交的数据量
        data: pandas dataframe
        model: django models
    Returns:
        NoneType
    """
    ms = [model(**x) for _, x in data.iterrows()]
    chunks = chunk(ms, size)
    for c in chunks:
        model.objects.bulk_create(c)
