# Generated by Django 2.2.1 on 2019-05-15 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0007_auto_20190515_0911'),
    ]

    operations = [
        migrations.AddField(
            model_name='defendant',
            name='first_name',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='defendant',
            name='last_name',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='defendant',
            name='middle_name',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
