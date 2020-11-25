"""
to_database
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-09-08
@desc:
"""
from shu.collect import export
from shu.configs import tables, mapping
from sql.progress import progressbar

from shu.sma_export.parse_configs import special_table
from investment.models import Funds


def commit_portfolio(name):
    """组合基本信息表"""
    table = tables.get(name)
    m = mapping.get(table)
    data = export(name)
    for d in data:
        if 'port_code' in d:
            m.objects.update_or_create(port_code=d['port_code'], defaults=d)
        if 'secucode_id' in d and 'fundtype' in d:
            f = Funds.objects.filter(secucode=d['secucode_id']).last()
            if f:
                m.objects.update_or_create(secucode=f, defaults=d)


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
        if name in special_table:
            commit_portfolio(name)
        else:
            commit_other(name)
        progressbar(i, len(tables))


if __name__ == '__main__':
    run()
