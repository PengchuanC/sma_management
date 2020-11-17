"""
tradingdays
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-07-01
@desc: 获取交易日历
"""

import datetime
from sql import models
from sql.sql_templates import tradingday
from sql.utils import read_oracle, render


def get_tradingdays(date=None):
    """
    从gildata获取交易日数据
    :param date: 日期，默认为空
    :return:
    """
    if not date:
        date = datetime.date(1990, 1, 1)
    date = date.strftime('%Y-%m-%d')
    sql = render(tradingday.tradingday, '<date/>', date)
    data = read_oracle(sql)
    if data.empty:
        return
    return data


def commit_tradingdays():
    """添加交易日历"""
    date = models.TradingDays.objects.last()
    if not date:
        data = get_tradingdays()
    else:
        data = get_tradingdays(date.date)
    if data is None:
        return
    if not data.empty:
        ret = [models.TradingDays(date=r.date) for _, r in data.iterrows()]
        models.TradingDays.objects.bulk_create(ret)


if __name__ == '__main__':
    commit_tradingdays()
