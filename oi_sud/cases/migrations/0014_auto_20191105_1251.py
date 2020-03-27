# Generated by Django 2.2.6 on 2019-11-05 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0013_auto_20191101_1921'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='appeal_result',
            field=models.CharField(blank=True, max_length=120, null=True, verbose_name='Результат обжалования'),
        ),
        migrations.AlterField(
            model_name='case',
            name='result_type',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Решение по делу'),
        ),
        migrations.AlterField(
            model_name='caseevent',
            name='result',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Результат'),
        ),
        migrations.AlterField(
            model_name='caseevent',
            name='type',
            field=models.CharField(max_length=200, verbose_name='Тип'),
        ),
    ]