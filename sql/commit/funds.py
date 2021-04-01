"""
index
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-11-09
@desc: 同步基金数据
"""

import datetime

from django.db.models import Max
from math import ceil
from itertools import groupby
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from typing import List, Dict
from sql import models
from sql.sql_templates import funds as template
from sql.utils import read_oracle, render


__all__ = ('commit_funds', 'commit_fund_associate', 'commit_fund_data', 'commit_fund_asset_allocate')


def get_funds():
    """获取本地数据库中的基金列表"""
    funds = models.Funds.objects.all()
    funds = [x.secucode for x in funds]
    return funds


def commit_funds():
    """增量更新基金列表"""
    sql = template.fund
    funds_jy = read_oracle(sql)
    funds_jy = funds_jy.to_dict(orient='records')
    for f in funds_jy:
        models.Funds.objects.update_or_create(secucode=f.pop('secucode'), defaults=f)


def commit_fund_associate():
    """更新基金代码关联表，主要针对ETF和LOF"""
    sql = template.fund_associate
    funds_jy = read_oracle(sql)
    for _, row in funds_jy.iterrows():
        exist = models.FundAssociate.objects.filter(secucode=row.secucode, relate=row.relate).all()
        if exist:
            continue
        fund = models.Funds.objects.filter(secucode=row.secucode).first()
        if not fund:
            continue
        models.FundAssociate.objects.update_or_create(relate=row.relate, secucode=fund, defaults={'define': row.define})


def commit_fund_asset_allocate():
    """更新基金资产配置比例"""
    sql = template.fund_allocate
    data = read_oracle(sql)
    data = data.fillna(0)
    codes = models.Funds.objects.filter(secucode__in=list(data.secucode)).all()
    codes = {x.secucode: x for x in codes}
    data = data.to_dict(orient='records')
    executor = ThreadPoolExecutor(max_workers=8)

    def target(r):
        if r['secucode'] in codes.keys():
            fund = codes.get(r.pop('secucode'))
            models.FundAssetAllocate.objects.update_or_create(
                secucode=fund, date=r['date'], defaults=r
            )

    tasks = []
    for row in data:
        ret = executor.submit(target, row)
        tasks.append(ret)
    wait(tasks, return_when=ALL_COMPLETED)


def get_fund_last_update_date(model):
    dates = model.objects.values('secucode').annotate(mdate=Max('date'))
    dates = {x['secucode']: x['mdate'] for x in dates}
    return dates


def chunk(array, size=1):
    """
    Example:

        >>> chunk([1, 2, 3, 4, 5], 2)
        [[1, 2], [3, 4], [5]]

    .. versionadded:: 1.1.0
    """
    chunks = int(ceil(len(array) / float(size)))
    return [array[i * size:(i + 1) * size] for i in range(chunks)]


class DataGetter(object):
    """数据获取

    如果当日数据出现遗漏，需要在下次同步时补足数据，因此将本地每只基金的最新同步日期分组，
    相同日期的分为一组，按组获取最新数据
    Attributes:
        model: 模型

    """

    model_mapping = {
        models.FundPrice: template.acc_nav_multi,
        models.FundAdjPrice: template.adj_nav_multi
    }

    dates: Dict[datetime.date, List[str]] = {}

    def __init__(self, model):
        self.m = model
        self._max_date_group()

    def _max_date_group(self):
        """每个最新同步日期下的基金列表

        Returns:
            {
                '2005-7-14': ['000001',...],
                ...,
                '2021-02-04': ['110011',...]
            }
        """
        max_dates = get_fund_last_update_date(self.m)
        sorted_dates = [(secucode, date) for secucode, date in max_dates.items()]
        sorted_dates = sorted(sorted_dates, key=lambda x: x[1], reverse=True)
        group_dates = groupby(sorted_dates, key=lambda x: x[1])
        group_dates = {x[0]: [y[0] for y in x[1]]for x in group_dates}
        recent = self._recent_launched_funds()
        date = datetime.date.today() - datetime.timedelta(days=30)
        if date in group_dates.keys():
            group_dates[date].extend(recent)
        else:
            group_dates[date] = recent
        self.dates = group_dates

    def _recent_launched_funds(self) -> List[str]:
        """部分新成立基金没有最大日期

        Returns:
            [001428, ...]
        """
        funds = models.Funds.objects.values('secucode').distinct()
        funds = [x['secucode'] for x in funds]
        funds2 = self.m.objects.values('secucode').distinct()
        funds2 = [x['secucode'] for x in funds2]
        funds = [x for x in funds if x not in funds2]
        return funds

    def get_data(self, date: datetime.date):
        """从远程获取增量数据

        Args:
            date: 本地最新更新日期

        Returns:

        """
        codes = self.dates.get(date)
        # oracle 单条in语句查询记录不允许超过1000条
        codes = chunk(codes, 999)
        data = []
        for code in codes:
            codes_str = "','".join(code)
            sql = self.model_mapping.get(self.m)
            sql = render(sql, '<code>', codes_str)
            sql = render(sql, '<date>', date.strftime('%Y-%m-%d'))
            d = read_oracle(sql)
            data.append(d)
        data = pd.concat(data, axis=0)
        return data

    def commit(self):
        """提交"""
        dates = self.dates
        funds = models.Funds.objects.all()
        funds = {x.secucode: x for x in funds}
        ret = []
        for date in dates:
            # 60日内无净值数据的，不视为净值遗漏，视为不再披露净值
            if date < datetime.date.today() - datetime.timedelta(days=60):
                continue
            data = self.get_data(date)
            data.secucode = data.secucode.apply(lambda x: funds.get(x))
            data = data.where(data.notnull(), None)
            for idx, r in data.iterrows():
                r = self.m(**r)
                ret.append(r)
        self.m.objects.bulk_create(ret)


def commit_fund_data():
    """同步基金净值数据

    2021.02.04修改为批量同步

    Returns:

    """
    p = ThreadPoolExecutor(max_workers=2)
    tasks = []
    for m in DataGetter.model_mapping.keys():
        dg = DataGetter(m)
        tasks.append(p.submit(dg.commit))
    wait(tasks, return_when=ALL_COMPLETED)


if __name__ == '__main__':
    commit_fund_asset_allocate()
