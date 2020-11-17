"""
backtest
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-10-13
@desc: 回测数据model
"""

from django.db import models


class AssetWeight(models.Model):
    date = models.DateField(verbose_name="日期")
    equity_bound_limit = models.DecimalField(verbose_name='股指仓位上限', max_digits=8, decimal_places=6, default=0)
    target_risk = models.DecimalField(verbose_name='目标风险', max_digits=8, decimal_places=6, default=0)
    annual_r = models.DecimalField(verbose_name='年化收益', max_digits=10, decimal_places=6, default=0)
    risk = models.DecimalField(verbose_name='年化波动', max_digits=8, decimal_places=6, default=0)
    sharpe = models.DecimalField(verbose_name='夏普比', max_digits=8, decimal_places=6, default=0)
    hs300 = models.DecimalField(verbose_name='沪深300', max_digits=8, decimal_places=6, default=0)
    zcf = models.DecimalField(verbose_name='中债总财富', max_digits=8, decimal_places=6, default=0)
    qyz = models.DecimalField(verbose_name='中债企业债', max_digits=8, decimal_places=6, default=0)
    hb = models.DecimalField(verbose_name='货币基金', max_digits=8, decimal_places=6, default=0)
    zz500 = models.DecimalField(verbose_name='中证500', max_digits=8, decimal_places=6, default=0)
    hj = models.DecimalField(verbose_name='上海金现', max_digits=8, decimal_places=6, default=0)
    zz = models.DecimalField(verbose_name='中证转债', max_digits=8, decimal_places=6, default=0)
    hs = models.DecimalField(verbose_name='恒生指数', max_digits=8, decimal_places=6, default=0)

    class Meta:
        db_table = 'sma_backtest_weight'
        verbose_name = '回测用指数权重'
        verbose_name_plural = verbose_name
        index_together = ('date', 'target_risk')

    def __str__(self):
        return f'target_risk: {self.target_risk} annual_return: {self.annual_r}'
