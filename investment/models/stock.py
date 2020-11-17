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
