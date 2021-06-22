import datetime

import pandas as pd
from pandas import DataFrame

from tasks import models
from investment.utils.holding import fund_holding_stock, holding_etf_in_exchange
from investment.views import FundHoldingView
from investment.views.prev_valuation import PreValuationConsumer


def pre_valuation():
    portfolios = models.Portfolio.objects.filter(valid=True).all()
    for portfolio in portfolios:
        try:
            port_code = portfolio.port_code
            try:
                date = models.PreValuedNav.objects.filter(port_code=port_code).latest('date').date
            except models.PreValuedNav.DoesNotExist:
                date = datetime.date(2020, 1, 1)
            dates = models.Balance.objects.filter(port_code=port_code, date__gt=date).values('date').distinct()
            dates = sorted([x['date'] for x in dates])
            for date in dates+[datetime.date.today()]:
                try:
                    r = _pre_valuation_gil(port_code, date)
                    models.PreValuedNav.objects.update_or_create(port_code=portfolio, date=r['date'], defaults=r)
                except AttributeError:
                    pass
        except Exception as e:
            raise e


def _pre_valuation(port_code: str):
    """获取组合预估值"""
    date = models.Balance.objects.filter(port_code=port_code).last().date
    ratio = FundHoldingView.asset_allocate(port_code, date)
    stock = ratio['stock']
    holding = fund_holding_stock(port_code, date)
    equity = float(holding.ratio.sum()) / stock
    ret = PreValuationConsumer.calc(holding, equity)[0]
    return {'date': datetime.date.today(), 'value': ret['value']}


def _pre_valuation_gil(port_code: str, date: datetime.date):
    """预估组合当日涨跌幅，利用聚源数据而非爬虫数据"""
    date = models.Balance.objects.filter(port_code=port_code, date__lte=date).last().date
    ratio = FundHoldingView.asset_allocate(port_code, date)
    stock = ratio['stock']
    holding = fund_holding_stock(port_code, date, in_exchange=False)
    etf = holding_etf_in_exchange(port_code, date)
    etf_df = pd.DataFrame([{'stockcode': x, 'ratio': y} for x, y in etf.items()])
    # 计算前十大在权益持仓中的占比
    equity = float(holding.ratio.sum()) / float(stock)

    # 获取股票涨跌幅
    stocks = list(holding.stockcode)
    price = models.StockDailyQuote.objects.filter(
        secucode__in=stocks, date=date).values('secucode', 'closeprice', 'prevcloseprice')
    price_etf = models.FundQuote.objects.filter(
        secucode__in=list(etf.keys()), date=date).values('secucode', 'closeprice', 'prevcloseprice')
    price = [*price, *price_etf]
    price = DataFrame(price)
    price['change'] = price['closeprice'] / price['prevcloseprice'] - 1
    price = price[['secucode', 'change']]
    price = price.dropna()

    stock = holding.merge(price, left_on='stockcode', right_on='secucode', how='left')
    change_stock = float((stock['ratio'] * stock['change']).sum()) / equity
    if etf_df.empty:
        change_etf = 0
    else:
        etf = etf_df.merge(price, left_on='stockcode', right_on='secucode', how='left')
        change_etf = float((etf['ratio'].astype('float') * etf['change']).sum())
    change = change_etf + change_stock
    return {'date': date, 'value': change}


if __name__ == '__main__':
    pre_valuation()
