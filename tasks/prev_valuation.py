import datetime

from tasks import models
from investment.utils.holding import fund_holding_stock
from investment.views import FundHoldingView
from investment.views.prev_valuation import PreValuationConsumer


def pre_valuation():
    portfolios = models.Portfolio.objects.filter(valid=True).all()
    for portfolio in portfolios:
        try:
            ret = _pre_valuation(portfolio.port_code)
            models.PreValuedNav.objects.update_or_create(port_code=portfolio, date=ret['date'], defaults=ret)
        except Exception as e:
            print(e)


def _pre_valuation(port_code: str):
    """获取组合预估值"""
    date = models.Balance.objects.filter(port_code=port_code).last().date
    ratio = FundHoldingView.asset_allocate(port_code, date)
    stock = ratio['stock']
    holding = fund_holding_stock(port_code, date)
    equity = float(holding.ratio.sum()) / stock
    ret = PreValuationConsumer.calc(holding, equity)[0]
    return {'date': datetime.date.today(), 'value': ret['value']}
