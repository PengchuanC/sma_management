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
    secucode = models.CharField(max_length=12, verbose_name='股票代码', null=False)
    prev_close = models.DecimalField(verbose_name='昨收', max_digits=10, decimal_places=4, null=True)
    price = models.DecimalField(verbose_name='实时价格', max_digits=10, decimal_places=4, null=True)
    date = models.DateField(verbose_name='日期', null=False)
    time = models.TimeField(verbose_name='时间', null=False)

    class Meta:
        db_table = 'sma_stocks_realtime_price'
        verbose_name = '股票实时价格'
        get_latest_by = 'id'
        verbose_name_plural = verbose_name


class StockExpose(models.Model):
    secucode = models.ForeignKey(Stock, to_field='secucode', on_delete=models.CASCADE, verbose_name="股票代码")
    date = models.DateField(verbose_name='日期', null=False)
    beta = models.DecimalField(verbose_name='贝塔', max_digits=18, decimal_places=3)
    momentum = models.DecimalField(verbose_name='动量', max_digits=18, decimal_places=3)
    size = models.DecimalField(verbose_name='市值', max_digits=18, decimal_places=3)
    earnyild = models.DecimalField(verbose_name='盈利', max_digits=18, decimal_places=3)
    resvol = models.DecimalField(verbose_name='波动', max_digits=18, decimal_places=3)
    growth = models.DecimalField(verbose_name='成长', max_digits=18, decimal_places=3)
    btop = models.DecimalField(verbose_name='质量', max_digits=18, decimal_places=3)
    leverage = models.DecimalField(verbose_name='杠杆', max_digits=18, decimal_places=3)
    liquidty = models.DecimalField(verbose_name='流动', max_digits=18, decimal_places=3)
    sizenl = models.DecimalField(verbose_name='非线性市值', max_digits=18, decimal_places=3)

    class Meta:
        db_table = 'sma_stock_exposure'
        verbose_name = '股票因子暴露'
        verbose_name_plural = verbose_name
        index_together = ('secucode', 'date')

    def __str__(self):
        return self.secucode.secucode


class StockDailyQuote(models.Model):
    secucode = models.ForeignKey(Stock, to_field='secucode', on_delete=models.CASCADE, verbose_name="股票代码")
    closeprice = models.DecimalField(verbose_name='收盘价', max_digits=10, decimal_places=2)
    prevcloseprice = models.DecimalField(verbose_name='收盘价', max_digits=10, decimal_places=2)
    date = models.DateField(verbose_name='交易日', null=False)

    class Meta:
        db_table = 'sma_stock_daily_quote'
        verbose_name = '股票日行情'
        verbose_name_plural = verbose_name
        unique_together = (('secucode', 'date'),)


class StockDailyQuoteHK(models.Model):
    secucode = models.ForeignKey(Stock, to_field='secucode', on_delete=models.CASCADE, verbose_name="股票代码")
    closeprice = models.DecimalField(verbose_name='收盘价', max_digits=10, decimal_places=2)
    prevcloseprice = models.DecimalField(verbose_name='收盘价', max_digits=10, decimal_places=2)
    date = models.DateField(verbose_name='交易日', null=False)

    class Meta:
        db_table = 'sma_stock_daily_quote_hk'
        verbose_name = '股票日行情'
        verbose_name_plural = verbose_name
        unique_together = (('secucode', 'date'),)


class CapitalFlow(models.Model):
    secucode = models.ForeignKey(Stock, verbose_name='证券代码', to_field='secucode', on_delete=models.CASCADE)
    date = models.DateField(verbose_name='交易日期', null=False, blank=False)
    buyvalue = models.DecimalField(verbose_name='买入金额', decimal_places=4, max_digits=18, default=0)
    sellvalue = models.DecimalField(verbose_name='买入金额', decimal_places=4, max_digits=18, default=0)
    netvalue = models.DecimalField(verbose_name='买入金额', decimal_places=4, max_digits=18, default=0)

    class Meta:
        db_table = "sma_stock_capital_flow"
        verbose_name = "股票资金流动"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.secucode.secucode
