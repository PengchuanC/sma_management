"""
index
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-11-12
@desc: 同步股票数据
"""

import datetime
from django.db import transaction
from copy import deepcopy
from math import ceil
from dateutil.parser import parse
from sql import models
from sql.sql_templates import stock as template
from sql.utils import read_oracle, read_datayes, render
from sql.progress import progressbar


def chunk(array, size=1):
    chunks = int(ceil(len(array) / float(size)))
    return [array[i * size:(i + 1) * size] for i in range(chunks)]


def stock_code_in_local():
    """获取本地已保存的股票代码列表"""
    stocks = models.Stock.objects.all()
    return [x.secucode for x in stocks]


def commit_stock():
    full = read_oracle(template.stock)
    full = full.to_dict(orient='records')
    length = len(full)
    local = stock_code_in_local()
    with transaction.atomic():
        for i, stock in enumerate(full):
            if stock['secucode'] in local:
                continue
            models.Stock.objects.update_or_create(secucode=stock.pop('secucode'), defaults=stock)
            progressbar(i, length)


def commit_industry_sw():
    """同步股票申万行业分类"""
    full = read_oracle(template.stock_sw)
    full = full.to_dict(orient='records')
    stocks = list({x['secucode'] for x in full if not x['secucode'].startswith('X')})
    all_ = models.Stock.objects.filter(secucode__in=stocks).all()
    all_ = {x.secucode: x for x in all_}
    with transaction.atomic():
        for s in full:
            # 不使用深拷贝这里导致了一个严重的问题：数据错乱
            s = deepcopy(s)
            c = s['secucode']
            if any([c.startswith('4'), c.startswith('8'), c.startswith('X')]):
                continue
            f = all_.get(s.pop('secucode'))
            if not f:
                continue
            s['secucode'] = f
            m: models.StockIndustrySW = models.StockIndustrySW.objects.filter(secucode=f).last()
            first = s['firstindustryname']
            second = s['secondindustryname']
            if m:
                if m.firstindustryname == first:
                    continue
                m.firstindustryname = first
                m.secondindustryname = second
                m.save()
            else:
                models.StockIndustrySW.objects.create(secucode=f, firstindustryname=first, secondindustryname=second)


def commit_stock_expose():
    """同步因子暴露度数据"""
    exist = models.StockExpose.objects.last()
    if exist:
        date = exist.date
    else:
        date = datetime.date(2020, 10, 1)
    sql = render(template.stock_expose, '<date>', date.strftime('%Y%m%d'))
    data = read_datayes(sql)
    stocks = list(set(list(data.secucode)))
    stocks = models.Stock.objects.filter(secucode__in=stocks).all()
    stocks = {x.secucode: x for x in stocks}
    data['secucode'] = data['secucode'].apply(lambda x: stocks.get(x))
    data = data[data.secucode.notnull()]
    data.date = data.date.apply(lambda x: parse(x).date())
    need = []
    for _, r in data.iterrows():
        need.append(models.StockExpose(**r.to_dict()))
    need = chunk(need, 1000)
    for n in need:
        models.StockExpose.objects.bulk_create(n)


def commit_stock_daily_quote():
    """同步股票日度行情数据

    首先从本地表单sma_stock_daily_quote查询最新交易日期
    根据最新交易日期从聚源查询全部股票大于该日期的忍度行情数据
    最终只会保留本地表单sma_stocks中收录的股票的行情数据
    """
    _commit_stock_data(models.StockDailyQuote, template.stock_quote)


def commit_stock_capital_flow():
    """同步股票日度资金流动

    首先从本地表单sma_stock_capital_flow查询最新交易日期
    根据最新交易日期从聚源查询全部股票大于该日期的资金流动数据
    最终只会保留本地表单sma_stocks中收录的股票的资金流动数据
    """
    _commit_stock_data(models.CapitalFlow, template.stock_capital_flow)


def _commit_stock_data(model: models.StockDailyQuote or models.CapitalFlow, sql: str):
    """同步股票行情或资金流向数据

    Args:
        model:
        sql:

    Returns:

    """
    exist = model.objects.last()
    if exist:
        date = exist.date
    else:
        date = datetime.date(2020, 1, 1)
    sql = render(sql, '<date>', date.strftime('%Y-%m-%d'))
    data = read_oracle(sql)
    stocks = models.Stock.objects.all()
    stocks = {x.secucode: x for x in stocks}
    data.secucode = data.secucode.apply(lambda x: stocks.get(x))
    data = data[data.secucode.notnull()]
    ret = [model(**x) for _, x in data.iterrows()]
    ret = chunk(ret, 5000)
    for r in ret:
        model.objects.bulk_create(r)


if __name__ == '__main__':
    commit_stock_capital_flow()
