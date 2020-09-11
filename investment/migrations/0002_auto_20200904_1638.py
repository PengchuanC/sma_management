# Generated by Django 3.1 on 2020-09-04 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investment', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='indexquote',
            options={'get_latest_by': 'date', 'verbose_name': '指数行情', 'verbose_name_plural': '指数行情'},
        ),
        migrations.AddField(
            model_name='indexbasicinfo',
            name='component',
            field=models.CharField(default=None, max_length=20, verbose_name='指数成分类别'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='indexbasicinfo',
            name='category',
            field=models.CharField(max_length=20, verbose_name='指数类别'),
        ),
    ]
