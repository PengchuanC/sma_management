"""
index
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-11-09
@desc: 同步基金数据
"""

import datetime

from django.db.models import Max
from threading import Thread, Lock
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from typing import List, Union, Optional
from sql import models
from sql.sql_templates import funds as template
from sql.utils import read_oracle, render
from sql.progress import progressbar


__all__ = ('commit_funds', 'commit_fund_associate', 'commit_fund_data', 'commit_fund_asset_allocate')


model_mapping = {
    models.FundPrice: template.acc_nav,
    models.FundAdjPrice: template.adj_nav
}


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
        fund = models.Funds.objects.get(secucode=row.secucode)
        models.FundAssociate.objects.update_or_create(secucode=fund, defaults={'relate': row.relate})


def commit_fund_asset_allocate():
    """更新基金资产配置比例"""
    sql = template.fund_allocate
    data = read_oracle(sql)
    data = data.fillna(0)
    codes = models.Funds.objects.filter(secucode__in=list(data.secucode)).all()
    codes = {x.secucode: x for x in codes}
    data = data.to_dict(orient='records')
    executor = ThreadPoolExecutor(max_workers=16)

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


class ExecuteCommit(object):
    def __init__(self, model, sql, fund, date: Optional[datetime.date] = None):
        self.m = model
        self.s = sql
        self.f = fund
        self.d = date

    def run(self):
        if not self.d:
            self.d = datetime.date(2010, 1, 1)
        date = self.d.strftime('%Y-%m-%d')
        sql = render(self.s, '<code>', self.f)
        sql = render(sql, '<date>', date)
        quote = read_oracle(sql)
        if quote.empty:
            return
        data = []
        for _, q in quote.iterrows():
            if 'secucode' in q.index:
                q.secucode = models.Funds.objects.get(secucode=q.secucode)
            data.append(self.m(**q))
        self.m.objects.bulk_create(data)


class Task(Thread):
    def __init__(self, target: List[ExecuteCommit], lock: Lock):
        super().__init__()
        self.t = target
        self.lk = lock
        self.length = len(target)

    def run(self):
        while True:
            self.lk.acquire()
            if not self.t:
                self.lk.release()
                break
            t = self.t.pop()
            self.lk.release()
            progressbar(self.length - len(self.t), self.length)
            try:
                t.run()
            except Exception as e:
                print(e)


class FundCommitFactory(object):
    """根据数据model创建任务"""
    model_mapping = model_mapping
    m = None
    dates = {}

    def __init__(self):
        self.funds = get_funds()

    def set_model(self, model: Union[models.FundPrice, models.FundAdjPrice, models.FundHoldingStock]):
        self.m = model
        self.dates = get_fund_last_update_date(model)

    def generate_task(self):
        tasks = []
        for fund in self.funds:
            date = self.dates.get(fund)
            sql = self.model_mapping.get(self.m)
            e = ExecuteCommit(self.m, sql, fund, date)
            tasks.append(e)
        return tasks


def commit_in_threading(task: List[ExecuteCommit], thread=16):
    """多线程同步数据"""
    threads = []
    lock = Lock()
    for i in range(thread):
        t = Task(task, lock)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()


def commit_fund_data():
    factory = FundCommitFactory()
    m: Union[models.FundPrice, models.FundAdjPrice, models.FundHoldingStock]
    for m in model_mapping.keys():
        print(m)
        factory.set_model(m)
        tasks = factory.generate_task()
        commit_in_threading(tasks)


if __name__ == '__main__':
    commit_fund_asset_allocate()
