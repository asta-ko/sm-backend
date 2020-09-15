## Курсовой проект

- [Короткое описание и задачи](https://www.notion.so/DE-f0552bc9b80441fab4474934d3aa6f5e)
- [Презентация проекта](https://docs.google.com/presentation/d/14MMPzufBBZvvILmaqUBUKyn-dAkJeia3A2Duk0f_EAI/edit?usp=sharing)

## Установка


1) если не установлены docker и docker-compose, устанавливаем:

- https://docs.docker.com/install/linux/docker-ce/ubuntu/
- https://docs.docker.com/compose/install/

2) получаем нужную структуру файлов:

`mkdir ovdinfo_sudmonster && cd ovdinfo_sudmonster`

`git clone git@github.com:asta-ko/sm-backend.git && git clone git@github.com:ovdinfo/sm-frontend.git`

`mv backend sudmonster && cd frontend && cp env.orig .env && cd ../sudmonster && git checkout develop && cp env.orig .env`  - 

3) создаем и запускаем контейнеры

`./run.sh stack`

4) готовим базу

`docker-compose exec backend python -m oi_sud migrate && docker-compose exec backend python -m oi_sud collectstatic` - проводим миграции и копируем статику

`docker-compose exec backend python -m oi_sud createsuperuser` - создаём суперюзера

`docker-compose exec backend python -m oi_sud loaddata courts.json && docker-compose exec backend python -m oi_sud loaddata codex.json` - разворачиваем дамп

`docker-compose exec backend python -m oi_sud get_cases koap 1 --region 78 --limit 1 &&
docker-compose exec backend python -m oi_sud get_cases uk 1 --region 78 --limit 1` - получаем некоторые дела

5) судмонстр доступен по 127.0.0.1:8082/admin (django-админка) и 127.0.0.1:3000 (фронт) 
