"""
capital
~~~~~~~
计算每日行业资金流入情况
"""
import datetime

import pandas as pd
from django.db.models import Max

from sql import models
from investment.utils.capital_flow import outlook


def commit_capital_flow():
    """
    同步资金流向数据
    Returns:

    """
    latest = models.IndustryCF.objects.values('secucode').annotate(mdate=Max('date'))
    latest = {x['secucode']: x['mdate'] for x in latest}
    data = outlook()
    data = pd.DataFrame(data)
    data = data[data.agg(lambda x: x.date > latest.get(x.secucode, datetime.date(2021, 1, 1)), axis=1)]
    data.columns = [x.lower() for x in data.columns]
    m = [models.IndustryCF(**x) for _, x in data.iterrows()]
    models.IndustryCF.objects.bulk_create(m)


if __name__ == '__main__':
    commit_capital_flow()
