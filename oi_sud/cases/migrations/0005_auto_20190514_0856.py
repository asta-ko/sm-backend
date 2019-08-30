# Generated by Django 2.2 on 2019-05-14 08:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0004_auto_20190429_1800'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='case',
            name='group',
        ),
        migrations.AddField(
            model_name='case',
            name='linked_cases',
            field=models.ManyToManyField(related_name='_case_linked_cases_+', to='cases.Case'),
        ),
        migrations.AlterField(
            model_name='case',
            name='appeal_result',
            field=models.IntegerField(blank=True, choices=[(1, 'Отмена'), (2, 'Жалоба (протест) на определение (постановление) не по существу дела - рассмотрена'), (3, 'Изменено'), (4, 'Направлено по подведомственности'), (5, 'Оставлено без изменения'), (6, 'Оставлено без рассмотрения'), (7, 'Оставлено без рассмотрения в связи с пропуском срока обжалования'), (8, 'Отменено с возвращением на новое рассмотрение'), (9, 'Отменено с направлением по подведомственности'), (10, 'Отменено с прекращением производства'), (11, 'Производство по жалобе прекращено'), (12, 'вынесено иное определение не по существу дела'), (13, 'Без изменения'), (14, 'Отменено с возвращением дела на новое рассмотрение'), (15, 'Отменено с прекращением производства по делу'), (16, 'Оставлено без рассмотрения или возвращено'), (17, 'производство прекращено'), (18, 'Отменено')], null=True, verbose_name='Результат обжалования'),
        ),
        migrations.AlterField(
            model_name='caseevent',
            name='type',
            field=models.IntegerField(choices=[(0, 'Передача дела судье'), (1, 'Подготовка дела к рассмотрению'), (2, 'Рассмотрение дела по существу'), (3, 'Обращено к исполнению'), (4, 'Вступление постановления (определения) в законную силу'), (5, 'Направленная копия постановления (определения) ВРУЧЕНА'), (6, 'Вручение копии постановления (определения) в соотв. с ч. 2 ст. 29.11 КоАП РФ'), (7, 'Материалы дела сданы в отдел судебного делопроизводства'), (8, 'Направление копии постановления (определения) в соотв. с ч. 2 ст. 29.11 КоАП РФ'), (9, 'Протокол (материалы дела) НЕ БЫЛИ возвращены в ТРЕХДНЕВНЫЙ срок'), (10, 'Направленная копия постановления (определения) ВЕРНУЛАСЬ с отметкой о НЕВОЗМОЖНОСТИ ВРУЧЕНИЯ (п. 29.1 Пост. Пленума ВС от 19.12.2013 № 40)'), (11, 'Производство по делу возобновлено'), (12, 'Регистрация поступившего в суд дела'), (13, 'Передача материалов дела судье'), (14, 'Дело сдано в отдел судебного делопроизводства'), (15, 'Провозглашение приговора'), (16, 'Предварительное слушание'), (17, 'Решение в отношении поступившего уголовного дела'), (18, 'Судебное заседание'), (19, 'Сдача материалов дела в архив'), (20, 'Изготовлено постановление о назначении административного наказания в полном объеме'), (21, 'Изготовлено постановление о прекращении в полном объеме'), (22, 'Окончено производство по исполнению'), (23, 'Дело оформлено'), (24, 'Дело передано в архив'), (25, 'Материалы переданы в производство судье'), (26, 'Истребованы материалы'), (27, 'Оставлено без рассмотрения'), (28, 'Поступили истребованные материалы'), (29, 'Направление копии решения (определения) в соотв. с чч. 2, 2.1, 2.2 ст. 30.8 КоАП РФ'), (30, 'Направленная копия решения (определения) ВРУЧЕНА'), (31, 'Вступило в законную силу'), (32, 'Оставлено без рассмотрения в связи с пропуском срока обжалования'), (33, 'Направленная копия решения (определения) ВЕРНУЛАСЬ с отметкой о НЕВОЗМОЖНОСТИ ВРУЧЕНИЯ (п. 29.1 Пост. Пленума ВС от 19.12.2013 № 40)'), (34, 'Вынесено постановление о назначении судебного заседания'), (35, 'Снято с апелляционного рассмотрения'), (36, 'Дело отправлено мировому судье'), (37, 'Отзыв жалобы (представления)'), (38, 'Вручение копии решения (определения) в соотв. с чч. 2, 2.1, 2.2 ст. 30.8 КоАП РФ'), (39, 'Дело передано в экспедицию'), (40, 'Протокол (материалы дела) БЫЛИ возвращены в ТРЕХДНЕВНЫЙ срок'), (41, 'Продление срока рассмотрения')], verbose_name='Тип'),
        ),
        migrations.DeleteModel(
            name='CaseGroup',
        ),
    ]
