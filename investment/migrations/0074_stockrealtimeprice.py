# Generated by Django 3.2.4 on 2021-06-24 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investment', '0073_delete_stockrealtimeprice'),
    ]

    operations = [
        migrations.CreateModel(
            name='StockRealtimePrice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('secucode', models.CharField(max_length=12, verbose_name='股票代码')),
                ('prev_close', models.DecimalField(decimal_places=4, max_digits=10, null=True, verbose_name='昨收')),
                ('price', models.DecimalField(decimal_places=4, max_digits=10, null=True, verbose_name='实时价格')),
                ('date', models.DateField(verbose_name='日期')),
                ('time', models.TimeField(verbose_name='时间')),
            ],
            options={
                'verbose_name': '股票实时价格',
                'verbose_name_plural': '股票实时价格',
                'db_table': 'sma_stocks_realtime_price',
                'get_latest_by': 'id',
            },
        ),
    ]
