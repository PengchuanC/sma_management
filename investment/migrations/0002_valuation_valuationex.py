# Generated by Django 4.0.1 on 2022-02-26 15:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('investment', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Valuation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asset', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='资产合计')),
                ('debt', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='负债合计')),
                ('net_asset', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='资产净值')),
                ('unit_nav', models.DecimalField(decimal_places=4, default=0, max_digits=10, verbose_name='单位净值')),
                ('accu_nav', models.DecimalField(decimal_places=4, default=0, max_digits=10, verbose_name='累计净值')),
                ('nav_increment', models.DecimalField(decimal_places=4, default=0, max_digits=10, verbose_name='净值日增长率')),
                ('date', models.DateField(verbose_name='业务日期')),
                ('port_code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='investment.portfolio', to_field='port_code', verbose_name='产品代码')),
            ],
            options={
                'verbose_name': '5.1 基金估值表',
                'verbose_name_plural': '5.1 基金估值表',
                'db_table': 'sma_balance',
                'unique_together': {('port_code', 'date')},
            },
        ),
        migrations.CreateModel(
            name='ValuationEx',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('savings', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='银行存款')),
                ('settlement_reserve', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='结算备付金')),
                ('deposit', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='存出保证金')),
                ('stocks', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='股票投资')),
                ('bonds', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='债券投资')),
                ('abs', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='资产支持证券投资')),
                ('funds', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='基金投资')),
                ('metals', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='贵金属投资')),
                ('other', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='其他投资')),
                ('resale_agreements', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='买入返售金融资产')),
                ('purchase_rec', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='应收申购款')),
                ('ransom_pay', models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='应付赎回款')),
                ('date', models.DateField(verbose_name='业务日期')),
                ('port_code', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='investment.valuation', verbose_name='产品代码')),
            ],
            options={
                'verbose_name': '5.2 基金估值表细项',
                'verbose_name_plural': '5.2 基金估值表细项',
                'db_table': 'sma_balance_expanded',
                'unique_together': {('port_code', 'date')},
            },
        ),
    ]
