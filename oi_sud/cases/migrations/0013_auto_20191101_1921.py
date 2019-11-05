# Generated by Django 2.2.6 on 2019-11-01 19:21

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0012_auto_20191030_1029'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='linked_case_number',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=50), blank=True, null=True, size=None, verbose_name='Номер связанного дела'),
        ),
        migrations.AddField(
            model_name='case',
            name='linked_case_url',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.URLField(), blank=True, null=True, size=None, verbose_name='Ссылка на связанное дело'),
        ),
        migrations.AlterField(
            model_name='case',
            name='result_type',
            field=models.IntegerField(blank=True, choices=[(0, 'Апелляционное ПРОИЗВОДСТВО ПРЕКРАЩЕНО'), (1, 'ВОЗВРАЩЕНО ПРОКУРОРУ'), (2, 'Вынесен ПРИГОВОР'), (3, 'Вынесено другое ПОСТАНОВЛЕНИЕ'), (4, 'Направлено ПО ПОДСУДНОСТИ (подведомственности)'), (5, 'ОСТАВЛЕНО БЕЗ РАССМОТРЕНИЯ в связи с неявкой сторон'), (6, 'Представление (жалоба) ОТОЗВАНЫ'), (7, 'Применены ПРИНУДИТЕЛЬНЫЕ МЕРЫ МЕДИЦИНСКОГО ХАРАКТЕРА'), (8, 'СНЯТО с апелляционного рассмотрения'), (9, 'Уголовное дело ПРЕКРАЩЕНО'), (10, 'Отмена'), (11, 'Вынесено определение о возвращении протокола об АП и др. материалов дела в орган, долж. лицу ... в случае составления протокола и оформления других материалов дела неправомочными лицами, ...'), (12, 'Вынесено определение о передаче дела по подведомственности (ст 29.9 ч.2 п.2 и ст 29.4 ч.1 п.5)'), (13, 'Вынесено постановление о назначении административного наказания'), (14, 'Вынесено постановление о прекращении производства по делу об адм. правонарушении'), (15, 'Оставлено без изменения'), (16, 'Отменено с прекращением производства'), (17, 'Оставлено без рассмотрения'), (18, 'Отменено с возвращением на новое рассмотрение'), (19, 'Оставлено без рассмотрения в связи с пропуском срока обжалования'), (20, 'Производство по жалобе прекращено'), (21, 'Изменено'), (22, 'Отменено с направлением по подведомственности'), (23, 'Жалоба (протест) на определение (постановление) не по существу дела - рассмотрена'), (24, 'Направлено по подведомственности'), (25, 'Производство по делу прекращено'), (26, 'Вынесено определение о передаче дела судье, в орган, должностному лицу, уполномоченному ...'), (27, 'Дело присоединено к другому делу'), (28, 'ВОЗВРАЩЕНО ПРОКУРОРУ в порядке ст. 237 УПК РФ'), (29, 'Возвращено без рассмотрения'), (30, 'Возвращено без рассмотрения в связи с пропуском срока обжалования'), (31, 'Приостановлено')], null=True, verbose_name='Решение по делу'),
        ),
        migrations.AlterField(
            model_name='caseevent',
            name='result',
            field=models.IntegerField(blank=True, choices=[(0, 'Назначено предварительное слушание'), (1, 'Назначено судебное заседание'), (2, 'Рассмотрение отложено'), (3, 'Заседание отложено'), (4, 'Протокол об административном правонарушении (материалы дела) возвращен(ы)  (в пор. ст.29.4 п.4)'), (5, 'Дело возвращено прокурору'), (6, 'Возвращено без рассмотрения'), (7, 'Производство по делу прекращено'), (8, 'Производство по делу приостановлено'), (9, 'Производство прекращено'), (10, 'Вынесено постановление о назначении административного наказания'), (11, 'Вынесено постановление в порядке гл. 51 УПК (о применении ПМ медицинского характера)'), (12, 'Постановление приговора'), (13, 'Провозглашение приговора окончено'), (14, 'Оглашение резолютивной части постановления о назначении административного наказания (изготовление постановления в полном объеме отложено)'), (15, 'Передано по подведомственности'), (16, 'Оглашение резолютивной части постановления о прекращении производства (изготовление постановления в полном объеме отложено)'), (17, 'Объявлен перерыв'), (18, 'Оставлено без изменения'), (19, 'Отменено с возвращением на новое рассмотрение'), (20, 'Отменено с прекращением производства'), (21, 'Оставлено без рассмотрения'), (22, 'Оставлено без рассмотрения в связи с пропуском срока обжалования'), (23, 'Производство по жалобе прекращено'), (24, 'Изменено'), (25, 'Дело рассмотрено по существу'), (26, 'Апелляционное производство прекращено'), (27, 'Отменено с направлением по подведомственности'), (28, 'Жалоба (протест) на определение (постановление) не по существу дела - рассмотрена'), (29, 'Регистрация поступившего в суд дела'), (30, 'Суд удалился в совещательную комнату для постановления приговора'), (31, 'Передача материалов дела судье'), (32, 'Дело направлено по подсудности'), (33, 'Вынесено постановление о назначении судебного заседания'), (34, 'Решение в отношении поступившего уголовного дела'), (35, 'Предварительное слушание'), (36, 'Отзыв жалобы (представления)'), (37, 'Судебное заседание'), (38, 'Дело сдано в отдел судебного делопроизводства'), (39, 'Дело оформлено'), (40, 'Провозглашение приговора'), (41, 'Рассмотрение завершено'), (42, 'Отложено'), (44, 'Дело направлено по подведомственности прокурору, в орган следствия, дознания'), (45, 'Дело передано в архив'), (46, 'Производство по делу возобновлено'), (47, 'Назначено судебное заседание для рассмотрения ходатайства/заявления'), (48, 'Ходатайство/заявление УДОВЛЕТВОРЕНО'), (49, 'Регистрация ходатайства/заявления лица, участвующего в деле'), (50, 'Дело отправлено мировому судье'), (51, 'Снято с апелляционного рассмотрения'), (52, 'Ходатайство/заявление ОТКЛОНЕНО'), (53, 'Перерыв'), (55, 'Постановление приговора или иного судебного акта'), (56, 'Приостановлено')], null=True, verbose_name='Результат'),
        ),
        migrations.AlterField(
            model_name='caseevent',
            name='type',
            field=models.IntegerField(choices=[(0, 'Передача дела судье'), (1, 'Подготовка дела к рассмотрению'), (2, 'Рассмотрение дела по существу'), (3, 'Обращено к исполнению'), (4, 'Вступление постановления (определения) в законную силу'), (5, 'Направленная копия постановления (определения) ВРУЧЕНА'), (6, 'Вручение копии постановления (определения) в соотв. с ч. 2 ст. 29.11 КоАП РФ'), (7, 'Материалы дела сданы в отдел судебного делопроизводства'), (8, 'Направление копии постановления (определения) в соотв. с ч. 2 ст. 29.11 КоАП РФ'), (9, 'Протокол (материалы дела) НЕ БЫЛИ возвращены в ТРЕХДНЕВНЫЙ срок'), (10, 'Направленная копия постановления (определения) ВЕРНУЛАСЬ с отметкой о НЕВОЗМОЖНОСТИ ВРУЧЕНИЯ (п. 29.1 Пост. Пленума ВС от 19.12.2013 № 40)'), (11, 'Производство по делу возобновлено'), (12, 'Регистрация поступившего в суд дела'), (13, 'Передача материалов дела судье'), (14, 'Дело сдано в отдел судебного делопроизводства'), (15, 'Провозглашение приговора'), (16, 'Предварительное слушание'), (17, 'Решение в отношении поступившего уголовного дела'), (18, 'Судебное заседание'), (19, 'Сдача материалов дела в архив'), (20, 'Изготовлено постановление о назначении административного наказания в полном объеме'), (21, 'Изготовлено постановление о прекращении в полном объеме'), (22, 'Окончено производство по исполнению'), (23, 'Дело оформлено'), (24, 'Дело передано в архив'), (25, 'Материалы переданы в производство судье'), (26, 'Истребованы материалы'), (27, 'Оставлено без рассмотрения'), (28, 'Поступили истребованные материалы'), (29, 'Направление копии решения (определения) в соотв. с чч. 2, 2.1, 2.2 ст. 30.8 КоАП РФ'), (30, 'Направленная копия решения (определения) ВРУЧЕНА'), (31, 'Вступило в законную силу'), (32, 'Оставлено без рассмотрения в связи с пропуском срока обжалования'), (33, 'Направленная копия решения (определения) ВЕРНУЛАСЬ с отметкой о НЕВОЗМОЖНОСТИ ВРУЧЕНИЯ (п. 29.1 Пост. Пленума ВС от 19.12.2013 № 40)'), (34, 'Вынесено постановление о назначении судебного заседания'), (35, 'Снято с апелляционного рассмотрения'), (36, 'Дело отправлено мировому судье'), (37, 'Отзыв жалобы (представления)'), (38, 'Вручение копии решения (определения) в соотв. с чч. 2, 2.1, 2.2 ст. 30.8 КоАП РФ'), (39, 'Дело передано в экспедицию'), (40, 'Протокол (материалы дела) БЫЛИ возвращены в ТРЕХДНЕВНЫЙ срок'), (41, 'Продление срока рассмотрения'), (42, 'Материалы дела сданы в канцелярию'), (43, 'Дело сдано в канцелярию'), (44, 'Направлено по подведомственности'), (45, 'Производство по делу прекращено'), (46, 'Направленная копия постановления (определения) ВЕРНУЛАСЬ'), (47, 'Производство по жалобе прекращено'), (48, 'Судебное заседание для решения вопроса об избрании/продлении меры пресечения'), (49, 'Регистрация ходатайства/заявления лица, участвующего в деле'), (50, 'Изучение поступившего ходатайства/заявления'), (51, 'Прокурором в течение 5-суток НЕ устранены препятствия для рассмотрения дела судом'), (52, 'Дело сдано в отдел судебного делопроизводства после рассмотрения ходатайства/заявления'), (54, 'Возвращено'), (55, 'Возвращено без рассмотрения'), (56, 'Возвращено на новое рассмотрение'), (57, 'Вступило в силу'), (58, 'Вынесено на заседание Президиума'), (59, 'Вынесено определение суда апелляционной инстанции'), (60, 'Вынесено постановление суда апелляционной инстанции'), (61, 'Вынесен приговор'), (62, 'Дело истребовано'), (63, 'Дело истребовано (производство возбуждено)'), (64, 'Дело получено'), (65, 'Другое постановление с изменением решения'), (66, 'Другое постановление с отменой решения'), (67, 'Завершено'), (68, 'Зарегистрировано'), (69, 'Изменено'), (70, 'Изменить определение (постановление) частично'), (71, 'Изменить постановление (решение)'), (72, 'Изменить судебное постановление'), (73, 'Иное определение не по существу дела (районный суд)'), (74, 'Назначена беседа'), (75, 'Назначена новая беседа'), (76, 'Назначено оглашение приговора или иного судебного акта'), (77, 'Назначено постановление приговора или иного судебного акта'), (78, 'Назначено предварительное слушание'), (79, 'Назначено предварительное судебное заседание'), (80, 'Назначено судебное заседание'), (81, 'Не подано'), (82, 'Обжаловано'), (83, 'Объединено'), (84, 'Оставить определение (постановление) без изменения'), (85, 'Оставить постановление (решение) без изменения, а жалобу/протест без удовлетворения'), (86, 'Оставить приговор (или иное решение) без изменения, жалобу - без удовлетворения'), (87, 'Оставить судебное постановление без изменения, жалобу без удовлетворения'), (88, 'Оставлено без движения'), (89, 'Оставлено без изменений'), (90, 'Оставлено без изменения'), (91, 'Оставлено без рассмотрения'), (92, 'Отказано в истребовании дела'), (93, 'Отказано в принятии'), (94, 'Отказано в рассмотрении'), (95, 'Отказано в удовлетворении'), (96, 'Отклонено'), (97, 'Отложено'), (98, 'Отменено'), (99, 'Отменено апелляцией'), (100, 'Отменено по новым (в/о) обстоятельстам'), (101, 'Отменено частично'), (102, 'Отменить определение (постановление), дело возвратить прокурору, в орган следствия'), (103, 'Отменить определение (постановление), дело прекратить'), (104, 'Отменить определение (постановление) полностью, вынести новое решение'), (105, 'Отменить определение (постановление) полностью, вынести решение по существу'), (106, 'Отменить определение (постановление) полностью, дело вернуть на новое рассмотрение'), (107, 'Отменить определение (постановление) частично, вынести решение по существу'), (108, 'Отменить определение (постановление) частично, дело вернуть на новое рассмотрение'), (109, 'Отменить постановление (решение), дело вернуть на новое рассмотрение'), (110, 'Отменить постановление (решение), дело направить на рассмотрение по подведомственности'), (111, 'Отменить постановление (решение), дело направить на рассмотрение по подсудности'), (112, 'Отменить постановление (решение), дело прекратить'), (113, 'Отменить судебное постановление полностью, дело направить на новое рассмотрение'), (114, 'Отменить судебное постановление полностью, дело направить по подведомственности'), (115, 'Отменить судебное постановление полностью, дело направить по подсудности'), (116, 'Отменить судебное постановление полностью, оставить заявление без рассмотрения'), (117, 'Отменить судебное постановление полностью, прекратить производство по делу'), (118, 'Отменить судебное постановление полностью, принять новое решение'), (119, 'Отменить судебное постановление частично, дело направить на новое рассмотрение'), (120, 'Отменить судебное постановление частично, дело направить по подведомственности '), (121, 'Отменить судебное постановление частично, дело направить по подсудности'), (122, 'Отменить судебное постановление частично, оставить заявление без рассмотрения'), (123, 'Отменить судебное постановление частично, прекратить производство по делу'), (124, 'Отменить судебное постановление частично, принять новое решение'), (125, 'Отозвано'), (126, 'Передано в другой орган'), (127, 'Передано в иной орган'), (128, 'Передано по подведомственности'), (129, 'Передано по подведомственности '), (130, 'Передано по подсудности'), (131, 'Перерыв'), (132, 'Подготовка к рассмотрению'), (133, 'Постановление приговора'), (134, 'Постановление (решение) не пересматривалось'), (135, 'Прекращено'), (136, 'Принудительные меры к невменяемому'), (137, 'Принудительные меры к невменяемым'), (138, 'Принято к рассмотрению'), (139, 'Приостановлено'), (140, 'Присоединено'), (141, 'Проведена беседа'), (142, 'Рассмотрение'), (143, 'Рассмотрено'), (144, 'Решение не по существу не пересматривалось'), (145, 'Снято с рассмотрения'), (146, 'Удовлетворено'), (147, 'Удовлетворено частично'), (148, 'Предварительное судебное заседание'), (149, 'Оглашение приговора или иного судебного акта')], verbose_name='Тип'),
        ),
    ]
