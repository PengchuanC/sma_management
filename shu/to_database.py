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
from sql.progress import progressbar


def commit_portfolio():
    """组合基本信息表"""
    data = export('组合信息表')
    for d in data:
        models.Portfolio.objects.update_or_create(port_code=d['port_code'], defaults=d)


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
    for i, name in enumerate(tables):
        if name == '组合信息表':
            commit_portfolio()
        else:
            commit_other(name)
        progressbar(i, len(tables))


if __name__ == '__main__':
    run()
