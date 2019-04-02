# Generated by Django 2.1.7 on 2019-03-27 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='court',
            name='instance',
            field=models.IntegerField(choices=[(1, 'Суд первой инстанции'), (2, 'Суд второй инстанции')], default=1),
        ),
        migrations.AlterField(
            model_name='court',
            name='type',
            field=models.IntegerField(choices=[(0, 'Районный суд'), (1, 'Городской суд'), (2, 'Городской суд (федерального значения)'), (3, 'Областной суд'), (4, 'Краевой суд'), (5, 'Гарнизонный военный суд'), (6, 'Окружной военный (флотский) суд'), (7, 'Суд автономного округа'), (8, 'Суд автономной области')]),
        ),
    ]
