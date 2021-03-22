"""
添加宜和1号的宜信交易流水及估算持仓
"""

from django.db import models
from .portfolio import Portfolio


class TransactionsYX(models.Model):
    port_code = models.ForeignKey(Portfolio, to_field='port_code', on_delete=models.CASCADE)
    secucode = models.CharField(max_length=12, null=True, verbose_name="证券代码", blank=True)
    operation = models.CharField(verbose_name="业务类型", max_length=30, null=False)
    amount = models.DecimalField(verbose_name="确认金额", max_digits=18, decimal_places=4)
    shares = models.DecimalField(verbose_name="确认份额", max_digits=18, decimal_places=4)
    fee = models.DecimalField(verbose_name="费用", max_digits=10, decimal_places=4)
    apply = models.DateField(null=False, verbose_name="申请时间")
    confirm = models.DateField(null=False, verbose_name="确认时间")

    class Meta:
        db_table = 'sma_transactions_yx'
        verbose_name = '组合交易流水-宜信普泽'
        verbose_name_plural = verbose_name
        get_latest_by = ['confirm']

    def __str__(self):
        return self.port_code.port_code


class HoldingYX(models.Model):
    port_code = models.ForeignKey(Portfolio, to_field='port_code', on_delete=models.CASCADE)
    secucode = models.CharField(max_length=12, null=True, verbose_name="证券代码", blank=True)
    shares = models.DecimalField(verbose_name="累计份额", max_digits=18, decimal_places=4)
    shares_change = models.DecimalField(verbose_name="份额变化", max_digits=18, decimal_places=4, default=0)
    date = models.DateField(null=False, verbose_name="确认时间")

    class Meta:
        db_table = 'sma_holding_fund_yx'
        verbose_name = '组合持基明细-宜信普泽'
        verbose_name_plural = verbose_name
        get_latest_by = 'date'

    def __str__(self):
        return self.port_code.port_code
