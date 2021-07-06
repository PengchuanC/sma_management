"""
valuation v2
~~~~~~~~~~~~
@date: 2021-06-21
@desc:
    初版估值表导入程序无法处理T+2以上的数据（OP不会反复导出估值表数据）
    因此在此版中采用从TA数据库中导出的数据来还原第一版估值表中的数据
"""
from pandas.core.reshape.concat import concat
from proc.read.valuation import read_valuation_new
from proc.commit.valuation import whole_cta_fof, latest_update_date, models, TradingDays, three_days_ago
from proc.configs import FileStoragePath
from proc.read import collect


def commit_valuation():
    """逐一同步数据"""
    whole = whole_cta_fof()
    for cta in whole:
        commit_single_cta_fof(cta)


def commit_single_cta_fof(cta: models.Portfolio):
    """同步单只CTA FOF数据"""
    o32 = models.PortfolioExpanded.objects.get(
        port_code=cta.port_code).o32_code
    latest = latest_update_date(cta)
    vfs = collect.collect_files(FileStoragePath.o32, 'xls', 'guzhibiao')
    vfs = [x for x in vfs if x.date > latest]
    balance = ['asset', 'debt', 'net_asset', 'shares', 'unit_nav',
               'acc_nav', 'savings', 'fund_invest', 'liquidation', 'value_added', 'profit_pay', 'cash_dividend',
               'security_deposit', 'date', 'port_code']
    expanded = ['dividend_rec', 'interest_rec', 'purchase_rec', 'redemption_pay',
                'redemption_fee_pay', 'management_pay', 'custodian_pay', 'withholding_pay', 'interest_pay',
                'date', 'port_code']
    for vf in vfs:
        date = vf.date
        tradingday = TradingDays.objects.filter(date=date)
        # 非交易日估值表（多数为月末）不同步
        if not tradingday.exists():
            continue
        v = read_valuation_new(vf)
        v = v.get(str(o32))
        ago = three_days_ago(max(v.index))
        v = v[(v.index > latest) & (v.index <= ago)]
        if v.empty:
            continue
        v = v.fillna(0)
        v['port_code'] = cta
        v = v.reset_index()
        b = v[balance]
        e = v[expanded]
        b = [models.Balance(**x) for _, x in b.iterrows()]
        e = [models.BalanceExpanded(**x) for _, x in e.iterrows()]
        models.Balance.objects.bulk_create(b)
        models.BalanceExpanded.objects.bulk_create(e)
