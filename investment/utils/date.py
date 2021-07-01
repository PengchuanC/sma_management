import datetime
from typing import Any, List
from itertools import groupby


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
