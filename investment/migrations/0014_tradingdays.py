# Generated by Django 3.1.2 on 2020-11-11 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investment', '0013_auto_20201111_1636'),
    ]

    operations = [
        migrations.CreateModel(
            name='TradingDays',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='交易日')),
            ],
            options={
                'verbose_name': 'A股交易日历',
                'verbose_name_plural': 'A股交易日历',
                'db_table': 'sma_tradingdays',
            },
        ),
    ]
