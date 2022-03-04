import datetime

import numpy as np
import cvxopt as opt

from sql.preprocess.dataset import portfolio_nav, data_for_rbsm
from sql import models


def optimize(x: np.array, y: np.array):
    """优化求解"""
    length = len(x.T)

    opt.solvers.options['show_progress'] = False
    opt.solvers.options['abstol'] = 1e-10

    p = opt.matrix(np.dot(x.T, x))
    q = -opt.matrix(np.dot(x.T, y))
    g = opt.matrix(-np.eye(length))
    h = opt.matrix([0.]*length)
    a = opt.matrix([1.]*length, (1, length))
    b = opt.matrix(1.)

    model = opt.solvers.qp(P=p, q=q, G=g, h=h, A=a, b=b)

    ret = model.get("x")
    return ret


def optimize_and_r(x, y):
    """计算R方
    R^2 = 1 - Σ(y - y_hat)^2/Σ(y - y_mean)^2
    """
    coef = optimize(x, y)
    y_hat = np.dot(x, coef)

    r = (1 - sum((y - y_hat)**2)/sum((y - y.mean())**2))[0]
    return coef, r


def style_of_one_day(port_code: str, date: datetime.date):
    nav = portfolio_nav(port_code=port_code, date=date)
    if nav.empty:
        return
    start = nav.index[0]
    data = data_for_rbsm(start, date)
    data = data[data.index.isin(nav.index)]
    x = data.pct_change().dropna().values
    y = nav.pct_change().dropna().values
    coef, r = optimize_and_r(x, y)
    r = round(r, 4)
    ret = [round(x, 4) for x in coef]
    ret.extend([r, date, port_code])
    col = ['large_growth', 'large_value', 'mid_growth', 'mid_value', 'small_growth',
           'small_value', 'bond', 'r_square', 'date', 'port_code']
    ret = dict(zip(col, ret))
    return ret


def commit_style():
    port = models.Portfolio.objects.all()
    for p in port:
        port_code = p.port_code
        date = models.Valuation.objects.filter(port_code=port_code).values('date')
        last = models.PortfolioStyle.objects.filter(port_code=port_code).last()
        l: datetime.date = datetime.date(2020, 1, 1)
        if last:
            l = last.date
        date = [x['date'] for x in date if x['date'] > l]
        for d in date:
            ret = style_of_one_day(port_code, d)
            if ret:
                ret.pop('port_code')
                models.PortfolioStyle.objects.update_or_create(port_code=p, date=d, defaults=ret)


if __name__ == '__main__':
    commit_style()
