"""
计算持仓区间收益
单只基金计算从买入到卖出期间的收益
@date: 2021-10-19
"""

import weakref
import pandas as pd
from django.db.models import Max

from sql import models


def commit_return_yield():
    portfolios = models.Portfolio.objects.filter(settlemented=0)
    for portfolio in portfolios:
        _commit_return_yield(portfolio)
        break


def _commit_return_yield(portfolio: models.Portfolio):
    last = models.Holding.objects.filter(port_code=portfolio.port_code).aggregate(mdate=Max('date'))['mdate']
    holding = models.Holding.objects.filter(port_code=portfolio.port_code, date=last).values('secucode', 'trade_market')
    holding = {x['secucode']: x['trade_market'] for x in holding}
    for secucode in holding:
        market = holding.get(secucode)
        ret = transactions(portfolio.port_code, secucode, last)
        if not ret:
            continue
        if market in (1, 2):
            # 场内交易
            im = proc_inner_market(portfolio.port_code, secucode, ret)
            print(im)
        else:
            pass


def transactions(port_code, secucode, date):
    operations = [
        '开放式基金认购成交确认', '开放式基金申购成交确认', '开放式基金赎回成交确认', '开放式基金转换转入成交确认',
        '开放式基金转换转出成交确认', '证券买入', '证券卖出'
    ]
    history = models.Transactions.objects.filter(
        port_code=port_code, secucode=secucode, operation__in=operations, date__lte=date
    ).values('date', 'order_price', 'order_value', 'operation')
    history = pd.DataFrame(history)
    if history.empty:
        # 回购
        return
    history['order_value'] = history['order_value'].astype(float)
    buy_op = ['开放式基金认购成交确认', '开放式基金申购成交确认', '开放式基金转换转入成交确认', '证券买入']
    sell_op = ['开放式基金赎回成交确认', '开放式基金转换转出成交确认', '证券卖出']
    buy = history[history.operation.isin(buy_op)][['date', 'order_price', 'order_value']]
    buy = buy.groupby(['date', 'order_price']).sum().reset_index().sort_values('date')
    sell = history[history.operation.isin(sell_op)][['date', 'order_price', 'order_value']]
    ret = []
    if sell.empty:
        # 没有卖出
        for _, d in buy.iterrows():
            ret.append({
                'buy_at': d.date, 'sell_at': date, 'deal_value': d.order_value,
                'buy_price': d.order_price, 'sell_price': None
            })
        return ret
    sell = sell.groupby(['date', 'order_price']).sum().reset_index()
    data = [r for _, r in buy.iterrows()]
    for _, r in sell.iterrows():
        for b in data:
            d = weakref.ref(b)()
            if r.order_value <= d.order_value:
                ret.append({
                    'buy_at': d.date, 'sell_at': r.date, 'deal_value': r.order_value,
                    'buy_price': d.order_price, 'sell_price': r.order_price
                })
                d.order_value -= r.order_value
                break
            elif r.order_value > d.order_value:
                ret.append({
                    'buy_at': d.date, 'sell_at': r.date, 'deal_value': d.order_value,
                    'buy_price': d.order_price, 'sell_price': r.order_price
                })
                r.order_value -= d.order_value
                d.order_value = 0

    for d in data:
        if d.order_value > 0:
            ret.append({
                'buy_at': d.date, 'sell_at': date, 'deal_value': d.order_value,
                'buy_price': d.order_price, 'sell_price': None
            })
    ret = sorted(ret, key=lambda x: x['buy_at'])
    ret = sorted(ret, key=lambda x: x['sell_at'])
    return ret


def security_category(port_code, secucode):
    pass


def proc_inner_market(port_code, secucode, trans: list):
    """处理场内交易"""
    ret = []
    for t in trans:
        if t['sell_price']:
            sell_price = float(t['sell_price'])
        else:
            o32 = models.PortfolioExpanded.objects.get(port_code=port_code).o32
            sp = models.SecurityPrice.objects.filter(o32=o32, secucode=secucode, date=t['sell_at']).latest('date')
            sell_price = sp.price
        buy_price = float(t['buy_price'])
        ret_yield = sell_price / buy_price - 1
        t['ret_yield'] = ret_yield
        ret.append(t)
    return ret


if __name__ == '__main__':
    commit_return_yield()
