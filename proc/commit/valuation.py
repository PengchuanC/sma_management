import datetime
from typing import Iterable

from proc import models
from proc.configs import FileStoragePath
from proc.read.valuation import read_valuation
from proc.read.collect import collect_files
from investment.models.tradingday import TradingDays


def whole_cta_fof() -> Iterable[models.Portfolio]:
    """获取全部CTA FOF"""
    fof = models.Portfolio.objects.filter(valid=True)
    return fof


def latest_update_date(port_code: models.Portfolio) -> datetime.date:
    """组合最后更新日期，如果没有最新更新日期，默认采用成立日前一天"""
    last = models.Balance.objects.filter(port_code=port_code.port_code)
    if last.exists():
        return last.latest('date').date
    info = models.Portfolio.objects.get(port_code=port_code.port_code)
    return info.launch_date.date() - datetime.timedelta(days=1)


def three_days_ago():
    """三个交易日之前"""
    t = datetime.date.today()
    month_ago = t - datetime.timedelta(days=30)
    days = TradingDays.objects.filter(date__range=(
        month_ago, t)).values('date').order_by('date')
    days = [x['date'] for x in days]
    day = days[-3]
    return day


def commit_valuation():
    """同步全部CTA FOF的估值表数据"""
    whole = whole_cta_fof()
    for fof in whole:
        commit_single_cta(fof)


def commit_single_cta(portfolio: models.Portfolio):
    """同步单只CTA的估值表数据"""
    latest = latest_update_date(portfolio)
    name = models.PortfolioExpanded.objects.get(
        port_code=portfolio.port_code).valuation
    vfs = collect_files(FileStoragePath.valuation, 'xls', name)
    vfs = [x for x in vfs if x.date > latest]
    for vf in vfs:
        date = vf.date
        tradingday = TradingDays.objects.filter(date=date)
        # 非交易日估值表（多数为月末）不同步
        if not tradingday.exists():
            continue
        # 交易日不满足T+3暂不同步
        t_3 = three_days_ago()
        if date >= t_3:
            continue
        v = read_valuation(vf)
        bl = models.Balance(
            port_code=portfolio, asset=v['asset'], debt=v['debt'], net_asset=v['net_asset'], shares=v['shares'],
            unit_nav=v['unit_nav'], acc_nav=v['acc_nav'], savings=v['savings'], fund_invest=v['fund_invest'],
            liquidation=v['liquidation'], value_added=v['value_added'], profit_pay=v['profit_pay'], cash_dividend=0,
            date=date
        )
        ble = models.BalanceExpanded(
            port_code=portfolio, dividend_rec=v['dividend_rec'],
            interest_rec=v['interest_rec'], purchase_rec=v['purchase_rec'], redemption_pay=v['redemption_pay'],
            redemption_fee_pay=v['redemption_fee_pay'], management_pay=v['management_pay'],
            custodian_pay=v['custodian_pay'], withholding_pay=v['withholding_pay'], date=date
        )
        bl.save()
        ble.save()


__all__ = ('commit_valuation', 'whole_cta_fof', 'latest_update_date')
