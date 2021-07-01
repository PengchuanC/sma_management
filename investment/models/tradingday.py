from django.db import models


class TradingDays(models.Model):
    date = models.DateField(verbose_name="交易日")

    class Meta:
        db_table = 'sma_tradingdays'
        verbose_name = 'A股交易日历'
        verbose_name_plural = verbose_name
