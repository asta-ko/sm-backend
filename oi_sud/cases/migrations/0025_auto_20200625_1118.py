# Generated by Django 2.2.8 on 2020-06-25 11:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0024_auto_20200623_2111_squashed_0028_auto_20200624_1127'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='actual_url_unknown',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='case',
            name='linked_cases',
            field=models.ManyToManyField(related_name='_case_linked_cases_+', to='cases.Case'),
        ),
        migrations.AlterField(
            model_name='casedefense',
            name='advocates',
            field=models.ManyToManyField(related_name='a_defenses', to='cases.Advocate', verbose_name='Адвокаты'),
        ),
        migrations.AlterField(
            model_name='casedefense',
            name='case',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='defenses', to='cases.Case'),
        ),
        migrations.AlterField(
            model_name='casedefense',
            name='prosecutors',
            field=models.ManyToManyField(related_name='p_defenses', to='cases.Prosecutor', verbose_name='Прокуроры'),
        ),
    ]
