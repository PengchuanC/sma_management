from django.db import models


class Portfolio(models.Model):
    id = models.IntegerField(primary_key=True, verbose_name="组合ID")
    port_code = models.CharField(
        max_length=12, null=False, unique=True, verbose_name="组合代码")
    port_name = models.CharField(
        max_length=20, null=False, verbose_name="组合名称")
    manager = models.CharField(max_length=20, null=False, verbose_name="管理人")
    init_money = models.DecimalField(
        verbose_name="初始资金", max_digits=18, decimal_places=4)
    port_type = models.CharField(verbose_name='产品类型', null=True, max_length=12)
    launch_date = models.DateTimeField(null=False, verbose_name="成立日期")
    valid = models.BooleanField(verbose_name='有效', default=True)

    class Meta:
        db_table = 'cta_portfolio'
        verbose_name = "1.组合基础信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'<{self.port_code} {self.port_name}>'


class PortfolioExpanded(models.Model):
    port_code = models.ForeignKey(
        Portfolio, to_field='port_code', on_delete=models.CASCADE)
    o32_code = models.IntegerField(verbose_name='o32中基金编码')
    valuation = models.CharField(verbose_name='估值表名称', max_length=100)

    class Meta:
        db_table = 'cta_portfolio_mapping'
        verbose_name = '2.组合对应O32和TA关联关系'


class Balance(models.Model):
    port_code = models.ForeignKey(
        Portfolio, to_field='port_code', on_delete=models.CASCADE)
    asset = models.DecimalField(
        verbose_name='资产', max_digits=18, decimal_places=4, default=0)
    debt = models.DecimalField(
        verbose_name='负债', max_digits=18, decimal_places=4, default=0)
    net_asset = models.DecimalField(
        verbose_name='资产净值', max_digits=18, decimal_places=4, default=0)
    shares = models.DecimalField(
        verbose_name='份额', max_digits=18, decimal_places=4, default=0)
    unit_nav = models.DecimalField(
        verbose_name='单位净值', max_digits=8, decimal_places=4, default=0)
    acc_nav = models.DecimalField(
        verbose_name='累计单位净值', max_digits=8, decimal_places=4, default=0)
    savings = models.DecimalField(
        verbose_name='银行存款', max_digits=18, decimal_places=4, default=0)
    fund_invest = models.DecimalField(
        verbose_name='基金投资', max_digits=18, decimal_places=4, default=0)
    liquidation = models.DecimalField(
        verbose_name='证券清算款', max_digits=18, decimal_places=4, default=0)
    value_added = models.DecimalField(
        verbose_name='估值增值', max_digits=18, decimal_places=4, default=0)
    profit_pay = models.DecimalField(
        verbose_name='应付利润(红利)', max_digits=18, decimal_places=4, default=0)
    cash_dividend = models.DecimalField(
        verbose_name='分红', max_digits=18, decimal_places=4, default=0)
    security_deposit = models.DecimalField(
        verbose_name='存出保证金', max_digits=18, decimal_places=4, default=0)
    date = models.DateField(verbose_name='日期', null=False)

    class Meta:
        db_table = 'cta_balance'
        verbose_name = "3.1组合资产负债"
        verbose_name_plural = verbose_name
        get_latest_by = ('date',)


class BalanceExpanded(models.Model):
    port_code = models.ForeignKey(
        Portfolio, to_field='port_code', on_delete=models.CASCADE)
    dividend_rec = models.DecimalField(
        verbose_name='应收股利', max_digits=18, decimal_places=4, default=0)
    interest_rec = models.DecimalField(
        verbose_name='应收利息', max_digits=18, decimal_places=4, default=0)
    purchase_rec = models.DecimalField(
        verbose_name='应收申购款', max_digits=18, decimal_places=4, default=0)
    redemption_pay = models.DecimalField(
        verbose_name='应付赎回款', max_digits=18, decimal_places=4, default=0)
    redemption_fee_pay = models.DecimalField(
        verbose_name='应付赎回费', max_digits=18, decimal_places=4, default=0)
    management_pay = models.DecimalField(
        verbose_name='应付管理人报酬', max_digits=18, decimal_places=4, default=0)
    custodian_pay = models.DecimalField(
        verbose_name='应付托管费', max_digits=18, decimal_places=4, default=0)
    withholding_pay = models.DecimalField(
        verbose_name='预提费用', max_digits=18, decimal_places=4, default=0)
    interest_pay = models.DecimalField(
        verbose_name='应付利息税', max_digits=18, decimal_places=4, default=0)
    date = models.DateField(verbose_name='日期', null=False)

    class Meta:
        db_table = 'cta_balance_expanded'
        verbose_name = "3.2组合应收应付表"
        verbose_name_plural = verbose_name
        get_latest_by = ('date',)


class Holding(models.Model):
    port_code = models.ForeignKey(
        Portfolio, to_field='port_code', on_delete=models.CASCADE)
    secucode = models.CharField(max_length=12, null=False, verbose_name="证券代码")
    holding_value = models.DecimalField(
        verbose_name="持仓数量", max_digits=18, decimal_places=4)
    mkt_cap = models.DecimalField(
        verbose_name="市值", max_digits=18, decimal_places=4)
    current_cost = models.DecimalField(
        verbose_name="持仓成本", max_digits=18, decimal_places=4)
    total_cost = models.DecimalField(
        verbose_name="含费用成本", max_digits=18, decimal_places=4)
    fee = models.DecimalField(
        verbose_name="费用合计", max_digits=12, decimal_places=4)
    flow_profit = models.DecimalField(
        verbose_name="浮动盈亏", max_digits=18, decimal_places=4)
    total_profit = models.DecimalField(
        verbose_name="总盈亏", max_digits=18, decimal_places=4)
    dividend = models.DecimalField(
        verbose_name="当日分红", max_digits=18, decimal_places=4)
    total_dividend = models.DecimalField(
        verbose_name="累计分红", max_digits=18, decimal_places=4)
    category = models.CharField(
        verbose_name='证券类型', max_length=20, default='开放式基金')
    trade_market = models.IntegerField(verbose_name='交易市场', default=6)
    date = models.DateField(null=False, verbose_name="交易日")

    class Meta:
        db_table = 'cta_holding_fund'
        verbose_name = '4.组合持基明细'
        verbose_name_plural = verbose_name
        index_together = ['port_code', 'date']
        get_latest_by = 'date'


class Transactions(models.Model):
    port_code = models.ForeignKey(
        Portfolio, to_field='port_code', on_delete=models.CASCADE)
    secucode = models.CharField(
        max_length=12, null=True, verbose_name="证券代码", blank=True)
    amount = models.DecimalField(
        verbose_name="发生金额", max_digits=18, decimal_places=4)
    balance = models.DecimalField(
        verbose_name="发生后余额", max_digits=18, decimal_places=4)
    order_price = models.DecimalField(
        verbose_name="委托价格", max_digits=10, decimal_places=4)
    order_value = models.DecimalField(
        verbose_name="委托数量", max_digits=18, decimal_places=4)
    deal_value = models.DecimalField(
        verbose_name="发生数量", max_digits=18, decimal_places=4)
    fee = models.DecimalField(
        verbose_name="费用", max_digits=10, decimal_places=4)
    operation_amount = models.DecimalField(
        verbose_name="科目发生额", max_digits=18, decimal_places=4)
    operation = models.CharField(
        verbose_name="业务类型", max_length=30, null=False)
    subject_name = models.CharField(
        max_length=20, verbose_name="科目名称", null=True, blank=True)
    date = models.DateField(null=False, verbose_name="交易发生时间")

    class Meta:
        db_table = 'cta_transactions'
        verbose_name = '5.组合交易流水'
        verbose_name_plural = verbose_name
        index_together = ['port_code', 'date']
        get_latest_by = ['date']
