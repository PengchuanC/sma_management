"""
to_database
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-09-08
@desc:
"""
from shu import models
from shu.collect import export
from shu.configs import tables, mapping


def commit_portfolio():
    """组合基本信息表"""
    data = export('组合信息表')
    for d in data:
        if not models.Portfolio.objects.filter(**d).exists():
            models.Portfolio(**d).save()


def commit_other(name):
    table = tables.get(name)
    m = mapping.get(table)
    data = export(name)
    last = m.objects.last()
    if last:
        date = last.date
        data = {x: y for x, y in data.items() if x > date}
    for date, dat in data.items():
        ret = []
        for row in dat:
            for r in row:
                ret.append(m(**r))
        m.objects.bulk_create(ret)


def run():
    for name in tables:
        if name == '组合信息表':
            commit_portfolio()
        else:
            commit_other(name)


if __name__ == '__main__':
    run()
