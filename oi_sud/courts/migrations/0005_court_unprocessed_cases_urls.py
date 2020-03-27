# Generated by Django 2.2.6 on 2019-10-04 20:42

import django.contrib.postgres.fields
from django.db import migrations, models
import oi_sud.courts.models


class Migration(migrations.Migration):

    dependencies = [
        ('courts', '0004_court_servers_num'),
    ]

    operations = [
        migrations.AddField(
            model_name='court',
            name='unprocessed_cases_urls',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, default=oi_sud.courts.models.new_array, size=None, verbose_name='Дела для обработки'),
        ),
    ]