# Generated by Django 3.1.5 on 2021-01-06 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investment', '0044_prevaluednav'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prevaluednav',
            name='value',
            field=models.DecimalField(decimal_places=6, max_digits=8, verbose_name='预估净值'),
        ),
    ]
