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
from typing import List, Union, Optional
from sql import models
from sql.sql_templates import funds as template
from sql.utils import read_oracle, render
from sql.progress import progressbar


__all__ = ('commit_funds', 'commit_fund_data')


model_mapping = {
    models.FundPrice: template.acc_nav,
    models.FundAdjPrice: template.adj_nav,
    models.FundHoldingStock: template.fund_top_ten_stock
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
        print(m.Meta.db_table)
        factory.set_model(m)
        tasks = factory.generate_task()
        commit_in_threading(tasks)


if __name__ == '__main__':
    commit_fund_data()
