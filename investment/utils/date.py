import datetime
from typing import Any, List, Optional
from itertools import groupby

from asgiref.sync import sync_to_async

from investment import models


def latest_trading_day(m: Any):
    date = m.objects.latest().date
    return date


def quarter_end_in_date_series(dates: List[datetime.date]):
    """从时间序列中获取季度最后一日

    除季度最后一日外，还包含起止日期
    Args:
        dates: 日期序列

    Returns:

    """
    series = [((x.month - 1) // 3, x) for x in dates]
    series = groupby(series, lambda x: x[0])
    series = [max(x[1]) for x in series]
    series = [x[1] for x in series]
    return series


def nearest_tradingday_before_x(day: datetime.date):
    """指定日期的前一个交易日"""
    return models.TradingDays.objects.filter(date__lt=day).latest('date').date


async def last_tradingday_in_balance(port_code: str, date: Optional[datetime.date]):
    """估值表中最新交易日，若无交易日，则取组合成立日"""
    if date is None:
        date = datetime.date.today()
    exists = await sync_to_async(models.Balance.objects.filter)(port_code=port_code, date__lte=date)
    exist = await sync_to_async(exists.exists)()
    if not exist:
        launch = await sync_to_async(models.Portfolio.objects.get)(port_code=port_code)
        date = launch.launch_date
        return date
    bl = await sync_to_async(exists.latest)('date')
    return bl.date
