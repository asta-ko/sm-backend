# Generated by Django 2.2.4 on 2019-09-09 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courts', '0003_court_not_available'),
    ]

    operations = [
        migrations.AddField(
            model_name='court',
            name='servers_num',
            field=models.IntegerField(blank=True, default=1, null=True, verbose_name='Количество серверов'),
        ),
    ]
