"""
Portfolio
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-09-08
@desc:
"""

from django.db import models


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
        choices=((1, '现金型'), (2, '固收型'), (3, '平衡型'), (4, '成长型'), (5, '权益型'))
    )
    launch_date = models.DateTimeField(null=False, verbose_name="成立日期")
    valid = models.BooleanField(verbose_name='有效', default=True)

    class Meta:
        db_table = 'sma_portfolio'
        verbose_name = "组合基础信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'<{self.port_code} {self.port_name}>'


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
    date = models.DateField(verbose_name='日期', null=False)

    class Meta:
        db_table = 'sma_balance'
        verbose_name = "组合资产负债"
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
    redemption_fee_pay = models.DecimalField(verbose_name='应付赎回费', max_digits=18, decimal_places=4, default=0)
    management_pay = models.DecimalField(verbose_name='应付管理人报酬', max_digits=18, decimal_places=4, default=0)
    custodian_pay = models.DecimalField(verbose_name='应付托管费', max_digits=18, decimal_places=4, default=0)
    withholding_pay = models.DecimalField(verbose_name='预提费用', max_digits=18, decimal_places=4, default=0)
    date = models.DateField(verbose_name='日期', null=False)

    class Meta:
        db_table = 'sma_balance_expanded'
        verbose_name = "组合应收应付表"
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
        verbose_name = '组合损益表'
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
        verbose_name = '组合资产损益表'
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
    date = models.DateField(null=False, verbose_name="交易日")

    class Meta:
        db_table = 'sma_holding_fund'
        verbose_name = '组合持基明细'
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
        verbose_name = '组合交易流水'
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
    date = models.DateField(verbose_name='业务日期')

    class Meta:
        db_table = 'sma_detail_fee'
        verbose_name = '组合费用提取明细'
        verbose_name_plural = verbose_name
        get_latest_by = 'date'

    def __str__(self):
        return self.port_code.port_name


# 基准估值表
class ValuationBenchmark(models.Model):
    port_code = models.ForeignKey(Portfolio, to_field='port_code', on_delete=models.CASCADE)
    unit_nav = models.DecimalField(verbose_name="单位净值", max_digits=10, decimal_places=4)
    date = models.DateField(null=False, verbose_name="交易日")

    class Meta:
        db_table = 'sma_evaluate_benchmark'
        verbose_name = '组合基准净值表'
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
        verbose_name = '组合风格'
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
        verbose_name = '组合Brinson'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.port_code.port_code
