# Generated by Django 3.1.2 on 2020-12-07 15:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('investment', '0036_auto_20201207_1405'),
    ]

    operations = [
        migrations.CreateModel(
            name='PortfolioBrinson',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index', models.CharField(max_length=20, verbose_name='指数代码')),
                ('date', models.DateField(verbose_name='日期')),
                ('q1', models.DecimalField(decimal_places=8, max_digits=12, verbose_name='q1')),
                ('q2', models.DecimalField(decimal_places=8, max_digits=12, verbose_name='q2')),
                ('q3', models.DecimalField(decimal_places=8, max_digits=12, verbose_name='q3')),
                ('q4', models.DecimalField(decimal_places=8, max_digits=12, verbose_name='q4')),
                ('port_code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='investment.portfolio', to_field='port_code', verbose_name='组合代码')),
            ],
            options={
                'verbose_name': '组合Brinson',
                'verbose_name_plural': '组合Brinson',
                'db_table': 'sma_brinson',
            },
        ),
    ]