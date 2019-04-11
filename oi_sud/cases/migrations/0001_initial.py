# Generated by Django 2.2 on 2019-04-11 08:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('courts', '0003_auto_20190402_0227'),
        ('codex', '0003_codexarticle_m_judge'),
    ]

    operations = [
        migrations.CreateModel(
            name='Advocate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
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
                ('case_number', models.CharField(max_length=50)),
                ('case_uid', models.CharField(blank=True, max_length=50, null=True)),
                ('protocol_number', models.CharField(blank=True, max_length=50, null=True)),
                ('result_text', models.TextField(blank=True, null=True)),
                ('type', models.IntegerField(choices=[(1, 'Дело об административном правонарушении'), (2, 'Уголовное дело'), (3, 'Производство по материалам')])),
                ('stage', models.IntegerField(choices=[(1, 'Первая инстанция'), (2, 'Аппеляция'), (3, 'Пересмотр')])),
                ('url', models.URLField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CaseGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
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
                ('gender', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CaseEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('date', models.DateTimeField()),
                ('type', models.IntegerField(choices=[(0, 'Передача дела судье'), (1, 'Подготовка дела к рассмотрению'), (2, 'Рассмотрение дела по существу'), (3, 'Обращено к исполнению'), (4, 'Вступление постановления (определения) в законную силу'), (5, 'Направленная копия постановления (определения) ВРУЧЕНА'), (6, 'Вручение копии постановления (определения) в соотв. с ч. 2 ст. 29.11 КоАП РФ'), (7, 'Материалы дела сданы в отдел судебного делопроизводства'), (8, 'Направление копии постановления (определения) в соотв. с ч. 2 ст. 29.11 КоАП РФ'), (9, 'Протокол (материалы дела) НЕ БЫЛИ возвращены в ТРЕХДНЕВНЫЙ срок'), (10, 'Направленная копия постановления (определения) ВЕРНУЛАСЬ с отметкой о НЕВОЗМОЖНОСТИ ВРУЧЕНИЯ (п. 29.1 Пост. Пленума ВС от 19.12.2013 № 40)'), (11, 'Производство по делу возобновлено'), (12, 'Регистрация поступившего в суд дела'), (13, 'Передача материалов дела судье'), (14, 'Дело сдано в отдел судебного делопроизводства'), (15, 'Провозглашение приговора'), (16, 'Предварительное слушание'), (17, 'Решение в отношении поступившего уголовного дела'), (18, 'Судебное заседание'), (19, 'Сдача материалов дела в архив')])),
                ('result', models.IntegerField(blank=True, choices=[(0, 'Назначено предварительное слушание'), (1, 'Назначено судебное заседание'), (2, 'Рассмотрение отложено'), (3, 'Заседание отложено'), (4, 'Протокол об административном правонарушении (материалы дела) возвращен(ы)  (в пор. ст.29.4 п.4)'), (5, 'Дело возвращено прокурору'), (6, 'Возвращено без рассмотрения'), (7, 'Производство по делу прекращено'), (8, 'Производство по делу приостановлено'), (9, 'Производство прекращено'), (10, 'Вынесено постановление о назначении административного наказания'), (11, 'Вынесено постановление в порядке гл. 51 УПК (о применении ПМ медицинского характера)'), (12, 'Постановление приговора'), (13, 'Провозглашение приговора окончено')], null=True)),
                ('courtroom', models.IntegerField(blank=True, null=True)),
                ('case', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cases.Case')),
            ],
        ),
        migrations.CreateModel(
            name='CaseDefense',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('advocate', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cases.Advocate')),
                ('case', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cases.Case')),
                ('codex_articles', models.ManyToManyField(to='codex.CodexArticle')),
                ('defendant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cases.Defendant')),
            ],
        ),
        migrations.AddField(
            model_name='case',
            name='advocates',
            field=models.ManyToManyField(through='cases.CaseDefense', to='cases.Advocate'),
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
            field=models.ManyToManyField(through='cases.CaseDefense', to='cases.Defendant'),
        ),
        migrations.AddField(
            model_name='case',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cases.CaseGroup'),
        ),
        migrations.AddField(
            model_name='case',
            name='judge',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='courts.Judge'),
        ),
    ]
