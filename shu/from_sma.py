"""
from_sma
~~~~~~~~
从sma客户服务系统导入组合数据
第一版采用导出excel文件再读取的方式，性能消耗过大
因此第二版采用rpc服务读取数据，保存到另一个数据库
"""
import asyncio
import datetime

from asgiref.sync import sync_to_async

from shu.rpc_client import Client
from shu import models


client = Client()


async def update_portfolio():
    async for p in client.sma_portfolio():
        try:
            portfolio = await sync_to_async(models.Portfolio.objects.get)(port_code=p.port_code)
        except models.Portfolio.DoesNotExist:
            continue
        for attr in (
                'manager', 'init_money', 'purchase_fee', 'redemption_fee', 'base', 'describe', 'settlemented', 't_n'
        ):
            setattr(portfolio, attr, getattr(p, attr))
        await sync_to_async(portfolio.save)()


async def update_portfolio_expanded():
    async for p in client.sma_portfolio_expanded():
        portfolio = await sync_to_async(models.Portfolio.objects.get)(port_code=p.port_code_id)
        await sync_to_async(models.PortfolioExpanded.objects.update_or_create)(
            port_code=portfolio, defaults={'o32': p.o32, 'valuation': p.valuation}
        )


async def portfolio_instance(port_code):
    portfolio = await sync_to_async(models.Portfolio.objects.get)(port_code=port_code)
    return portfolio


async def launch_date(port_code):
    """组合成立日期"""
    portfolio = await sync_to_async(models.Portfolio.objects.get)(port_code=port_code)
    date = portfolio.launch_date
    return date.date()


async def latest_update_date(model, port_code: str):
    """最后更新日期"""
    exist = await sync_to_async(model.objects.filter(port_code=port_code).exists)()
    if not exist:
        last = await launch_date(port_code) - datetime.timedelta(days=1)
    else:
        last = await sync_to_async(model.objects.filter(port_code=port_code).latest)('date')
        last = last.date
    date = last.strftime('%Y-%m-%d')
    return date


async def balance(portfolio: models.Portfolio):
    port_code = portfolio.port_code
    date = await latest_update_date(models.Balance, port_code)
    ret = []
    async for d in client.sma_balance(port_code, date):
        m = models.Balance(
            port_code=portfolio, asset=d.asset, debt=d.debt, net_asset=d.net_asset, shares=d.shares,
            unit_nav=d.unit_nav, acc_nav=d.acc_nav, savings=d.savings, fund_invest=d.fund_invest,
            liquidation=d.liquidation, value_added=d.value_added, profit_pay=d.profit_pay,
            cash_dividend=d.cash_dividend, security_deposit=d.security_deposit, date=d.date
        )
        ret.append(m)
    await sync_to_async(models.Balance.objects.bulk_create)(ret)


async def balance_expanded(portfolio: models.Portfolio):
    port_code = portfolio.port_code
    date = await latest_update_date(models.BalanceExpanded, port_code)
    ret = []
    async for d in client.sma_balance_expanded(port_code, date):
        m = models.BalanceExpanded(
            port_code=portfolio, dividend_rec=d.dividend_rec, interest_rec=d.interest_rec, purchase_rec=d.purchase_rec,
            redemption_pay=d.redemption_pay, redemption_fee_pay=d.redemption_fee_pay, management_pay=d.management_pay,
            custodian_pay=d.custodian_pay, withholding_pay=d.withholding_pay, interest_pay=d.interest_pay, date=d.date
        )
        ret.append(m)
    await sync_to_async(models.BalanceExpanded.objects.bulk_create)(ret)


async def income(portfolio: models.Portfolio):
    port_code = portfolio.port_code
    date = await latest_update_date(models.Income, port_code)
    ret = []
    async for d in client.sma_income(port_code, date):
        m = models.Income(
            port_code=portfolio, unit_nav=d.unit_nav, net_asset=d.net_asset, change=d.change, change_pct=d.change_pct,
            date=d.date
        )
        ret.append(m)
    await sync_to_async(models.Income.objects.bulk_create)(ret)


async def income_asset(portfolio: models.Portfolio):
    port_code = portfolio.port_code
    date = await latest_update_date(models.IncomeAsset, port_code)
    ret = []
    async for d in client.sma_income_asset(port_code, date):
        m = models.IncomeAsset(
            port_code=portfolio, total_profit=d.total_profit, equity=d.equity, bond=d.bond, alter=d.alter,
            money=d.money, date=d.date
        )
        ret.append(m)
    await sync_to_async(models.IncomeAsset.objects.bulk_create)(ret)


async def holding(portfolio: models.Portfolio):
    port_code = portfolio.port_code
    date = await latest_update_date(models.Holding, port_code)
    ret = []
    async for d in client.sma_holding(port_code, date):
        m = models.Holding(
            port_code=portfolio, secucode=d.secucode, holding_value=d.holding_value, mkt_cap=d.mkt_cap,
            current_cost=d.current_cost, total_cost=d.total_cost, fee=d.fee, flow_profit=d.flow_profit,
            total_profit=d.total_profit, dividend=d.dividend, total_dividend=d.total_dividend, category=d.category,
            trade_market=d.trade_market, date=d.date
        )
        ret.append(m)
    await sync_to_async(models.Holding.objects.bulk_create)(ret)


async def transaction(portfolio: models.Portfolio):
    port_code = portfolio.port_code
    date = await latest_update_date(models.Transactions, port_code)
    ret = []
    async for d in client.sma_transaction(port_code, date):
        m = models.Transactions(
            port_code=portfolio, secucode=d.secucode, amount=d.amount, balance=d.balance, order_price=d.order_price,
            order_value=d.order_value, deal_value=d.deal_value, fee=d.fee, operation_amount=d.operation_amount,
            operation=d.operation, subject_name=d.subject_name, date=d.date
        )
        ret.append(m)
    await sync_to_async(models.Transactions.objects.bulk_create)(ret)


async def detail_fee(portfolio: models.Portfolio):
    port_code = portfolio.port_code
    date = await latest_update_date(models.DetailFee, port_code)
    ret = []
    async for d in client.sma_detail_fee(port_code, date):
        m = models.DetailFee(
            port_code=portfolio, management=d.management, custodian=d.custodian, audit=d.audit, interest=d.interest,
            interest_tax=d.interest_tax, date=d.date
        )
        ret.append(m)
    await sync_to_async(models.DetailFee.objects.bulk_create)(ret)


async def benchmark(portfolio: models.Portfolio):
    port_code = portfolio.port_code
    date = await latest_update_date(models.ValuationBenchmark, port_code)
    ret = []
    async for d in client.sma_benchmark(port_code, date):
        m = models.ValuationBenchmark(port_code=portfolio, unit_nav=d.unit_nav, date=d.date)
        ret.append(m)
    await sync_to_async(models.ValuationBenchmark.objects.bulk_create)(ret)


async def interest_tax(portfolio: models.Portfolio):
    port_code = portfolio.port_code
    date = await latest_update_date(models.InterestTax, port_code)
    ret = []
    async for d in client.sma_interest_tax(port_code, date):
        m = models.InterestTax(port_code=portfolio, secucode=d.secucode, tax=d.tax, date=d.date)
        ret.append(m)
    await sync_to_async(models.InterestTax.objects.bulk_create)(ret)


async def security():
    async for d in client.sma_security():
        default = {'secuname': d.secuname, 'category': d.category, 'category_code': d.category_code}
        await sync_to_async(models.Security.objects.update_or_create)(secucode=d.secucode, defaults=default)


async def security_quote():
    try:
        max_id = await sync_to_async(models.SecurityPrice.objects.latest)('id')
        max_id = max_id.id
    except models.SecurityPrice.DoesNotExist:
        max_id = 0
    async for d in client.sma_security_quote(str(max_id)):
        default = {
            'secucode_id': d.secucode_id, 'date': d.date, 'auto_date': d.auto_date, 'price': d.price, 'note': d.note,
            'o32': d.o32
        }
        await sync_to_async(models.SecurityPrice.objects.update_or_create)(id=d.id, defaults=default)


async def update_sma():
    await update_portfolio()
    whole = await sync_to_async(models.Portfolio.objects.filter)(settlemented=0)
    whole = await sync_to_async(list)(whole)
    for portfolio in whole:
        await update_portfolio_expanded()
        await balance(portfolio)
        await balance_expanded(portfolio)
        await income(portfolio)
        await income_asset(portfolio)
        await holding(portfolio)
        await transaction(portfolio)
        await detail_fee(portfolio)
        await benchmark(portfolio)
        await interest_tax(portfolio)
        await security()
        await security_quote()


def commit_sma():
    """从客户服务系统更新sma数据"""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(update_sma())


__all__ = ('commit_sma',)


if __name__ == '__main__':
    commit_sma()
