from django.db import models


class Portfolio(models.Model):
    port_code = models.CharField(verbose_name='组合代码', max_length=12)
