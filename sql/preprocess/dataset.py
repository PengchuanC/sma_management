import datetime
import pandas as pd

from sql import models


style_index = ['399372', '399373', '399374', '399375', '399376', '399377', 'Y00001']


def data_for_rbsm(start: datetime.date, end: datetime.date):
    """用于风格分析的指数数据"""
    data = models.IndexQuote.objects.filter(
        secucode__in=style_index, date__gte=start, date__lte=end
    ).order_by('date').values('secucode', 'date', 'close')
    data = pd.DataFrame(data)
    data['close'] = data['close'].astype('float')
    data = data.pivot_table(values='close', index='date', columns='secucode')
    data = data.astype('float')
    return data


def portfolio_nav(port_code: str, date: datetime.date, length=20):
    """获取组合累计单位净值"""
    nav = models.Balance.objects.filter(port_code=port_code, date__lte=date).order_by('date').values('date', 'acc_nav')
    nav_length = len(nav)
    if nav_length <= length:
        return pd.DataFrame()
    nav = nav[nav_length-length-1:]
    data = pd.DataFrame(nav).set_index('date')
    data = data.astype('float')
    return data
