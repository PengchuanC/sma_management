# Generated by Django 3.1.2 on 2020-11-25 16:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('investment', '0028_fundassociate'),
    ]

    operations = [
        migrations.CreateModel(
            name='FundAssetAllocate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock', models.DecimalField(decimal_places=6, default=0, max_digits=18, verbose_name='股票投资')),
                ('bond', models.DecimalField(decimal_places=6, default=0, max_digits=18, verbose_name='债券投资')),
                ('fund', models.DecimalField(decimal_places=6, default=0, max_digits=18, verbose_name='基金投资')),
                ('metals', models.DecimalField(decimal_places=6, default=0, max_digits=18, verbose_name='贵金属投资')),
                ('monetary', models.DecimalField(decimal_places=6, default=0, max_digits=18, verbose_name='货币投资')),
                ('date', models.DateField(verbose_name='报告日期')),
                ('secucode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='investment.funds', verbose_name='基金代码')),
            ],
            options={
                'verbose_name': '基金资产配置',
                'verbose_name_plural': '基金资产配置',
                'db_table': 'sma_fund_asset_allocate',
            },
        ),
    ]
