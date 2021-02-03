
import datetime

from itertools import count
from collections import Counter
from django.db.models import Max
from threading import Thread, Lock
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from sql.sql_templates import funds as template
from sql import models


def get_fund_last_update_date(model):
    dates = model.objects.values('secucode').annotate(mdate=Max('date'))
    dates = {x['secucode']: x['mdate'] for x in dates}
    return dates


class DataGetter(object):
    """数据获取

    Attributes:
        model: 模型
        sql: 对应的sql语句

    """
    def __init__(self, model, sql):
        self.m = model
        self.sql = sql


if __name__ == '__main__':
    a = get_fund_last_update_date(models.FundPrice)
    print(Counter(a.values()))
