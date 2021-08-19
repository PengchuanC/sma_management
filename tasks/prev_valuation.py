import datetime

import pandas as pd
from pandas import DataFrame

from tasks import models
from investment.utils.holding import fund_holding_stock, holding_etf_in_exchange
from investment.views import FundHoldingView
from investment.views.prev_valuation import PreValuationConsumer
from investment.utils.holding_v2 import asset_type_penetrate, portfolio_holding_security


def pre_valuation():
    portfolios = models.Portfolio.objects.filter(settlemented=0).all()
    for portfolio in portfolios:
        try:
            port_code = portfolio.port_code
            try:
                date = models.PreValuedNav.objects.filter(port_code=port_code).latest('date').date
            except models.PreValuedNav.DoesNotExist:
                date = datetime.date(2020, 1, 1)
            dates = models.Balance.objects.filter(port_code=port_code, date__gte=date).values('date').distinct()
            dates = sorted([x['date'] for x in dates])
            after = models.TradingDays.objects.filter(date__range=(dates[-1], datetime.date.today())).values('date')
            after = sorted([x['date'] for x in after])
            for date in set(dates+after):
                try:
                    r = _pre_valuation_gil(port_code, date)
                    if not r:
                        continue
                    models.PreValuedNav.objects.update_or_create(port_code=portfolio, date=r['date'], defaults=r)
                except AttributeError as e:
                    raise e
        except Exception as e:
            raise e


def _pre_valuation(port_code: str):
    """获取组合预估值"""
    date = models.Balance.objects.filter(port_code=port_code).last().date
    holding = fund_holding_stock(port_code, date)
    ret = PreValuationConsumer.calc(holding)[0]
    return {'date': datetime.date.today(), 'value': ret['value']}


def _pre_valuation_gil(port_code: str, date: datetime.date):
    """预估组合当日涨跌幅，利用聚源数据而非爬虫数据"""
    v_date = models.Balance.objects.filter(port_code=port_code, date__lte=date).last().date
    holding = portfolio_holding_security(port_code, v_date)
    holding = pd.Series(holding, dtype=float)
    # 获取股票涨跌幅
    stocks = list(holding.index)
    price = models.StockDailyQuote.objects.filter(
        secucode__in=stocks, date=date).values('secucode', 'closeprice', 'prevcloseprice')
    price = DataFrame(price)
    if price.empty:
        return
    price['change'] = price['closeprice'] / price['prevcloseprice'] - 1
    price = price[['secucode', 'change']]
    price = price.dropna().set_index('secucode')['change'].astype(float)
    change = (holding * price).sum()
    return {'date': date, 'value': change}


if __name__ == '__main__':
    # _pre_valuation_gil('PFF005', datetime.date(2021, 8, 18))
    pre_valuation()
