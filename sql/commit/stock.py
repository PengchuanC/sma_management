"""
index
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-11-12
@desc: 同步股票数据
"""


from sql import models
from sql.sql_templates import stock as template
from sql.utils import read_oracle
from sql.progress import progressbar


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


if __name__ == '__main__':
    commit_industry_sw()
