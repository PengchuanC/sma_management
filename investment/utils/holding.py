"""
组合持股相关

@modify: 2021-03-01
"""

import datetime
import pandas as pd

from django.db.models import Max
from .. import models


def fund_holding_stock(port_code: str, date: str or datetime.date, in_exchange=True):
    """获取组合在给定日期的持股情况"""
    if in_exchange:
        market = [1, 2, 6]
    else:
        market = [6]
    funds = models.Holding.objects.filter(
        port_code=port_code, date=date, trade_market__in=market
    ).values('secucode', 'mkt_cap')
    funds = [x for x in funds]
    if not funds:
        return
    na = models.Balance.objects.get(port_code=port_code, date=date).net_asset
    funds = {x['secucode']: x['mkt_cap'] / na for x in funds}
    data = fund_holding_stock_by_fund(list(funds.keys()))

    if data.empty:
        return
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
    query_set = []
    for fund in funds:
        stocks = fund_top_ten_scale(fund, scale=False)
        if stocks is None:
            continue
        query_set.append(stocks)
    if not query_set:
        return
    data: pd.DataFrame = pd.concat(query_set, axis=0)
    return data


def index_holding_sw(index_code: str) -> pd.DataFrame:
    """股票指数持仓sw行业分布

    Args:
        index_code: 指数代码

    Returns:
                stockcode  weight secucode firstindustryname
        0      000001  0.8690   000001                银行
        1      000002  0.7340   000002               房地产
        2      000008  0.0190   000008              机械设备
        3      000009  0.0690   000009                综合
        4      000012  0.0350   000012              建筑材料
    """
    latest = models.IndexComponent.objects.filter(secucode=index_code).aggregate(mdate=Max('date'))['mdate']
    ratio = models.IndexComponent.objects.filter(secucode=index_code, date=latest).values('stockcode', 'weight')
    ratio = pd.DataFrame(ratio)

    # sw分类
    sw = models.StockIndustrySW.objects.values('secucode', 'firstindustryname')
    sw = pd.DataFrame(sw)

    data = ratio.merge(sw, left_on='stockcode', right_on='secucode', how='left')
    data['weight'] /= 100
    return data


def fund_top_ten_scale(fund_code: str, scale=True):
    """基金前十大持仓占比100%化

    将基金前十大持仓再分配为100%，非主基金需要获取关联代码转为主基金
    Args:
        fund_code: 基金代码
        scale: 是否百分化，默认是

    Returns:
          secucode stockcode                            ratio
        0   110011    000858   0.1445318296483157738536874907
        1   110011    002304   0.1458673393678587327496661226
        2   110011    600009  0.06098827719246178958302418756
        3   110011    600763  0.09511797002522629470247811248
        4   110011    600519   0.1477964089627541178216352575
        5   110011    002032  0.06262056684968096156699807093
        6   110011    000568   0.1446802196171538803976851165
        7   110011    600066  0.06069149725478557649502893604
        8   110011    600161  0.05905920759756640451105505268
        9   110011    002044  0.07864668348419646831874165306

    """
    try:
        associate = models.FundAssociate.objects.get(relate=fund_code).secucode
    except models.FundAssociate.DoesNotExist:
        associate = fund_code
    except models.FundAssociate.MultipleObjectsReturned:
        associate = models.FundAssociate.objects.get(relate=fund_code, define=24).secucode
    latest = models.FundHoldingStock.objects.filter(secucode=associate).aggregate(mdate=Max('date'))['mdate']
    holding = models.FundHoldingStock.objects.filter(
        secucode=associate, date=latest).values('secucode', 'stockcode', 'stockname', 'ratio')
    if not holding:
        return
    holding = pd.DataFrame(holding)
    if scale:
        holding['ratio'] = holding['ratio'] / holding['ratio'].sum()
    holding['secucode'] = fund_code
    return holding


def holding_etf_in_exchange(port_code, date) -> dict:
    """
    组合持有场内基金及占比
    Args:
        port_code: 证券代码
        date: 指定日期
    """
    holding = models.Holding.objects.filter(
        port_code=port_code, date=date, trade_market__in=(1, 2), mkt_cap__gt=0).values('secucode', 'mkt_cap')
    na = models.Balance.objects.get(port_code=port_code, date=date).net_asset
    holding = {x['secucode']: x['mkt_cap'] / na for x in holding}
    return holding
