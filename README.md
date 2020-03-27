как запустить судмонстра
1) если не установлены docker и docker-compose, установить
- https://docs.docker.com/install/linux/docker-ce/ubuntu/
- https://docs.docker.com/compose/install/

2) склонировать код
git clone https://gitlab.com/ovdinfo/oi-sud-monster.git или
git clone git@gitlab.com:ovdinfo/oi-sud-monster.git

3) в папку oi-sud-monster положить конфиг .env:
cd oi-sud-monster && cp env.orig .env

5) запустить ./run.sh stack

6) провести миграции docker-compose exec backend python -m oi_sud migrate

7) создать юзера для админки
docker-compose exec backend python -m oi_sud createsuperuser

8) закачать суды и статьи
docker-compose exec backend python -m oi_sud loaddata courts.json
docker-compose exec backend python -m oi_sud loaddata codex.json

9) получить некоторые дела
docker-compose exec backend python -m oi_sud get_cases koap 1 --region 78 --limit 3 - административки, первая инстанция, Санкт-Петербург
docker-compose exec backend python -m oi_sud get_cases uk 1 --region 78 --limit 3 - уголовки, первая инстанция, Санкт-Петербург

10) вы великолепны! судмонстр доступен по http://127.0.0.1:8082/admin/