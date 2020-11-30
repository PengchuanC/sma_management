"""
funds_extend
~~~~~~~~~~~~
扩充基金数据同步，处理复杂的同步程序
"""
import datetime
import math

from sql import models
from sql.sql_templates import funds
from sql.utils import read_oracle, render


def commit_holding_stock_detail():
    """同步基金完整持仓"""
    publish = '年报'
    _commit(publish, funds.fund_holding_stock_detail, funds.fund_holding_stock_detail_date)


def commit_holding_top_ten():
    """同步基金季报重仓股"""
    publish = '季报'
    _commit(publish, funds.fund_top_ten_stock, funds.fund_top_ten_stock_date)


def commit_announcement():
    """同步基金公告数据"""
    exist = models.FundAnnouncement.objects.last()
    if exist:
        date = exist.date
    else:
        date = datetime.date.today() + datetime.timedelta(days=-30)
    date = date.strftime('%Y-%m-%d')
    sql = render(funds.fund_announcement, '<date>', date)
    data = read_oracle(sql)
    fund = models.Holding.objects.values('secucode').distinct()
    fund = [x['secucode'] for x in fund]
    fund = models.Funds.objects.filter(secucode__in=fund).all()
    fund = {x.secucode: x for x in fund}
    data.secucode = data.secucode.apply(lambda x: fund.get(x))
    data = data[data.secucode.notnull()]
    ret = (models.FundAnnouncement(**x) for _, x in data.iterrows())
    for i in ret:
        try:
            i.save()
        except Exception as e:
            print(e.__class__)


def _commit(publish: str, sql, sql_date):
    """"""
    max_date = read_oracle(sql_date)['date'][0].date()
    existed = models.FundHoldingStock.objects.filter(publish=publish, date=max_date).values('secucode').distinct()
    existed = [x['secucode'] for x in existed]

    full = models.Funds.objects.all()
    need = [x.secucode for x in full if x.secucode not in existed]
    data = read_oracle(sql)
    data = data[data.secucode.isin(need)]
    full = {x.secucode: x for x in full}
    data.secucode = data.secucode.apply(lambda x: full.get(x))
    data = data.to_dict(orient='records')
    data = [models.FundHoldingStock(**x) for x in data]
    split = math.ceil(len(data) / 10000)
    for i in range(split):
        models.FundHoldingStock.objects.bulk_create(data[i*10000: (i+1)*10000])


if __name__ == '__main__':
    commit_announcement()
