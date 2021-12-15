"""
Portfolio
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-09-08
@desc:
"""

from django.db import models

from .funds import Funds


# 组合基础信息表
class Portfolio(models.Model):
    id = models.IntegerField(primary_key=True, verbose_name="组合ID")
    port_code = models.CharField(max_length=12, null=False, unique=True, verbose_name="组合代码")
    port_name = models.CharField(max_length=20, null=False, verbose_name="组合名称")
    manager = models.CharField(max_length=20, null=False, verbose_name="管理人")
    init_money = models.DecimalField(verbose_name="初始资金", max_digits=18, decimal_places=4)
    purchase_fee = models.DecimalField(verbose_name="申购费", max_digits=6, decimal_places=4, default=0.0)
    redemption_fee = models.DecimalField(verbose_name="赎回费", max_digits=6, decimal_places=4, default=0.0)
    base = models.CharField(max_length=100, verbose_name="业绩比较基准")
    describe = models.CharField(verbose_name="组合描述", max_length=100)
    activation = models.DecimalField(verbose_name="开户费", max_digits=10, decimal_places=2, default=0)
    port_type = models.IntegerField(
        verbose_name='组合类型', default=3,
        choices=((1, '现金型'), (2, '固收型'), (3, '平衡型'), (4, '成长型'), (5, '权益型'), (6, 'CTA'))
    )
    launch_date = models.DateTimeField(null=False, verbose_name="成立日期")
    settlemented = models.IntegerField(verbose_name='是否已清算', choices=((0, '否'), (1, '是')), default=1)
    t_n = models.IntegerField(verbose_name="估值频率", default=1)

    class Meta:
        db_table = 'sma_portfolio'
        verbose_name = "1. 组合基础信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'<{self.port_code} {self.port_name}>'


class PortfolioExpanded(models.Model):
    port_code = models.ForeignKey(
        to=Portfolio, to_field='port_code', on_delete=models.DO_NOTHING)
    o32 = models.IntegerField(verbose_name="o32中基金编号", null=False)
    valuation = models.CharField(
        verbose_name="估值表中基金名称", max_length=50, null=False)

    class Meta:
        db_table = 'sma_portfolio_expanded'
        verbose_name = "1.2 组合代码在O32和估值表中对应关系"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.port_code.port_code


# 组合资产负债表
class Balance(models.Model):
    port_code = models.ForeignKey(to=Portfolio, to_field='port_code', on_delete=models.CASCADE)
    asset = models.DecimalField(verbose_name='资产', max_digits=18, decimal_places=4, default=0)
    debt = models.DecimalField(verbose_name='负债', max_digits=18, decimal_places=4, default=0)
    net_asset = models.DecimalField(verbose_name='资产净值', max_digits=18, decimal_places=4, default=0)
    shares = models.DecimalField(verbose_name='份额', max_digits=18, decimal_places=4, default=0)
    unit_nav = models.DecimalField(verbose_name='单位净值', max_digits=8, decimal_places=4, default=0)
    acc_nav = models.DecimalField(verbose_name='累计单位净值', max_digits=8, decimal_places=4, default=0)
    savings = models.DecimalField(verbose_name='银行存款', max_digits=18, decimal_places=4, default=0)
    fund_invest = models.DecimalField(verbose_name='基金投资', max_digits=18, decimal_places=4, default=0)
    liquidation = models.DecimalField(verbose_name='证券清算款', max_digits=18, decimal_places=4, default=0)
    value_added = models.DecimalField(verbose_name='估值增值', max_digits=18, decimal_places=4, default=0)
    profit_pay = models.DecimalField(verbose_name='应付利润(红利)', max_digits=18, decimal_places=4, default=0)
    cash_dividend = models.DecimalField(verbose_name='分红', max_digits=18, decimal_places=4, default=0)
    security_deposit = models.DecimalField(verbose_name='存出保证金', max_digits=18, decimal_places=4, default=0)
    date = models.DateField(verbose_name='日期', null=False)

    class Meta:
        db_table = 'sma_balance'
        verbose_name = "2.1 组合资产负债"
        verbose_name_plural = verbose_name
        get_latest_by = ('date',)

    def __str__(self):
        return self.port_code.port_code


# 组合应收应付
class BalanceExpanded(models.Model):
    port_code = models.ForeignKey(to=Portfolio, to_field='port_code', on_delete=models.CASCADE)
    dividend_rec = models.DecimalField(verbose_name='应收股利', max_digits=18, decimal_places=4, default=0)
    interest_rec = models.DecimalField(verbose_name='应收利息', max_digits=18, decimal_places=4, default=0)
    purchase_rec = models.DecimalField(verbose_name='应收申购款', max_digits=18, decimal_places=4, default=0)
    redemption_pay = models.DecimalField(verbose_name='应付赎回款', max_digits=18, decimal_places=4, default=0)
    redemption_fee_pay = models.DecimalField(
        verbose_name='应付赎回费', max_digits=18, decimal_places=4, default=0)
    management_pay = models.DecimalField(verbose_name='应付管理人报酬', max_digits=18, decimal_places=4, default=0)
    custodian_pay = models.DecimalField(verbose_name='应付托管费', max_digits=18, decimal_places=4, default=0)
    withholding_pay = models.DecimalField(verbose_name='预提费用', max_digits=18, decimal_places=4, default=0)
    interest_pay = models.DecimalField(verbose_name='应付利息税', max_digits=18, decimal_places=4, default=0)
    date = models.DateField(verbose_name='日期', null=False)

    class Meta:
        db_table = 'sma_balance_expanded'
        verbose_name = "2.2 组合应收应付表"
        verbose_name_plural = verbose_name
        get_latest_by = ('date', )

    def __str__(self):
        return self.port_code.port_code


# 组合层面每日收益
class Income(models.Model):
    port_code = models.ForeignKey(Portfolio, to_field='port_code', on_delete=models.CASCADE)
    unit_nav = models.DecimalField(verbose_name='单位净值', max_digits=8, decimal_places=4, default=0)
    net_asset = models.DecimalField(verbose_name='资产净值', max_digits=18, decimal_places=4, default=0)
    change = models.DecimalField(verbose_name='涨跌', max_digits=18, decimal_places=4, default=0)
    change_pct = models.DecimalField(verbose_name='涨跌幅', max_digits=12, decimal_places=8, default=0)
    date = models.DateField(verbose_name="日期")

    class Meta:
        db_table = 'sma_income_portfolio'
        verbose_name = '3.1 组合损益表'
        verbose_name_plural = verbose_name
        get_latest_by = 'date'


# 资产层面(基金)每日收益
class IncomeAsset(models.Model):
    port_code = models.ForeignKey(Portfolio, to_field='port_code', on_delete=models.CASCADE)
    total_profit = models.DecimalField(verbose_name='基金整体收益', max_digits=18, decimal_places=4, default=0)
    equity = models.DecimalField(verbose_name='权益', max_digits=18, decimal_places=4, default=0)
    bond = models.DecimalField(verbose_name='固收', max_digits=18, decimal_places=4, default=0)
    alter = models.DecimalField(verbose_name='另类', max_digits=18, decimal_places=4, default=0)
    money = models.DecimalField(verbose_name='货币及现金', max_digits=18, decimal_places=4, default=0)
    date = models.DateField(verbose_name="日期")

    class Meta:
        db_table = 'sma_income_asset'
        verbose_name = '3.2 组合资产损益表'
        verbose_name_plural = verbose_name
        get_latest_by = 'date'


class Holding(models.Model):
    port_code = models.ForeignKey(Portfolio, to_field='port_code', on_delete=models.CASCADE)
    secucode = models.CharField(max_length=12, null=False, verbose_name="证券代码")
    holding_value = models.DecimalField(verbose_name="持仓数量", max_digits=18, decimal_places=4)
    mkt_cap = models.DecimalField(verbose_name="市值", max_digits=18, decimal_places=4)
    current_cost = models.DecimalField(verbose_name="持仓成本", max_digits=18, decimal_places=4)
    total_cost = models.DecimalField(verbose_name="含费用成本", max_digits=18, decimal_places=4)
    fee = models.DecimalField(verbose_name="费用合计", max_digits=12, decimal_places=4)
    flow_profit = models.DecimalField(verbose_name="浮动盈亏", max_digits=18, decimal_places=4)
    total_profit = models.DecimalField(verbose_name="总盈亏", max_digits=18, decimal_places=4)
    dividend = models.DecimalField(verbose_name="当日分红", max_digits=18, decimal_places=4)
    total_dividend = models.DecimalField(verbose_name="累计分红", max_digits=18, decimal_places=4)
    category = models.CharField(verbose_name='证券类型', max_length=20, default='开放式基金')
    trade_market = models.IntegerField(verbose_name='交易市场', default=6)
    date = models.DateField(null=False, verbose_name="交易日")

    class Meta:
        db_table = 'sma_holding_fund'
        verbose_name = '4.1 组合持基明细'
        verbose_name_plural = verbose_name
        index_together = ['port_code', 'date']
        get_latest_by = 'date'

    def __str__(self):
        return self.port_code.port_code


class Transactions(models.Model):
    port_code = models.ForeignKey(Portfolio, to_field='port_code', on_delete=models.CASCADE)
    secucode = models.CharField(max_length=12, null=True, verbose_name="证券代码", blank=True)
    amount = models.DecimalField(verbose_name="发生金额", max_digits=18, decimal_places=4)
    balance = models.DecimalField(verbose_name="发生后余额", max_digits=18, decimal_places=4)
    order_price = models.DecimalField(verbose_name="委托价格", max_digits=10, decimal_places=4)
    order_value = models.DecimalField(verbose_name="委托数量", max_digits=18, decimal_places=4)
    deal_value = models.DecimalField(verbose_name="发生数量", max_digits=18, decimal_places=4)
    fee = models.DecimalField(verbose_name="费用", max_digits=10, decimal_places=4)
    operation_amount = models.DecimalField(verbose_name="科目发生额", max_digits=18, decimal_places=4)
    operation = models.CharField(verbose_name="业务类型", max_length=30, null=False)
    subject_name = models.CharField(max_length=20, verbose_name="科目名称", null=True, blank=True)
    date = models.DateField(null=False, verbose_name="交易发生时间")

    class Meta:
        db_table = 'sma_transactions'
        verbose_name = '4.2 组合交易流水'
        verbose_name_plural = verbose_name
        index_together = ['port_code', 'date']
        get_latest_by = ['date']

    def __str__(self):
        return self.port_code.port_code


class DetailFee(models.Model):
    port_code = models.ForeignKey(Portfolio, to_field='port_code', on_delete=models.CASCADE)
    management = models.DecimalField(verbose_name='管理费', max_digits=18, decimal_places=4, default=0)
    custodian = models.DecimalField(verbose_name='托管费', max_digits=18, decimal_places=4, default=0)
    audit = models.DecimalField(verbose_name='审计费', max_digits=18, decimal_places=4, default=0)
    interest = models.DecimalField(verbose_name='应收利息', max_digits=18, decimal_places=4, default=0)
    interest_tax = models.DecimalField(verbose_name='应付利息税', max_digits=18, decimal_places=4, default=0)
    date = models.DateField(verbose_name='业务日期')

    class Meta:
        db_table = 'sma_detail_fee'
        verbose_name = '4.3 组合费用提取明细'
        verbose_name_plural = verbose_name
        get_latest_by = 'date'

    def __str__(self):
        return self.port_code.port_name


class InterestTax(models.Model):
    port_code = models.ForeignKey(
        Portfolio, to_field='port_code', on_delete=models.CASCADE)
    secucode = models.CharField(verbose_name='基金代码', max_length=12)
    tax = models.DecimalField(verbose_name='当月累计利息税',
                              max_digits=18, decimal_places=4, default=0)
    date = models.DateField(verbose_name='业务日期')

    class Meta:
        db_table = 'sma_interest_tax'
        verbose_name = '4.4 组合场内交易基金利息税'
        verbose_name_plural = verbose_name
        get_latest_by = 'date'


# 基准估值表
class ValuationBenchmark(models.Model):
    port_code = models.ForeignKey(Portfolio, to_field='port_code', on_delete=models.CASCADE)
    unit_nav = models.DecimalField(verbose_name="单位净值", max_digits=10, decimal_places=4)
    date = models.DateField(null=False, verbose_name="交易日")

    class Meta:
        db_table = 'sma_evaluate_benchmark'
        verbose_name = '4.5 组合基准净值表'
        verbose_name_plural = verbose_name
        index_together = ['port_code', 'date']
        get_latest_by = 'date'

    def __str__(self):
        return self.port_code.port_name


# 组合风格
class PortfolioStyle(models.Model):
    port_code = models.ForeignKey(Portfolio, to_field='port_code', on_delete=models.CASCADE, verbose_name='组合代码')
    small_value = models.DecimalField(verbose_name='小盘价值', max_digits=6, decimal_places=4, default=0)
    small_growth = models.DecimalField(verbose_name='小盘成长', max_digits=6, decimal_places=4, default=0)
    mid_value = models.DecimalField(verbose_name='中盘价值', max_digits=6, decimal_places=4, default=0)
    mid_growth = models.DecimalField(verbose_name='中盘成长', max_digits=6, decimal_places=4, default=0)
    large_value = models.DecimalField(verbose_name='大盘价值', max_digits=6, decimal_places=4, default=0)
    large_growth = models.DecimalField(verbose_name='大盘成长', max_digits=6, decimal_places=4, default=0)
    bond = models.DecimalField(verbose_name='债券', max_digits=6, decimal_places=4, default=0)
    r_square = models.DecimalField(verbose_name='R方', max_digits=6, decimal_places=4, default=0)
    date = models.DateField(verbose_name='日期')

    class Meta:
        db_table = 'sma_style'
        verbose_name = '4.6 组合风格'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.port_code.port_code


# 组合Brinson归因
class PortfolioBrinson(models.Model):
    port_code = models.ForeignKey(Portfolio, to_field='port_code', on_delete=models.CASCADE, verbose_name='组合代码')
    index = models.CharField(verbose_name='指数代码', max_length=20, null=False)
    date = models.DateField(verbose_name='日期', null=False)
    industry = models.CharField(verbose_name='行业', max_length=20, null=False)
    q1 = models.DecimalField(verbose_name='q1', max_digits=12, decimal_places=8)
    q2 = models.DecimalField(verbose_name='q2', max_digits=12, decimal_places=8)
    q3 = models.DecimalField(verbose_name='q3', max_digits=12, decimal_places=8)
    q4 = models.DecimalField(verbose_name='q4', max_digits=12, decimal_places=8)

    class Meta:
        db_table = 'sma_brinson'
        verbose_name = '4.7 组合Brinson'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.port_code.port_code


# TA对照表
class Sales(models.Model):
    port_code = models.ForeignKey(Portfolio, to_field='port_code', on_delete=models.CASCADE, verbose_name='组合代码')
    name = models.CharField(verbose_name='姓名', max_length=20, null=False)
    mobile = models.CharField(verbose_name='手机', max_length=20)
    mail = models.CharField(verbose_name='邮箱', max_length=50)

    class Meta:
        db_table = 'sma_sales'
        verbose_name = '1.2 组合对应销售人员'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.port_code.port_code


# 每日预估净值记录
class PreValuedNav(models.Model):
    port_code = models.ForeignKey(Portfolio, to_field='port_code', on_delete=models.CASCADE, verbose_name='组合代码')
    date = models.DateField(null=False, verbose_name='预估值日期')
    value = models.DecimalField(verbose_name='预估净值', decimal_places=6, max_digits=8)

    class Meta:
        db_table = 'sma_portfolio_pre_valuation'
        verbose_name = '4.8 组合每日预估值记录'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.port_code.port_code


# 客户申赎申请
class ClientPR(models.Model):
    port_code = models.ForeignKey(Portfolio, to_field='port_code', on_delete=models.CASCADE, verbose_name='组合代码')
    purchase_amount = models.DecimalField(verbose_name='申购金额', max_digits=18, decimal_places=2, null=True, blank=True)
    ransom_share = models.DecimalField(verbose_name='赎回份额', max_digits=18, decimal_places=2, null=True, blank=True)
    p_open_date = models.DateField(verbose_name='申购开放日', null=True, blank=True)
    r_open_date = models.DateField(verbose_name='赎回开放日', null=True, blank=True)
    p_confirm = models.IntegerField(
        choices=((1, 'T+1'), (2, 'T+2'), (3, 'T+3'), (4, 'T+4')), verbose_name='赎回确认日', null=True, blank=True)
    r_confirm = models.IntegerField(
        choices=((1, 'T+1'), (2, 'T+2'), (3, 'T+3'), (4, 'T+4')), verbose_name='赎回确认日', null=True, blank=True)
    complete = models.BooleanField(verbose_name='是否完成', default=False, blank=True)

    class Meta:
        db_table = 'sma_client_pr'
        verbose_name = '5.1 组合客户申赎记录'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.port_code.port_code


# portfolio asset allocate
class PortfolioAssetAllocate(models.Model):
    port_code = models.ForeignKey(Portfolio, to_field='port_code', on_delete=models.CASCADE, verbose_name='组合代码')
    equity = models.DecimalField(verbose_name='权益', max_digits=18, decimal_places=6, default=0)
    fix_income = models.DecimalField(verbose_name='固收', max_digits=18, decimal_places=6, default=0)
    alter = models.DecimalField(verbose_name='另类', max_digits=18, decimal_places=6, default=0)
    money = models.DecimalField(verbose_name='货币', max_digits=18, decimal_places=6, default=0)
    other = models.DecimalField(verbose_name='其他', max_digits=18, decimal_places=6, default=0)
    date = models.DateField(verbose_name='日期', null=True, blank=True)

    class Meta:
        db_table = 'sma_portfolio_allocate'
        verbose_name = '4.9 组合资产配置'
        verbose_name_plural = verbose_name
        get_latest_by = 'date'

    def __str__(self):
        return self.port_code.port_code


# 基金备投池
class ObservePool(models.Model):
    secucode = models.ForeignKey(Funds, to_field='secucode', on_delete=models.CASCADE, verbose_name='基金代码')

    class Meta:
        db_table = 'sma_observe_pool'
        verbose_name = '基金备投池'
        verbose_name_plural = verbose_name
