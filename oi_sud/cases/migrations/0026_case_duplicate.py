# Generated by Django 2.2.8 on 2020-06-27 19:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0025_auto_20200625_1118'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='duplicate',
            field=models.BooleanField(default=False),
        ),
    ]
