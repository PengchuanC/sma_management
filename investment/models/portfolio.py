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
    port_code = models.CharField(max_length=20, verbose_name='组合代码', unique=True, db_index=True)
    port_name = models.CharField(max_length=50, verbose_name='组合简称')
    port_type = models.CharField(max_length=20, verbose_name='产品类型', choices=(
        ('现金型', '现金型'), ('固收型', '固收型'), ('平衡型', '平衡型'), ('成长型', '成长型'), ('权益型', '权益型'), ('CTA', 'CTA')
    ))
    benchmark = models.CharField(max_length=100, verbose_name='业绩比较基准', choices=(
        ('100%*中债3-5年国债指数+0%*中证800指数', '现金型基准'), ('80%*中债3-5年国债指数+20%*中证800指数', '固收型基准'),
        ('60%*中债3-5年国债指数+40%*中证800指数', '平衡型基准'), ('40%*中债3-5年国债指数+60%*中证800指数', '成长型基准'),
        ('20%*中债3-5年国债指数+80%*中证800指数', '权益型基准')
    ))
    t_n = models.IntegerField(verbose_name='估值频率(T+N)', default=2)
    settlemented = models.BooleanField(verbose_name='是否已清算', choices=((1, '是'), (0, '否')), default=0)

    class Meta:
        db_table = 'sma_portfolio'
        verbose_name = '1.1 组合基础信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.port_code


class PortfolioExpanded(models.Model):
    port_code = models.OneToOneField(Portfolio, on_delete=models.CASCADE, verbose_name='组合代码')
    init_money = models.DecimalField(verbose_name='初始资金', default=10000000, max_digits=20, decimal_places=2)
    activation = models.DecimalField(verbose_name='开户费', max_digits=20, decimal_places=2, default=0)
    fund_id = models.IntegerField(verbose_name='恒生代码', default=0)
    launch = models.DateField(verbose_name='成立日', null=True)

    class Meta:
        db_table = 'sma_portfolio_expanded'
        verbose_name = '1.2 组合扩展信息'
        verbose_name_plural = verbose_name

    def __repr__(self):
        return self.port_code.port_code


# 组合资产负债表
class Valuation(models.Model):
    port_code = models.ForeignKey(Portfolio, to_field='port_code', on_delete=models.CASCADE, verbose_name='产品代码')
    asset = models.DecimalField(verbose_name='资产合计', max_digits=20, decimal_places=2, default=0)
    debt = models.DecimalField(verbose_name='负债合计', max_digits=20, decimal_places=2, default=0)
    net_asset = models.DecimalField(verbose_name='资产净值', max_digits=20, decimal_places=2, default=0)
    unit_nav = models.DecimalField(verbose_name='单位净值', max_digits=10, decimal_places=4, default=0)
    accu_nav = models.DecimalField(verbose_name='累计净值', max_digits=10, decimal_places=4, default=0)
    nav_increment = models.DecimalField(verbose_name='净值日增长率', max_digits=10, decimal_places=4, default=0)
    date = models.DateField(verbose_name='业务日期')

    class Meta:
        db_table = 'sma_balance'
        verbose_name = '5.1 基金估值表'
        verbose_name_plural = verbose_name
        unique_together = ('port_code', 'date')

    def __str__(self):
        return self.port_code.port_code


class ValuationEx(models.Model):
    port_code = models.OneToOneField(Valuation, to_field='id', on_delete=models.CASCADE, verbose_name='产品代码')
    savings = models.DecimalField(verbose_name='银行存款', max_digits=20, decimal_places=2, default=0)
    settlement_reserve = models.DecimalField(verbose_name='结算备付金', max_digits=20, decimal_places=2, default=0)
    deposit = models.DecimalField(verbose_name='存出保证金', max_digits=20, decimal_places=2, default=0)
    stocks = models.DecimalField(verbose_name='股票投资', max_digits=20, decimal_places=2, default=0)
    bonds = models.DecimalField(verbose_name='债券投资', max_digits=20, decimal_places=2, default=0)
    abs = models.DecimalField(verbose_name='资产支持证券投资', max_digits=20, decimal_places=2, default=0)
    funds = models.DecimalField(verbose_name='基金投资', max_digits=20, decimal_places=2, default=0)
    metals = models.DecimalField(verbose_name='贵金属投资', max_digits=20, decimal_places=2, default=0)
    other = models.DecimalField(verbose_name='其他投资', max_digits=20, decimal_places=2, default=0)
    resale_agreements = models.DecimalField(verbose_name='买入返售金融资产', max_digits=20, decimal_places=2, default=0)
    purchase_rec = models.DecimalField(verbose_name='应收申购款', max_digits=20, decimal_places=2, default=0)
    ransom_pay = models.DecimalField(verbose_name='应付赎回款', max_digits=20, decimal_places=2, default=0)
    date = models.DateField(verbose_name='业务日期')

    class Meta:
        db_table = 'sma_balance_expanded'
        verbose_name = '5.2 基金估值表细项'
        verbose_name_plural = verbose_name
        unique_together = ('port_code', 'date')

    def __repr__(self):
        return self.port_code.port_code


class PurchaseAndRansom(models.Model):
    port_code = models.ForeignKey(Portfolio, to_field='port_code', on_delete=models.CASCADE, verbose_name='产品代码')
    date = models.DateField(verbose_name='日期')
    confirm = models.DateField(verbose_name='确认日期')
    pr_quantity = models.DecimalField(verbose_name='申购数量', max_digits=20, decimal_places=2, default=0)
    pr_amount = models.DecimalField(verbose_name='申购金额', max_digits=20, decimal_places=2, default=0)
    rs_quantity = models.DecimalField(verbose_name='赎回数量', max_digits=20, decimal_places=2, default=0)
    rs_amount = models.DecimalField(verbose_name='赎回金额', max_digits=20, decimal_places=2, default=0)
    pr_fee_backend = models.DecimalField(verbose_name='后端申购费', max_digits=10, decimal_places=2, default=0)
    rs_fee = models.DecimalField(verbose_name='基金赎回费', max_digits=10, decimal_places=2, default=0)
    rs_fee_org = models.DecimalField(verbose_name='机构赎回费', max_digits=10, decimal_places=2, default=0)
    org_name = models.CharField(verbose_name='机构名称', max_length=250, null=True)

    class Meta:
        db_table = 'sma_purchase_ransom'
        verbose_name = '5.3 产品申购赎回记录'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.port_code.port_code


# 基准估值表
class ValuationBenchmark(models.Model):
    port_code = models.ForeignKey(Portfolio, to_field='port_code', on_delete=models.CASCADE)
    unit_nav = models.DecimalField(verbose_name="单位净值", max_digits=10, decimal_places=4)
    date = models.DateField(null=False, verbose_name="交易日")

    class Meta:
        db_table = 'sma_balance_benchmark'
        verbose_name = '5.4 组合基准估值表'
        verbose_name_plural = verbose_name
        index_together = ['port_code', 'date']
        get_latest_by = 'date'

    def __str__(self):
        return self.port_code.port_code


# 组合层面每日收益
class Income(models.Model):
    port_code = models.ForeignKey(Portfolio, to_field='port_code', on_delete=models.CASCADE, verbose_name='产品代码')
    date = models.DateField(verbose_name='净值日期')
    unit_nav = models.DecimalField(verbose_name='单位净值', max_digits=10, decimal_places=4)
    net_asset_chg = models.DecimalField(verbose_name='净资产变动', max_digits=20, decimal_places=2, default=0)
    total_net_asset_chg = models.DecimalField(verbose_name='净资产总变动', max_digits=20, decimal_places=2)
    unit_nav_chg = models.DecimalField(verbose_name='涨跌幅', max_digits=10, decimal_places=4)

    class Meta:
        db_table = 'sma_income'
        verbose_name = '7.1 产品收益情况'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.port_code.port_code


class IncomeEx(models.Model):
    port_code = models.ForeignKey(Portfolio, to_field='port_code', on_delete=models.CASCADE, verbose_name='产品代码')
    date = models.DateField(verbose_name='净值日期')
    total = models.DecimalField(verbose_name='累计收益', max_digits=20, decimal_places=2)
    today_total = models.DecimalField(verbose_name='当日收益', max_digits=20, decimal_places=2)
    equity = models.DecimalField(verbose_name='权益累计收益', max_digits=20, decimal_places=2)
    today_equity = models.DecimalField(verbose_name='权益当日收益', max_digits=20, decimal_places=2)
    fix_income = models.DecimalField(verbose_name='固收累计收益', max_digits=20, decimal_places=2)
    today_fix_income = models.DecimalField(verbose_name='固产当日收益', max_digits=20, decimal_places=2)
    alternative = models.DecimalField(verbose_name='另类累计收益', max_digits=20, decimal_places=2)
    today_alternative = models.DecimalField(verbose_name='另类当日收益', max_digits=20, decimal_places=2)
    monetary = models.DecimalField(verbose_name='现金累计收益', max_digits=20, decimal_places=2)
    today_monetary = models.DecimalField(verbose_name='现金当日收益', max_digits=20, decimal_places=2)
    fare = models.DecimalField(verbose_name='累计费用', max_digits=20, decimal_places=2)
    today_fare = models.DecimalField(verbose_name='当日费用', max_digits=20, decimal_places=2)
    other = models.DecimalField(verbose_name='累计轧差', max_digits=20, decimal_places=2)
    today_other = models.DecimalField(verbose_name='当日轧差', max_digits=20, decimal_places=2)

    class Meta:
        db_table = 'sma_income_ex'
        verbose_name = '7.2 产品分类收益'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.port_code.port_code


class Holding(models.Model):
    port_code = models.ForeignKey(Portfolio, to_field='port_code', on_delete=models.CASCADE, verbose_name='产品代码')
    date = models.DateField(verbose_name='交易日期')
    secucode = models.CharField(verbose_name='证券代码', max_length=20)
    market = models.IntegerField(verbose_name='交易市场', choices=((1, '上海'), (2, '深圳'), (6, '场外')))
    begin_shares = models.DecimalField(verbose_name='日初份额', max_digits=20, decimal_places=2, default=0)
    current_shares = models.DecimalField(verbose_name='当前份额', max_digits=20, decimal_places=2, default=0)
    mkt_cap = models.DecimalField(verbose_name='当前市值', max_digits=20, decimal_places=2, default=0)
    today_fare = models.DecimalField(verbose_name='当日费用', max_digits=20, decimal_places=2, default=0)
    fare = models.DecimalField(verbose_name='累计费用', max_digits=20, decimal_places=2, default=0)
    today_dividend = models.DecimalField(verbose_name='当日分红', max_digits=20, decimal_places=2, default=0)
    dividend = models.DecimalField(verbose_name='累计分红', max_digits=20, decimal_places=2, default=0)
    today_profit = models.DecimalField(verbose_name='当日收益', max_digits=20, decimal_places=2, default=0)
    profit = models.DecimalField(verbose_name='累计收益', max_digits=20, decimal_places=2, default=0)

    class Meta:
        db_table = 'sma_holding'
        verbose_name = '6.2 产品持仓记录'
        verbose_name_plural = verbose_name
        unique_together = ('port_code', 'date', 'secucode', 'market')

    def __str__(self):
        return self.port_code.port_code


class Transactions(models.Model):
    port_code = models.ForeignKey(Portfolio, to_field='port_code', on_delete=models.CASCADE, verbose_name='产品代码')
    date = models.DateField(verbose_name='交易日期')
    operation = models.CharField(verbose_name='操作类型', max_length=250, null=True)
    operation_flag = models.IntegerField(verbose_name='操作标识')
    secucode = models.CharField(verbose_name='证券代码', max_length=20, null=True)
    entrust_quantity = models.DecimalField(verbose_name='委托数量', max_digits=20, decimal_places=2, default=0)
    entrust_price = models.DecimalField(verbose_name='委托价格', max_digits=10, decimal_places=4, default=0)
    busin_quantity = models.DecimalField(verbose_name='成交数量', max_digits=20, decimal_places=2, default=0)
    occur_amount = models.DecimalField(verbose_name='发生金额', max_digits=20, decimal_places=2, default=0)
    subject_amount = models.DecimalField(verbose_name='科目发生额', max_digits=20, decimal_places=2, default=0, null=True)
    fare = models.DecimalField(verbose_name='交易费用', max_digits=10, decimal_places=2, default=0)
    note = models.CharField(verbose_name='会计科目', max_length=250, null=True)
    market = models.CharField(verbose_name='交易市场', max_length=20, null=True, blank=True)

    class Meta:
        db_table = 'sma_transactions'
        verbose_name = '6.1 交易流水记录'
        verbose_name_plural = verbose_name
        get_latest_by = 'date'

    def __str__(self):
        return self.port_code.port_code


class Vouchers(models.Model):
    port_code = models.ForeignKey(Portfolio, to_field='port_code', on_delete=models.CASCADE, verbose_name='组合代码')
    digest = models.CharField(verbose_name='账簿摘要', max_length=250)
    code = models.CharField(verbose_name='会计科目', max_length=32)
    value = models.DecimalField(max_digits=19, decimal_places=4, default=0, verbose_name='贷方金额')
    date = models.DateField(verbose_name='业务日期')

    class Meta:
        db_table = 'sma_voucher'
        verbose_name = '4 凭证子表-估值表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.port_code.port_code


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
