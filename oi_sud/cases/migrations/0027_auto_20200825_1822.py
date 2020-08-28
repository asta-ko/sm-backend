# Generated by Django 2.2.8 on 2020-08-25 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0026_case_duplicate'),
    ]

    operations = [
        migrations.AddField(
            model_name='defendant',
            name='risk_group',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='casepenalty',
            name='type',
            field=models.CharField(blank=True, choices=[('fine', 'Штраф'), ('works', 'Обязательные работы'), ('arrest', 'Арест'), ('term', 'Срок'), ('other', 'Другое'), ('caution', 'Предупреждение'), ('suspension', 'Приостановление деятельности'), ('no_data', 'Нет данных'), ('error', 'Ошибка')], db_index=True, max_length=10, null=True),
        ),
    ]
