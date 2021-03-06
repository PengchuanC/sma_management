# Generated by Django 3.1.5 on 2021-02-19 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investment', '0054_remove_fundposestimate_secucode'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fundassetallocate',
            options={'get_latest_by': 'date', 'verbose_name': '基金资产配置', 'verbose_name_plural': '基金资产配置'},
        ),
        migrations.AlterModelOptions(
            name='fundposestimate',
            options={'get_latest_by': 'date', 'verbose_name': '基金仓位估算', 'verbose_name_plural': '基金仓位估算'},
        ),
        migrations.AlterModelOptions(
            name='fundprice',
            options={'get_latest_by': 'date', 'verbose_name': '基金累计净值表', 'verbose_name_plural': '基金累计净值表'},
        ),
        migrations.AddField(
            model_name='fundassetallocate',
            name='other',
            field=models.DecimalField(decimal_places=6, default=0, max_digits=18, verbose_name='其他投资'),
        ),
    ]
