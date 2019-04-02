# Generated by Django 2.1.7 on 2019-04-02 02:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('courts', '0003_auto_20190402_0227'),
        ('codex', '0002_auto_20190401_2044'),
    ]

    operations = [
        migrations.CreateModel(
            name='Case',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('entry_date', models.DateTimeField()),
                ('result_date', models.DateTimeField(blank=True, null=True)),
                ('result_published', models.DateTimeField(blank=True, null=True)),
                ('result_valid', models.DateTimeField(blank=True, null=True)),
                ('case_id', models.CharField(max_length=20, unique=True)),
                ('system_id', models.CharField(max_length=20, unique=True)),
                ('protocol_number', models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ('result_text', models.TextField(blank=True, null=True)),
                ('case_type', models.IntegerField(choices=[(1, 'Дело об административном правонарушении'), (2, 'Уголовное дело'), (3, 'Производство по материалам')])),
                ('case_stage', models.IntegerField(choices=[(1, 'Первая инстанция'), (2, 'Аппеляция'), (3, 'Пересмотр')])),
            ],
        ),
        migrations.CreateModel(
            name='CaseEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField()),
                ('date', models.DateTimeField()),
                ('type', models.IntegerField()),
                ('result', models.IntegerField()),
                ('courtroom', models.IntegerField()),
                ('case', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cases.Case')),
            ],
        ),
        migrations.CreateModel(
            name='CaseGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('second_inst', models.BooleanField()),
                ('third_inst', models.BooleanField()),
                ('revision', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Defendant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=50)),
                ('region', models.IntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='case',
            name='case_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cases.CaseGroup'),
        ),
        migrations.AddField(
            model_name='case',
            name='codex_articles',
            field=models.ManyToManyField(to='codex.CodexArticle'),
        ),
        migrations.AddField(
            model_name='case',
            name='court',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courts.Court'),
        ),
        migrations.AddField(
            model_name='case',
            name='defendants',
            field=models.ManyToManyField(to='cases.Defendant'),
        ),
        migrations.AddField(
            model_name='case',
            name='judge',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courts.Judge'),
        ),
    ]
