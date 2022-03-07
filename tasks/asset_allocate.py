from tasks import models
from investment.views.analysis import FundHoldingView
from investment.utils.holding_v2 import asset_type_penetrate


def portfolio_asset_allocate():
    portfolios = models.Portfolio.objects.filter(settlemented=0).all()
    for portfolio in portfolios:
        ret = _portfolio_asset_allocate(portfolio)
        models.PortfolioAssetAllocate.objects.bulk_create(ret)


def _portfolio_asset_allocate(portfolio: models.Portfolio):
    last_update = models.PortfolioAssetAllocate.objects.filter(port_code=portfolio).last()
    if last_update:
        date = last_update.date
        dates = models.Valuation.objects.filter(date__gt=date, port_code=portfolio).values('date').order_by('date')
    else:
        dates = models.Valuation.objects.filter(port_code=portfolio).values('date').order_by('date')
    dates = [x['date'] for x in dates]
    ret = []
    for date in dates:
        try:
            allocate: dict = asset_type_penetrate(portfolio.port_code, date)
            names = ['equity', 'fix_income', 'alter', 'money', 'other']
            for idx, attr in enumerate(['equity', 'fix_income', 'alternative', 'monetary', 'other']):
                allocate[names[idx]] = allocate.pop(attr)
            allocate.update({'port_code': portfolio, 'date': date})
            if round(allocate['money'], 0) == 1:
                continue
            allocate: models.PortfolioAssetAllocate = models.PortfolioAssetAllocate(**allocate)
            ret.append(allocate)
        except Exception as e:
            print(e)
            continue
    return ret


if __name__ == '__main__':
    portfolio_asset_allocate()
