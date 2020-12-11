"""
fund
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-06-30
@desc: 定义基金基础数据model
"""

from django.db import models
from django.utils import timezone


# 基金列表
class Funds(models.Model):
    secucode = models.CharField(max_length=12, primary_key=True, verbose_name='基金代码')
    secuname = models.CharField(max_length=50, verbose_name='基金简称')

    class Meta:
        db_table = "sma_funds"
        verbose_name = '基金主表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.secucode


# 基金净值或万份收益数据
class FundPrice(models.Model):
    secucode = models.ForeignKey(Funds, to_field='secucode', on_delete=models.CASCADE)
    nv = models.DecimalField(verbose_name='净资产值(元)', null=True, max_digits=18, decimal_places=4)
    nav = models.DecimalField(verbose_name='单位净值', max_digits=18, decimal_places=6, null=True, blank=True)
    acc_nav = models.DecimalField(verbose_name='累计单位净值', max_digits=18, decimal_places=6, null=True, blank=True)
    dailyprofit = models.DecimalField(verbose_name='万份收益', null=True, max_digits=18, decimal_places=6, blank=True)
    date = models.DateField(verbose_name='交易日', null=False, default=timezone.now)

    class Meta:
        db_table = 'sma_fund_price'
        verbose_name = '基金累计净值表'
        verbose_name_plural = verbose_name
        index_together = ['secucode', 'date']
        get_latest_by = ['date']

    def __str__(self):
        return f'{self.secucode.secucode} {self.secucode.secuname}'


# 基金复权净值
class FundAdjPrice(models.Model):
    secucode = models.ForeignKey(Funds, to_field='secucode', on_delete=models.CASCADE)
    nav = models.DecimalField(verbose_name='单位净值', max_digits=18, decimal_places=6, null=True, blank=True)
    adj_nav = models.DecimalField(verbose_name='累计单位净值', max_digits=18, decimal_places=6, null=True, blank=True)
    date = models.DateField(verbose_name='交易日', null=False, default=timezone.now)

    class Meta:
        db_table = 'sma_fund_adj_price'
        verbose_name = '基金复权单位净值表'
        verbose_name_plural = verbose_name
        index_together = ['secucode', 'date']
        get_latest_by = ['date']

    def __str__(self):
        return f'{self.secucode.secucode} {self.secucode.secuname}'


# 基金风格
class FundStyle(models.Model):
    secucode = models.ForeignKey(Funds, to_field='secucode', on_delete=models.CASCADE)
    fundstyle = models.CharField(max_length=20, verbose_name="基金投资风格")
    fundtype = models.CharField(max_length=20, verbose_name="基金类型")

    class Meta:
        db_table = "sma_fund_style"
        verbose_name = "基金风格"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.secucode.secuname


# 基金申赎状态
class FundPurchaseAndRedeem(models.Model):
    secucode = models.ForeignKey(Funds, to_field='secucode', on_delete=models.CASCADE)
    apply_type = models.CharField(verbose_name='申购状态', null=True, max_length=20)
    redeem_type = models.CharField(verbose_name='赎回状态', null=True, max_length=20)
    min_apply = models.DecimalField(verbose_name='购买起点', max_digits=18, decimal_places=2, null=True, max_length=20)
    max_apply = models.DecimalField(verbose_name='单日限额', max_digits=18, decimal_places=2, null=True, max_length=20)
    date = models.DateField(auto_now=True)

    class Meta:
        db_table = "sma_fund_purchase_and_redeem"
        verbose_name = "基金申赎状态"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.secucode.secucode


# 基金持股
class FundHoldingStock(models.Model):
    secucode = models.ForeignKey(Funds, to_field='secucode', on_delete=models.CASCADE, verbose_name='基金代码')
    stockcode = models.CharField(max_length=20, null=False, verbose_name='股票代码')
    stockname = models.CharField(max_length=20, null=False, verbose_name='股票简称')
    serial = models.IntegerField(verbose_name='排名', null=False, default=1)
    ratio = models.DecimalField(verbose_name='占净值比', decimal_places=4, max_digits=8, default=0)
    publish = models.CharField(verbose_name='报告类型', choices=(('年报', '年报'), ('季报', '季报')), default='季报', max_length=8)
    date = models.DateField(verbose_name='报告期')

    class Meta:
        db_table = "sma_fund_holding_stock"
        verbose_name = "基金持股情况"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.secucode.secucode


# 基金申购费率-折后
class FundPurchaseFee(models.Model):
    secucode = models.ForeignKey(Funds, to_field='secucode', on_delete=models.CASCADE, verbose_name='基金代码')
    operate = models.CharField(verbose_name='交易方向', max_length=4, choices=(('buy', '买'), ('sell', '卖')))
    low = models.IntegerField(verbose_name='区间下限(<x)', default=0)
    high = models.IntegerField(verbose_name='区间上限(x<=)', null=True)
    fee = models.DecimalField(verbose_name="费率", max_digits=18, decimal_places=6)

    class Meta:
        db_table = "sma_fund_purchase_fee"
        verbose_name = "基金申购赎回费率(天天基金网)"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.secucode.secucode


# 联接基金、LOF对应场内基金
class FundAssociate(models.Model):
    secucode = models.ForeignKey(Funds, to_field='secucode', on_delete=models.CASCADE, verbose_name='基金代码')
    relate = models.CharField(verbose_name='关联基金代码', max_length=10, null=False)

    class Meta:
        db_table = 'sma_fund_associate'
        verbose_name = '基金代码关联'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.secucode.secucode


# 基金资产配置
class FundAssetAllocate(models.Model):
    secucode = models.ForeignKey(Funds, to_field='secucode', on_delete=models.CASCADE, verbose_name='基金代码')
    stock = models.DecimalField(verbose_name='股票投资', max_digits=18, decimal_places=6, default=0)
    bond = models.DecimalField(verbose_name='债券投资', max_digits=18, decimal_places=6, default=0)
    fund = models.DecimalField(verbose_name='基金投资', max_digits=18, decimal_places=6, default=0)
    metals = models.DecimalField(verbose_name='贵金属投资', max_digits=18, decimal_places=6, default=0)
    monetary = models.DecimalField(verbose_name='货币投资', max_digits=18, decimal_places=6, default=0)
    date = models.DateField(verbose_name='报告日期', null=False)

    class Meta:
        db_table = 'sma_fund_asset_allocate'
        verbose_name = '基金资产配置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.secucode.secucode


# 基金公告
class FundAnnouncement(models.Model):
    secucode = models.ForeignKey(Funds, to_field='secucode', on_delete=models.CASCADE, verbose_name='基金代码')
    secuabbr = models.CharField(verbose_name='基金简称', max_length=20, null=False)
    date = models.DateTimeField(verbose_name='公告日期', null=False)
    title = models.CharField(verbose_name='公告标题', null=False, max_length=200)
    content = models.TextField(verbose_name='公告内容', null=True)

    class Meta:
        db_table = 'sma_fund_announcement'
        verbose_name = '基金公告'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.secucode.secucode


# 基金管理人
class FundAdvisor(models.Model):
    secucode = models.ForeignKey(Funds, to_field='secucode', on_delete=models.CASCADE, verbose_name='基金代码')
    advisorcode = models.IntegerField(verbose_name='管理人代码', null=False)
    advisorname = models.CharField(verbose_name='管理人名称', max_length=50, null=False)

    class Meta:
        db_table = 'sma_fund_advisor'
        verbose_name = '基金管理人'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.secucode.secucode
