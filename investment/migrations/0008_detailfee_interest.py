# Generated by Django 3.1.2 on 2020-11-06 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investment', '0007_auto_20201106_1346'),
    ]

    operations = [
        migrations.AddField(
            model_name='detailfee',
            name='interest',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=18, verbose_name='应收利息'),
        ),
    ]