"""
client_questionnaire
~~~~~~~~~~~~~~~~~~~~
客户评测摘要
客户问卷的摘要信息
@date: 2020-12-24
"""

from django.db import models
from .portfolio import Portfolio


class ClientQ(models.Model):
    port_code = models.ForeignKey(verbose_name='所属组合', to=Portfolio, to_field='port_code', on_delete=models.DO_NOTHING)
    risk = models.CharField('风险等级', max_length=4)
    maturity = models.CharField('投资期限', max_length=10)
    arr = models.CharField('目标收益', max_length=10)
    volatility = models.CharField('目标风险', max_length=20)
    fluidity = models.CharField('流动性要求', max_length=20)
    age = models.IntegerField('年龄')
    experience = models.CharField('投资经验', max_length=20)
    plan = models.CharField('大额支出计划', max_length=50)
    tolerance = models.CharField('回撤容忍度', max_length=20)
    alter_limit = models.CharField('另类资产限制', max_length=20)
    cross_border_limit = models.CharField('跨境投资限制', max_length=20)

    class Meta:
        db_table = 'sma_questionnaire_summary'
        verbose_name = '客户评测主要信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.port_code.port_name
