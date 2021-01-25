from tasks import models
from investment.views.analysis import FundHoldingView


def portfolio_asset_allocate():
    portfolios = models.Portfolio.objects.filter(valid=True).all()
    for portfolio in portfolios:
        ret = _portfolio_asset_allocate(portfolio)
        models.PortfolioAssetAllocate.objects.bulk_create(ret)


def _portfolio_asset_allocate(portfolio: models.Portfolio):
    last_update = models.PortfolioAssetAllocate.objects.filter(port_code=portfolio).last()
    if last_update:
        date = last_update.date
        dates = models.Balance.objects.filter(date__gt=date, port_code=portfolio).values('date').order_by('date')
    else:
        dates = models.Balance.objects.filter(port_code=portfolio).values('date').order_by('date')
    dates = [x['date'] for x in dates]
    ret = []
    for date in dates:
        try:
            allocate: dict = FundHoldingView.asset_allocate(portfolio.port_code, date=date)
            allocate.pop('fund')
            names = ['equity', 'fix_income', 'alter', 'money']
            for idx, attr in enumerate(['stock', 'bond', 'metals', 'monetary']):
                allocate[names[idx]] = allocate.pop(attr)
            allocate.update({'port_code': portfolio, 'date': date})
            allocate: models.PortfolioAssetAllocate = models.PortfolioAssetAllocate(**allocate)
            ret.append(allocate)
        except:
            continue
    return ret


if __name__ == '__main__':
    portfolio_asset_allocate()
