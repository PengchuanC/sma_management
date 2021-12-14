"""
from_sma
~~~~~~~~
从sma客户服务系统导入组合数据
第一版采用导出excel文件再读取的方式，性能消耗过大
因此第二版采用rpc服务读取数据，保存到另一个数据库
"""
import datetime

from django.db import transaction as db_transaction
from django.db import close_old_connections

from services.client import Client
from shu import models
from sma_management.settings import RpcProxyHost


client = Client(RpcProxyHost)


def update_portfolio():
    for p in client.sma_portfolio():
        try:
            portfolio = models.Portfolio.objects.get(port_code=p.port_code)
            for attr in (
                    'manager', 'init_money', 'purchase_fee', 'redemption_fee', 'base', 'describe', 'settlemented', 't_n'
            ):
                setattr(portfolio, attr, getattr(p, attr))
            portfolio.save()
        except models.Portfolio.DoesNotExist:
            continue


def update_portfolio_expanded():
    for p in client.sma_portfolio_expanded():
        portfolio = models.Portfolio.objects.get(port_code=p.port_code)
        models.PortfolioExpanded.objects.update_or_create(
            port_code=portfolio, defaults={'o32': p.o32, 'valuation': p.valuation}
        )


def portfolio_instance(port_code):
    portfolio = models.Portfolio.objects.get(port_code=port_code)
    return portfolio


def launch_date(port_code):
    """组合成立日期"""
    portfolio = models.Portfolio.objects.get(port_code=port_code)
    date = portfolio.launch_date
    return date.date()


def latest_update_date(model, port_code: str):
    """最后更新日期"""
    exist = model.objects.filter(port_code=port_code).exists()
    if not exist:
        last = launch_date(port_code) - datetime.timedelta(days=1)
    else:
        last = model.objects.filter(port_code=port_code).latest('date')
        last = last.date
    date = last.strftime('%Y-%m-%d')
    return date


def balance(portfolio: models.Portfolio):
    port_code = portfolio.port_code
    date = latest_update_date(models.Balance, port_code)
    for d in client.sma_balance(port_code, date):
        m = dict(
            port_code=portfolio, asset=d.asset, debt=d.debt, net_asset=d.net_asset, shares=d.shares,
            unit_nav=d.unit_nav, acc_nav=d.acc_nav, savings=d.savings, fund_invest=d.fund_invest,
            liquidation=d.liquidation, value_added=d.value_added, profit_pay=d.profit_pay,
            cash_dividend=d.cash_dividend, security_deposit=d.security_deposit, date=d.date
        )
        models.Balance.objects.update_or_create(port_code=portfolio, date=d.date, defaults=m)


def balance_expanded(portfolio: models.Portfolio):
    port_code = portfolio.port_code
    date = latest_update_date(models.BalanceExpanded, port_code)
    for d in client.sma_balance_expanded(port_code, date):
        m = dict(
            dividend_rec=d.dividend_rec, interest_rec=d.interest_rec, purchase_rec=d.purchase_rec,
            redemption_pay=d.redemption_pay, redemption_fee_pay=d.redemption_fee_pay, management_pay=d.management_pay,
            custodian_pay=d.custodian_pay, withholding_pay=d.withholding_pay, interest_pay=d.interest_pay
        )
        models.BalanceExpanded.objects.update_or_create(port_code=portfolio, date=d.date, defaults=m)


def income(portfolio: models.Portfolio):
    port_code = portfolio.port_code
    date = latest_update_date(models.Income, port_code)
    for d in client.sma_income_portfolio(port_code, date):
        m = dict(
            port_code=portfolio, unit_nav=d.unit_nav, net_asset=d.net_asset, change=d.change, change_pct=d.change_pct,
            date=d.date
        )
        models.Income.objects.update_or_create(port_code=portfolio, date=d.date, defaults=m)


def income_asset(portfolio: models.Portfolio):
    port_code = portfolio.port_code
    date = latest_update_date(models.IncomeAsset, port_code)
    for d in client.sma_income_asset(port_code, date):
        m = dict(
            port_code=portfolio, total_profit=d.total_profit, equity=d.equity, bond=d.bond, alter=d.alter,
            money=d.money, date=d.date
        )
        models.IncomeAsset.objects.update_or_create(port_code=portfolio, date=d.date, defaults=m)


def holding(portfolio: models.Portfolio):
    port_code = portfolio.port_code
    date = latest_update_date(models.Holding, port_code)
    for d in client.sma_holding(port_code, date):
        m = dict(
            port_code=portfolio, secucode=d.secucode, holding_value=d.holding_value, mkt_cap=d.mkt_cap,
            current_cost=d.current_cost, total_cost=d.total_cost, fee=d.fee, flow_profit=d.flow_profit,
            total_profit=d.total_profit, dividend=d.dividend, total_dividend=d.total_dividend, category=d.category,
            trade_market=d.trade_market, date=d.date
        )
        models.Holding.objects.update_or_create(port_code=portfolio, secucode=d.secucode, date=d.date, defaults=m)


def transaction(portfolio: models.Portfolio):
    port_code = portfolio.port_code
    date = latest_update_date(models.Transactions, port_code)
    ret = []
    for d in client.sma_transaction(port_code, date):
        m = models.Transactions(
            port_code=portfolio, secucode=d.secucode, amount=d.amount, balance=d.balance, order_price=d.order_price,
            order_value=d.order_value, deal_value=d.deal_value, fee=d.fee, operation_amount=d.operation_amount,
            operation=d.operation, subject_name=d.subject_name, date=d.date
        )
        ret.append(m)
    models.Transactions.objects.bulk_create(ret)


def detail_fee(portfolio: models.Portfolio):
    port_code = portfolio.port_code
    date = latest_update_date(models.DetailFee, port_code)
    for d in client.sma_detail_fee(port_code, date):
        m = dict(
            port_code=portfolio, management=d.management, custodian=d.custodian, audit=d.audit, interest=d.interest,
            interest_tax=d.interest_tax, date=d.date
        )
        models.DetailFee.objects.update_or_create(port_code=portfolio, date=d.date, defaults=m)


def benchmark(portfolio: models.Portfolio):
    port_code = portfolio.port_code
    date = latest_update_date(models.ValuationBenchmark, port_code)
    for d in client.sma_benchmark(port_code, date):
        m = dict(port_code=portfolio, unit_nav=d.unit_nav, date=d.date)
        models.ValuationBenchmark.objects.update_or_create(port_code=portfolio, date=d.date, defaults=m)


def interest_tax(portfolio: models.Portfolio):
    port_code = portfolio.port_code
    date = latest_update_date(models.InterestTax, port_code)
    for d in client.sma_interest_tax(port_code, date):
        m = dict(port_code=portfolio, secucode=d.secucode, tax=d.tax, date=d.date)
        models.InterestTax.objects.update_or_create(
            port_code=portfolio, secucode=d.secucode, date=d.date, defaults=m
        )


def security():
    for d in client.sma_security():
        default = {'secuname': d.secuname, 'category': d.category, 'category_code': d.category_code}
        models.Security.objects.update_or_create(secucode=d.secucode, defaults=default)


def security_quote():
    try:
        max_id = models.SecurityPrice.objects.latest('auto_date')
        max_id = max_id.auto_date
    except models.SecurityPrice.DoesNotExist:
        max_id = datetime.date(2020, 1, 1)
    for d in client.sma_security_quote(max_id.strftime('%Y-%m-%d')):
        default = {
            'secucode_id': d.secucode, 'date': d.date, 'auto_date': d.auto_date, 'price': d.price, 'note': d.note,
            'o32': d.o32
        }
        models.SecurityPrice.objects.update_or_create(id=d.id, defaults=default)


def update_sma():
    close_old_connections()
    with db_transaction.atomic():
        update_portfolio()
        security()
        whole = list(models.Portfolio.objects.filter(settlemented=0))
        for portfolio in whole:
            update_portfolio_expanded()
            balance(portfolio)
            balance_expanded(portfolio)
            income(portfolio)
            income_asset(portfolio)
            holding(portfolio)
            transaction(portfolio)
            detail_fee(portfolio)
            benchmark(portfolio)
            # interest_tax(portfolio)
            security_quote()


def commit_sma():
    """从客户服务系统更新sma数据"""
    update_sma()


__all__ = ('commit_sma',)


if __name__ == '__main__':
    commit_sma()
