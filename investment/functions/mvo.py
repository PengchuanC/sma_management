"""
mvo
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-09-07
@desc: rolling mean variance optimize
"""
import pandas as pd
import numpy as np

from itertools import groupby
from typing import List
from dateutil import relativedelta
from scipy.optimize import minimize

from investment.models import IndexQuote


class Configs(object):
    window = 3
    min = 0
    max = 0.3
    risk_free = 0.015
    start = None
    end = None
    indexes = []
    bounds = {}

    def __init__(self, indexes: List[str], **kwargs):
        """需要给定指数列表indexes以及指数优化的上下限"""
        self.indexes = indexes
        for k, v in kwargs.items():
            if v:
                setattr(self, k, v)
        for index in self.indexes:
            if index in self.bounds:
                continue
            self.bounds[index] = (self.min, self.max)

    def close_price(self):
        if self.start and self.end:
            start = self.start + relativedelta.relativedelta(years=-self.window - 1)
            end = self.end
        else:
            end: datetime.date = IndexQuote.objects.last().date
            # -2*self.window 是为了保证窗口可滚动
            start = end + relativedelta.relativedelta(years= -self.window - self.window - 1)
        close = IndexQuote.objects.filter(secucode__in=self.indexes, date__range=(start, end))
        return close

    def prepare(self):
        data = self.close_price()
        data = [{'secucode': x.secucode.secucode, 'change': x.change / 100, 'date': x.date} for x in data]
        data = pd.DataFrame(data)
        data = data.drop_duplicates(['secucode', 'date'])
        data.change = data.change.astype('float')
        data = data.pivot(index='date', columns='secucode', values='change')
        data = data[self.indexes]
        data = data.dropna(how='any')
        return data

    def rolling_mean_and_cov(self):
        data: pd.DataFrame = self.prepare()
        mean = ( 1 + data.rolling(window=self.window * 250).mean().dropna())**250 - 1
        cov = data.rolling(window=self.window * 250).cov().dropna() * 250
        return mean, cov


class Optimize(Configs):
    _return = None
    _cov = None

    def __init__(self, indexes: List[str], **kwargs):
        super().__init__(indexes, **kwargs)

    def constraint(self, weight):
        """约束条件，风险必须小于给定的值"""
        var = np.dot(weight.T, np.dot(self._cov.values, weight))
        return np.sqrt(var)

    def objective(self, weight):
        """指定风险，收益最大"""
        return - sum(weight * self._return)

    def optimize(self, risks: List, smooth=True):
        mean, cov = self.rolling_mean_and_cov()
        index = mean.index
        # 仅保留月底
        index =  [(x, x.strftime('%Y%m')) for x in index]
        index = sorted(index, key=lambda x: x[0])
        index = groupby(index, key=lambda x: x[1])
        index = [max(y[0] for y in x[1]) for x in index]
        bounds = [self.bounds.get(x) for x in self.indexes]
        x_array = np.array([1 / len(self.indexes) for _ in self.indexes])
        constraints = (
            {'type': 'eq', 'fun': lambda x: sum(x) - 1}, {'type': 'ineq', 'fun': lambda x: risk - self.constraint(x)}
        ) or None
        ret = []
        for risk in risks:
            r = []
            for i in  index:
                self._return = mean.loc[i]
                self._cov = cov.loc[i]
                opt = minimize(self.objective, x0=x_array, constraints=constraints, bounds=bounds)
                if opt.success:
                    _ret = [i] + [x for x in opt.x]
                    r.append(_ret)
            data = pd.DataFrame(r)
            data.columns = ['date'] + self.indexes
            if smooth:
                data = data.set_index('date')
                data = data.rolling(window=self.window*12).mean().dropna()
                data = round(data, 4)
                data = data.reset_index()
            data = data.to_dict(orient='records')
            ret.append({'risk': risk, 'data': data})
        return  ret
