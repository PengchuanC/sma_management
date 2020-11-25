"""
stock
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-11-12
@desc: 定义股票基础数据model
"""

from django.db import models


class Stock(models.Model):
    secucode = models.CharField(max_length=12, primary_key=True, verbose_name='股票代码')
    secuname = models.CharField(max_length=50, verbose_name='股票简称')

    class Meta:
        db_table = 'sma_stocks'
        verbose_name = '股票列表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.secucode


class StockIndustrySW(models.Model):
    secucode = models.ForeignKey(Stock, to_field='secucode', on_delete=models.CASCADE, verbose_name="股票代码")
    firstindustryname = models.CharField(verbose_name="一级分类", max_length=10, null=False)
    secondindustryname = models.CharField(verbose_name="二级分类", max_length=20, null=False)

    class Meta:
        db_table = 'sma_stocks_industry_sw'
        verbose_name = '股票申万行业分类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.secucode.secucode


class StockRealtimePrice(models.Model):
    secucode = models.ForeignKey(Stock, to_field='secucode', on_delete=models.CASCADE, verbose_name="股票代码")
    prev_close = models.DecimalField(verbose_name='昨收', max_digits=10, decimal_places=4, null=True)
    price = models.DecimalField(verbose_name='实时价格', max_digits=10, decimal_places=4, null=True)
    date = models.DateField(verbose_name='日期', null=False)
    time = models.TimeField(verbose_name='时间', null=False)

    class Meta:
        db_table = 'sma_stocks_realtime_price'
        verbose_name = '股票实时价格'
        verbose_name_plural = verbose_name
