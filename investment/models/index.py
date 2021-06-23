"""
index
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-09-04
@desc: 指数数据
1.指数列表
2.指数基础信息
3.指数行情-股票、债券、港股
4.指数成分表
"""

from django.db import models


class Index(models.Model):
    secucode = models.CharField(verbose_name="指数代码", unique=True, max_length=30)

    class Meta:
        db_table = 'sma_index'
        verbose_name = '指数列表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.secucode


class IndexBasicInfo(models.Model):
    secucode = models.ForeignKey(to=Index, to_field='secucode', on_delete=models.CASCADE, verbose_name='指数代码')
    secuabbr = models.CharField(max_length=100, verbose_name='证券简称', null=False)
    chiname = models.CharField(max_length=100, verbose_name='中文名称')
    category = models.CharField(max_length=20, verbose_name='指数类别')
    component = models.CharField(max_length=20, verbose_name='指数成分类别')
    source = models.IntegerField(verbose_name='数据来源', choices=((1, '聚源'), (2, '万得')), default=1)
    basedate = models.DateTimeField(null=False, verbose_name='基日')

    class Meta:
        db_table = 'sma_index_basic'
        verbose_name = '指数基础信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.secuabbr


class IndexQuote(models.Model):
    secucode = models.ForeignKey(to=Index, to_field='secucode', on_delete=models.CASCADE, verbose_name='指数代码')
    pre_close = models.DecimalField(verbose_name='昨收', max_digits=10, decimal_places=4)
    close = models.DecimalField(verbose_name='收盘价', max_digits=10, decimal_places=4)
    change = models.DecimalField(verbose_name='涨跌幅', max_digits=19, decimal_places=8)
    date = models.DateField(verbose_name='交易日', null=False)

    class Meta:
        db_table = 'sma_index_quote'
        verbose_name = '指数行情'
        verbose_name_plural = verbose_name
        get_latest_by = 'date'

    def __str__(self):
        return self.secucode.secucode


class IndexComponent(models.Model):
    secucode = models.ForeignKey(to=Index, to_field='secucode', on_delete=models.CASCADE, verbose_name='指数代码')
    stockcode = models.CharField(verbose_name='股票代码', max_length=20)
    weight = models.DecimalField(verbose_name='权重', max_digits=10, decimal_places=4, default=0)
    date = models.DateField(verbose_name='日期', null=False)

    class Meta:
        db_table = 'sma_index_component'
        verbose_name = '指数成分'
        verbose_name_plural = verbose_name
        get_latest_by = 'date'


class IndustryCF(models.Model):
    secucode = models.CharField(verbose_name='指数代码', max_length=20)
    secuabbr = models.CharField(verbose_name='指数名称', max_length=50)
    date = models.DateField(verbose_name='交易日')
    netvalue = models.FloatField(verbose_name='流入金额')
    ma3 = models.FloatField(verbose_name='三日均值')
    ma5 = models.FloatField(verbose_name='三日均值')
    ma10 = models.FloatField(verbose_name='三日均值')
    sigma5 = models.FloatField(verbose_name='五日标准差')
    ma5_high = models.FloatField(verbose_name='上沿')
    ma5_low = models.FloatField(verbose_name='下沿')

    class Meta:
        db_table = 'sma_industry_capital_flow'
        verbose_name = '行业资金流向'
        verbose_name_plural = verbose_name
        get_latest_by = 'date'
        index_together = ('secucode', 'date')
