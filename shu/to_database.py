"""
to_database
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-09-08
@desc:
"""
from django.db.transaction import atomic
from django.db.models import Max

from shu.collect import export
from shu.configs import tables, mapping
from sql.progress import progressbar

from shu.sma_export.parse_configs import special_table
from investment.models import Funds, Portfolio


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
    print(name)
    table = tables.get(name)
    m = mapping.get(table)
    data = export(name)
    portfolios = Portfolio.objects.filter(valid=True).all()
    portfolios = [x.port_code for x in portfolios]
    portfolios = m.objects.filter(port_code__in=portfolios).values('port_code').annotate(mdate=Max('date'))
    date_mapping = {x['port_code']: x['mdate'] for x in portfolios}
    min_date = min(date_mapping.values())
    with atomic():
        data = {x: y for x, y in data.items() if x > min_date}
        for date, dat in data.items():
            ret = []
            for row in dat:
                for r in row:
                    date = date_mapping.get(r['port_code_id'])
                    if r['date'] <= date:
                        continue
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
