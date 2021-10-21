import datetime
import re
from typing import List, Dict
from decimal import Decimal

import pandas as pd
from numpy import round as npround
from django.db.models import Q

from investment import models


def sw_categories() -> List[Dict[str, str]]:
    """获取申万全部行业指数

    Returns:
        申万行业指数名称

    """
    categories = models.IndexBasicInfo.objects.filter(
        secucode__secucode__startswith='801'
    ).order_by('secucode').values('secucode', 'secuabbr')
    categories = [x for x in categories]
    return categories


def sw_first_categories() -> List[Dict[str, str]]:
    """
    获取申万全部一级行业名称
    Returns:
        申万一级行业名称
    """
    categories = models.IndexBasicInfo.objects.filter(
        secucode__secucode__regex=r"801\d{2}0"
    ).order_by('secucode').values('secucode', 'secuabbr')
    categories = [x for x in categories]
    return categories


def sw_second_categories(secucode: str) -> List[Dict[str, str]]:
    """
    获取指定申万一级行业的二级行业
    Args:
        secucode: 一级行业代码

    Returns:
        申万二级行业
    """
    categories = models.IndexBasicInfo.objects.filter(
        secucode__secucode__startswith=secucode[:5]
    ).exclude(
        secucode__secucode__endswith="0"
    ).order_by('secucode').values('secucode', 'secuabbr')
    categories = [x for x in categories]
    return categories


def stocks_of_target_category(category: str) -> List[str]:
    """指定行业的成分股

    Args:
        category: 行业代码

    Returns:
        成分股代码
    """
    name = models.IndexBasicInfo.objects.get(secucode=category).secuabbr
    name = re.sub('申万|申银万国', '', name)
    stocks = models.StockIndustrySW.objects.filter(
        Q(firstindustryname=name) | Q(secondindustryname=name)
    ).values_list('secucode').distinct()
    stocks = [x[0] for x in stocks if any(x)]
    return stocks


def category_capital_flow(category: str, date: datetime.date):
    """行业资金净流量

    Args:
        category: 行业代码
        date: 起始日期

    Returns:
        行业资金净流量
    """
    stocks = stocks_of_target_category(category=category)
    flow = models.CapitalFlow.objects.filter(secucode__in=stocks, date__gte=date).values('date', 'netvalue')
    flow: pd.DataFrame = pd.DataFrame(flow)
    flow.netvalue = flow.netvalue.astype(float)
    flow = flow.groupby('date').sum()
    flow = flow.reset_index()
    flow.date = flow.date.shift(-1)
    d = flow.iloc[-2, 0]
    last = models.TradingDays.objects.filter(date__gt=d).first().date
    flow.iloc[-1, 0] = last
    flow['netvalue'] /= 1e6
    flow['MA3'] = flow['netvalue'].rolling(3).mean()
    flow['MA5'] = flow['netvalue'].rolling(5).mean()
    flow['MA10'] = flow['netvalue'].rolling(10).mean()
    flow['SIGMA5'] = flow['netvalue'].rolling(5).std()*0.3
    flow['MA5_HIGH'] = flow['MA5'] + flow['SIGMA5']
    flow['MA5_LOW'] = flow['MA5'] - flow['SIGMA5']
    flow = npround(flow, 2)
    flow = flow.dropna(how='any')
    flow = flow.reset_index()
    return flow


def index_code_by_name(category: str):
    """根据行业简称获取行业指数代码

    Args:
        category: 行业名称

    Returns:
        指数代码

    """
    bi = models.IndexBasicInfo.objects.filter(secuabbr=f'申万{category}').last()
    return bi.secucode


def outlook():
    """
    申万一级行业流入流出概览

    Returns:

    """
    date = datetime.date.today()
    td = models.TradingDays.objects.filter(date__lte=date).order_by('-date')
    date = td[22].date
    categories = sw_categories()
    ret = []
    for category in categories:
        secucode = category['secucode']
        r = category_capital_flow(secucode, date)
        r = r.drop('index', axis=1)
        r = r.iloc[-1, :].to_dict()
        r['secucode'] = secucode
        r['secuabbr'] = category['secuabbr']
        ret.append(r)
    return ret


if __name__ == '__main__':
    sw_categories()
