"""
index
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-11-12
@desc: 同步股票数据
"""

import datetime
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
    for i, stock in enumerate(full):
        models.Stock.objects.update_or_create(secucode=stock.pop('secucode'), defaults=stock)
        progressbar(i, length)


def commit_industry_sw():
    """同步股票申万行业分类"""
    full = read_oracle(template.stock_sw)
    full = full.to_dict(orient='records')
    for stock in full:
        f = models.Stock.objects.filter(secucode=stock.pop('secucode')).last()
        if f:
            models.StockIndustrySW.objects.update_or_create(secucode=f, defaults=stock)


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


if __name__ == '__main__':
    commit_stock_expose()
