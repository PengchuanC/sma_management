"""
@author: chuanchao.peng
@date: 2022/2/26 14:51
@file security.py
@desc:
"""
from django.db import models

from investment.models.portfolio import Portfolio


class Security(models.Model):
    secucode = models.CharField(verbose_name='证券代码', max_length=50, unique=True)
    secuabbr = models.CharField(verbose_name='证券名称', max_length=250)
    category = models.CharField(verbose_name='证券类型', max_length=50)
    category_code = models.CharField(verbose_name='类型代码', max_length=20)

    class Meta:
        db_table = 'sma_security'
        verbose_name = '3.1 证券主表-估值表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.secucode


class SecurityQuote(models.Model):
    secucode = models.ForeignKey(Security, to_field='secucode', on_delete=models.CASCADE, verbose_name='证券代码')
    port_code = models.ForeignKey(Portfolio, to_field='port_code', on_delete=models.CASCADE, verbose_name='组合代码')
    quote = models.DecimalField(verbose_name='单位净值', max_digits=20, decimal_places=4)
    note = models.CharField(verbose_name='行情备注', null=True, max_length=250)
    date = models.DateField(verbose_name='行情日期')
    auto_date = models.DateField(verbose_name='生成日期')

    class Meta:
        db_table = 'sma_security_quote'
        verbose_name = '3.2 证券行情-估值表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.secucode.secucode


class SecurityCategory(models.Model):
    secucode = models.ForeignKey(Security, to_field='secucode', on_delete=models.CASCADE, verbose_name='证券代码')
    first = models.CharField(verbose_name='一级分类', max_length=20, choices=(
        ('权益类', '权益类'), ('固收类', '固收类'), ('另类', '另类'), ('货币', '货币')
    ))
    second = models.CharField(verbose_name='二级分类', max_length=20, null=True, blank=True)

    class Meta:
        db_table = 'sma_security_category'
        verbose_name = '3.3 证券分类表（自定义）'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.secucode.secucode
