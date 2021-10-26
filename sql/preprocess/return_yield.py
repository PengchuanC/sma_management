"""
计算持仓区间收益
单只基金计算从买入到卖出期间的收益
@date: 2021-10-19
"""
import datetime
import math
import weakref
import pandas as pd
from django.db.models import Max

from sql import models


def commit_return_yield():
    portfolios = models.Portfolio.objects.filter(settlemented=0)
    for portfolio in portfolios:
        _commit_return_yield(portfolio)


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
        else:
            category = security_category(secucode)
            if category == '私募理财':
                im = proc_private(portfolio.port_code, secucode, ret)
            else:
                im = proc_mutual(portfolio.port_code, secucode, ret)
        for r in im:
            models.ReturnYield.objects.update_or_create(
                port_code=portfolio, secucode=secucode, date=last, buy_at=r['buy_at'], sell_at=r['sell_at'],
                defaults=r
            )


def transactions(port_code, secucode, date):
    operations = [
        '开放式基金认购成交确认', '开放式基金申购成交确认', '开放式基金赎回成交确认', '开放式基金转换转入成交确认',
        '开放式基金转换转出成交确认', '证券买入', '证券卖出', '开放式基金红利再投资', '增加证券流通数量'
    ]
    history = models.Transactions.objects.filter(
        port_code=port_code, secucode=secucode, operation__in=operations, date__lte=date
    ).values('date', 'order_price', 'order_value', 'operation')
    history = pd.DataFrame(history)
    if history.empty:
        # 回购
        return
    history['order_value'] = history['order_value'].astype(float)
    buy_op = ['开放式基金认购成交确认', '开放式基金申购成交确认', '开放式基金转换转入成交确认', '证券买入', '开放式基金红利再投资']
    sell_op = ['开放式基金赎回成交确认', '开放式基金转换转出成交确认', '证券卖出']
    buy = history[history.operation.isin(buy_op)][['date', 'order_price', 'order_value']]
    buy = buy.groupby(['date', 'order_price']).sum().reset_index().sort_values('date')
    buy = buy[buy['order_price'] != 0]
    sell = history[history.operation.isin(sell_op)][['date', 'order_price', 'order_value']]
    ret = []
    if sell.empty:
        # 没有卖出
        for _, d in buy.iterrows():
            ret.append({
                'buy_at': d.date, 'sell_at': date + datetime.timedelta(days=1), 'deal_value': d.order_value,
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
        # 小份额视为OP做账误差
        if float(d.order_value) > 10:
            # 加1天是为了后续能取到当日净值（后续会取T-1日净值）
            ret.append({
                'buy_at': d.date, 'sell_at': date+datetime.timedelta(days=1), 'deal_value': d.order_value,
                'buy_price': d.order_price, 'sell_price': None
            })
    ret = sorted(ret, key=lambda x: x['buy_at'])
    ret = sorted(ret, key=lambda x: x['sell_at'])
    return ret


def security_category(secucode):
    security = models.Security.objects.filter(secucode=secucode).last()
    if not security:
        return '开放式基金'
    return security.category


def one_day_before_adjust_nav(secucode, date):
    """前一日复权单位净值"""
    obj = models.FundAdjPrice.objects.filter(secucode=secucode, date__lt=date).latest('date')
    return obj


def days_count(start, end):
    """两个日期之间交易日个数统计"""
    days = models.TradingDays.objects.filter(date__gte=start, date__lte=end)
    days = [x.date for x in days]
    return len(days)


def proc_inner_market(port_code, secucode, trans: list):
    """处理场内交易"""
    ret = []
    for t in trans:
        start = t['buy_at']
        end = t['sell_at']
        if t['sell_price']:
            sell_price = float(t['sell_price'])
        else:
            o32 = models.PortfolioExpanded.objects.get(port_code=port_code).o32
            try:
                sp = models.SecurityPrice.objects.filter(o32=o32, secucode=secucode, date__lt=end).latest('date')
                t['sell_at'] = sp.date
                sell_price = sp.price
            except models.SecurityPrice.DoesNotExist:
                sp = models.FundQuote.objects.filter(secucode=secucode, date=end).last()
                sell_price = sp.closeprice
        buy_price = float(t['buy_price'])
        ret_yield = sell_price / buy_price - 1
        t['ret_yield'] = ret_yield
        count = days_count(start, end)
        annualized = math.pow(1 + ret_yield, 250 / count) - 1
        t['annualized'] = annualized
        ret.append(t)
    return ret


def proc_private(port_code, secucode, trans):
    """处理私募基金"""
    return proc_inner_market(port_code, secucode, trans)


def proc_mutual(port_code, secucode, trans):
    """由于流水取的成交确认日期，因此实际确认净值为T-1日净值（忽略T+2等估值方式）"""
    ret = []
    for t in trans:
        start = t['buy_at']
        end = t['sell_at']
        # 排除op做账错误，如增加证券流通成本之类的
        if start > end:
            continue
        adj_start_obj = one_day_before_adjust_nav(secucode, start)
        adj_end_obj = one_day_before_adjust_nav(secucode, end)
        count = days_count(adj_start_obj.date, adj_end_obj.date)
        sp = adj_start_obj.adj_nav
        ep = adj_end_obj.adj_nav
        ret_yield = ep / sp - 1
        t['sell_at'] = adj_end_obj.date
        t['ret_yield'] = ret_yield
        annualized = math.pow(1 + ret_yield, 250 / count) - 1
        t['annualized'] = annualized
        ret.append(t)
    return ret


if __name__ == '__main__':
    commit_return_yield()
