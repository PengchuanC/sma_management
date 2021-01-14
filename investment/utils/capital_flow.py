import datetime
from typing import List

import pandas as pd

from investment import models


def sw_categories() -> List[str]:
    """获取申万全部行业指数

    Returns:
        申万行业指数名称

    """
    categories = models.StockIndustrySW.objects.values_list('firstindustryname').distinct()
    categories = [x[0] for x in categories]
    return categories


def stocks_of_target_category(category: str) -> List[str]:
    """指定行业的成分股

    Args:
        category: 行业名称

    Returns:
        成分股代码
    """
    stocks = models.StockIndustrySW.objects.filter(firstindustryname=category).values_list('secucode').distinct()
    stocks = [x[0] for x in stocks if any(x)]
    return stocks


def category_capital_flow(category: str, date: datetime.date):
    """行业资金净流量

    Args:
        category: 行业名称
        date: 起始日期

    Returns:
        行业资金净流量
    """
    stocks = stocks_of_target_category(category=category)
    flow = models.CapitalFlow.objects.filter(secucode__in=stocks, date__gte=date).values('date', 'netvalue')
    flow: pd.DataFrame = pd.DataFrame(flow)
    flow = flow.groupby('date').sum()
    flow['MA3'] = flow['netvalue'].rolling(3 + 1).mean()
    flow['MA5'] = flow['netvalue'].rolling(5 + 1).mean()
    flow['MA10'] = flow['netvalue'].rolling(10 + 1).mean()
    flow['SIGMA5'] = flow['netvalue'].rolling(5 + 1).std()*0.3
    flow['MA5_HIGH'] = flow['MA5'] + flow['SIGMA5']
    flow['MA5_LOW'] = flow['MA5'] - flow['SIGMA5']
    flow = flow.dropna(how='any')
    flow['date'] = flow.index
    return flow


def index_code_by_name(category: str):
    """根据行业简称获取行业指数代码

    Args:
        category: 行业名称

    Returns:
        指数代码

    """
    bi = models.IndexBasicInfo.objects.filter(secuabbr__like=f'%{category}%').last()
    return bi.secucode


if __name__ == '__main__':
    sw_categories()
