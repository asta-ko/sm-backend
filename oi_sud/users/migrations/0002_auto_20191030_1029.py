# Generated by Django 2.2.6 on 2019-10-30 10:29

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='regions',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True, null=True), blank=True, null=True, size=None, verbose_name='Регионы'),
        ),
    ]
