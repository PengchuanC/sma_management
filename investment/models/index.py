"""
index
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-09-04
@desc: 指数数据
1.指数列表
2.指数基础信息
3.指数行情-股票、债券、港股
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
    secucode = models.ForeignKey(to=Index, to_field='secucode', on_delete=models.CASCADE)
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
    secucode = models.ForeignKey(to=Index, to_field='secucode', on_delete=models.CASCADE)
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
