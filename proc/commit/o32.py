import datetime

from proc.configs import FileStoragePath
from proc.read.collect import collect_files
from proc.read.o32 import read_holding, read_transaction
from proc.commit.valuation import whole_cta_fof, latest_update_date
from proc import models


def commit_holding():
    """同步持仓数据"""
    whole = whole_cta_fof()
    for fof in whole:
        commit_single(fof, models.Holding)


def commit_transaction():
    """同步持仓数据"""
    whole = whole_cta_fof()
    for fof in whole:
        commit_single(fof, models.Transactions)


def latest_update_date_o32(portfolio: models.Portfolio, model):
    """获取持仓或者流水的最新更新日期，没有数据则使用成立日前一日"""
    last = model.objects.filter(port_code=portfolio.port_code)
    if last.exists():
        return last.latest('date').date
    info = models.Portfolio.objects.get(port_code=portfolio.port_code)
    return info.launch_date.date() - datetime.timedelta(days=1)


def commit_single(portfolio: models.Portfolio, model):
    """同步单只组合持仓数据"""
    if model == models.Holding:
        key = 'chicang'
        reader = read_holding
    elif model == models.Transactions:
        key = 'liushui'
        reader = read_transaction
    else:
        return
    vfs = collect_files(FileStoragePath.o32, 'xls', key)
    begin = latest_update_date_o32(portfolio, model)
    # o32会比估值表提前更新，但并不需要提前
    end = latest_update_date(portfolio)
    o32_code = models.PortfolioExpanded.objects.get(
        port_code=portfolio.port_code).o32_code
    vfs = [x for x in vfs if all({x.date > begin, x.date <= end})]
    rows = []
    for vf in vfs:
        data = reader(vf)
        data = data[data.port_code == o32_code]
        for _, row in data.iterrows():
            m = model(**{**row, **{'port_code': portfolio, 'date': vf.date}})
            rows.append(m)
    model.objects.bulk_create(rows)


__all__ = ('commit_holding', 'commit_transaction')
