# Generated by Django 3.2.3 on 2021-05-27 16:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cta_fof', '0005_portfolioexpanded'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='balance',
            options={'get_latest_by': ('date',), 'verbose_name': '3.1组合资产负债', 'verbose_name_plural': '3.1组合资产负债'},
        ),
        migrations.AlterModelOptions(
            name='balanceexpanded',
            options={'get_latest_by': ('date',), 'verbose_name': '3.2组合应收应付表', 'verbose_name_plural': '3.2组合应收应付表'},
        ),
        migrations.AlterModelOptions(
            name='holding',
            options={'get_latest_by': 'date', 'verbose_name': '4.组合持基明细', 'verbose_name_plural': '4.组合持基明细'},
        ),
        migrations.AlterModelOptions(
            name='portfolio',
            options={'verbose_name': '1.组合基础信息', 'verbose_name_plural': '1.组合基础信息'},
        ),
        migrations.AlterModelOptions(
            name='portfolioexpanded',
            options={'verbose_name': '2.组合对应O32和TA关联关系'},
        ),
        migrations.AlterModelOptions(
            name='transactions',
            options={'get_latest_by': ['date'], 'verbose_name': '5.组合交易流水', 'verbose_name_plural': '5.组合交易流水'},
        ),
    ]
