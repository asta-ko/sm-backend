# Generated by Django 2.2.1 on 2019-05-16 13:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0008_auto_20190515_1450'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='defendants',
            field=models.ManyToManyField(related_name='cases', through='cases.CaseDefense', to='cases.Defendant'),
        ),
        migrations.AlterField(
            model_name='casedefense',
            name='defendant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='defenses', to='cases.Defendant', verbose_name='Ответчик'),
        ),
        migrations.AlterField(
            model_name='defendant',
            name='gender',
            field=models.IntegerField(blank=True, choices=[(1, 'Ж'), (2, 'М')], null=True),
        ),
        migrations.AlterUniqueTogether(
            name='defendant',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='defendant',
            name='name',
        ),
    ]