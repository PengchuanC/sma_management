# Generated by Django 3.1.2 on 2020-11-19 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investment', '0023_fundpurchasefee'),
    ]

    operations = [
        migrations.AddField(
            model_name='fundpurchasefee',
            name='operate',
            field=models.CharField(choices=[('买', 'buy'), ('卖', 'sell')], default='buy', max_length=4),
            preserve_default=False,
        ),
    ]