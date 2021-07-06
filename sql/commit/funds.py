"""
index
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-11-09
@desc: 同步基金数据
"""

import datetime

from django.db.models import Max
from itertools import groupby
import pandas as pd
from typing import List, Dict
from sql import models
from sql.sql_templates import funds as template
from sql.utils import read_oracle, render, latest_update_date, commit_by_chunk, replace_fund_instance


__all__ = (
    'commit_funds', 'commit_fund_associate', 'commit_fund_adj_nav', 'commit_fund_acc_nav', 'commit_fund_asset_allocate'
)


ThisYear = datetime.date(datetime.date.today().year, 1, 1)


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
    local = models.Funds.objects.all()
    local = {x.secucode: x for x in local}
    add = []
    for f in funds_jy:
        local_ = local.get(f['secucode'])
        if not local_:
            add.append(models.Funds(**f))
            continue
        if f['secuname'] == local_.secuname:
            continue
        local_.secuname = f['secuname']
        local_.save()
    models.Funds.objects.bulk_create(add)


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
    """更新基金资产配置比例
       @updated: 20210706
       @desc: 原有更新方式速度过慢，采用新的更新逻辑
    """
    sql = template.fund_allocate
    data = read_oracle(sql)
    data = data.fillna(0)
    latest = latest_update_date(models.FundAssetAllocate)
    data = data[data.agg(lambda x: x.date > latest.get(x.secucode, datetime.date(2020, 1, 1)), axis=1)]
    data = replace_fund_instance(data)
    commit_by_chunk(data, models.FundAssetAllocate)


def get_fund_last_update_date(model):
    dates = model.objects.values('secucode').annotate(mdate=Max('date'))
    dates = {x['secucode']: x['mdate'] for x in dates}
    return dates


def commit_fund_adj_nav():
    """
    同步基金复权单位净值
    Returns:
    """
    if not models.FundAdjPrice.objects.exists():
        sql = template.adj_nav_bulk
    else:
        sql = template.adj_nav
    data = read_oracle(sql)
    latest = latest_update_date(models.FundAdjPrice)
    data = data[data.agg(lambda x: x.date > latest.get(x.secucode, ThisYear), axis=1)]
    data = replace_fund_instance(data)
    commit_by_chunk(data, models.FundAdjPrice)


def commit_fund_acc_nav():
    """
    同步基金累计单位净值

    Returns:
    """
    if not models.FundPrice.objects.exists():
        sql = template.acc_nav_bulk
    else:
        sql = template.acc_nav
    data = read_oracle(sql)
    latest = latest_update_date(models.FundPrice)
    data = data[data.agg(lambda x: x.date > latest.get(x.secucode, ThisYear), axis=1)]
    data = replace_fund_instance(data)
    data = data.fillna(0)
    commit_by_chunk(data, models.FundPrice)


if __name__ == '__main__':
    commit_fund_acc_nav()
