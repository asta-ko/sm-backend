# Generated by Django 2.2 on 2019-05-14 13:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0005_auto_20190514_0856'),
    ]

    operations = [
        migrations.CreateModel(
            name='LinkedCasesProxy',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('cases.case_linked_cases',),
        ),
    ]
