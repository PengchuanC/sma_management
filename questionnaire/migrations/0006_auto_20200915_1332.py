# Generated by Django 3.1 on 2020-09-15 13:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaire', '0005_auto_20200915_1227'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='associate_account',
            field=models.CharField(max_length=30, null=True, verbose_name='关联账号'),
        ),
        migrations.AlterField(
            model_name='client',
            name='associate_name',
            field=models.CharField(max_length=20, null=True, verbose_name='关联账户名称'),
        ),
    ]