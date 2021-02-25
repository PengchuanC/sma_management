"""
组合持股相关
"""

import datetime
import pandas as pd

from django.db.models import Max
from .. import models


def fund_holding_stock(port_code: str, date: str or datetime.date):
    """获取组合在给定日期的持股情况"""
    funds = models.Holding.objects.filter(port_code=port_code, date=date).values('secucode', 'mkt_cap')
    fund_codes = [x['secucode'] for x in funds]
    # 获取基金主代码
    associate = models.FundAssociate.objects.filter(relate__in=fund_codes).order_by('define').values('secucode', 'relate')
    associate = {x['relate']: x['secucode'] for x in associate}
    na = models.Balance.objects.get(port_code=port_code, date=date).net_asset
    funds = {associate.get(x['secucode'], x['secucode']): x['mkt_cap'] / na for x in funds}
    recent_report_date = models.FundHoldingStock.objects.values('secucode').annotate(recent=Max('date'))
    recent = {x['secucode']: x['recent'] for x in recent_report_date}
    query_set = []
    for fund in funds:
        stocks = models.FundHoldingStock.objects.filter(
            secucode=fund, date=recent.get(fund)
        ).values('secucode', 'stockcode', 'stockname', 'ratio', 'publish')
        publish = set([x['publish'] for x in stocks])
        if '年报' in publish:
            stocks = [x for x in stocks if x['publish'] == '年报']
        query_set.extend(stocks)

    data: pd.DataFrame = pd.DataFrame(query_set)
    if data.empty:
        return None
    data['ratio'] = data.aggregate(func=lambda x: x['ratio']*funds.get(x['secucode']), axis=1)
    names = dict(zip(data['stockcode'], data['stockname']))
    data = data.groupby(['stockcode'])['ratio'].sum()
    data = data.reset_index()
    data['stockname'] = data.stockcode.apply(lambda x: names.get(x))
    data = data.sort_values(by='ratio', ascending=False).reset_index(drop=True)
    data['key'] = data.index + 1
    return data


def fund_holding_stock_by_fund(funds: list):
    """
    基金持股情况
    Args:
        funds: 基金列表

    Returns:

    """
    associate = models.FundAssociate.objects.filter(
        relate__in=funds).order_by('define').values('secucode', 'relate')
    associate = {x['relate']: x['secucode'] for x in associate}
    recent_report_date = models.FundHoldingStock.objects.values('secucode').annotate(recent=Max('date'))
    recent = {x['secucode']: x['recent'] for x in recent_report_date}
    query_set = []
    for fund in funds:
        relate = associate.get(fund, fund)
        stocks = models.FundHoldingStock.objects.filter(
            secucode=relate, date=recent.get(relate)
        ).values('secucode', 'stockcode', 'ratio', 'publish')
        publish = set([x['publish'] for x in stocks])
        if '年报' in publish:
            stocks = [x for x in stocks if x['publish'] == '年报']
        query_set.extend(stocks)

    data: pd.DataFrame = pd.DataFrame(query_set)
    return data
