import sys

sys.path.append('/code')
sys.path.append('/code/oi_sud')

from datetime import datetime

from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from django_operator import DjangoOperator

from tasks import collect_rf_cases, parse_rf_cases, django_init, group_cases

district_dict = {
    'Центральный': (31, 32, 33, 36, 37, 40, 44, 46, 48, 50, 57, 62, 67, 68, 69, 71, 76, 77),
    'Северо-Западный': (10, 11, 29, 35, 39, 47, 51, 53, 60, 78, 83),
    'Дальневосточный': (3, 14, 25, 27, 28, 41, 49, 65, 75, 79),
    'Южный-и-Северо-Кавказский': (1, 8, 23, 30, 34, 61, 82, 92, 5, 6, 7, 9, 15, 26, 95),
    'Приволжский': (2, 12, 13, 16, 18, 21, 43, 52, 56, 58, 59, 63, 64, 73),
    'Уральский': (45, 66, 72, 74, 82, 94),
    'Сибирский': (4, 17, 19, 22, 24, 38, 42, 54, 55, 70)
}


# 81,80

def generate_tasks(v, year):
    kw = {}
    court = kw['court'] = v[2]
    region = court.region
    kw['instance'] = v[1]
    kw['codex'] = v[0]
    kw['date_from'] = f'01.01.{year}'
    kw['date_to'] = f'31.12.{year}'

    collect_task = DjangoOperator(task_id=f'{court.id}-{v[0]}-{v[1]}-get-{year}',
                                  python_callable=collect_rf_cases,
                                  priority_weight=1,
                                  retries=2,
                                  weight_rule='absolute',
                                  op_kwargs={**kw})

    group_task = DjangoOperator(task_id=f'group_{region}_all', wait_for_downstream=True, python_callable=group_cases,
                                op_args=[region, ],
                                weight_rule='absolute',
                                priority_weight=0)

    parse_task = DjangoOperator(
        task_id=f'{court.id}-{v[0]}-{v[1]}-parse-{year}',
        priority_weight=3,
        weight_rule='absolute',
        python_callable=parse_rf_cases,
        op_kwargs={**kw})

    collect_task >> parse_task
    parse_task >> group_task
    return collect_task


def generate_court_tasks(c):
    court_title = c.title.split(' (')[0].replace(' ', '.')
    court_task = DummyOperator(task_id=f'{court_title}', priority_weight=5,
                               weight_rule='absolute')

    for year in range(2009, datetime.now().year + 1):
        year_task = DummyOperator(task_id=f'{year}__{c.id}', priority_weight=5,
                                  weight_rule='absolute')

        variants = [('koap', 1, c), ('koap', 2, c), ('uk', 1, c), ('uk', 2, c)]

        t = [generate_tasks(v, year) for v in variants]
        court_task >> year_task >> t
    return court_task


def create_district_dag(dag_id,
                        schedule,
                        regions_list):
    django_init()

    from oi_sud.courts.models import Court
    from oi_sud.core.consts import region_choices

    dag = DAG(dag_id,
              schedule_interval=schedule,
              start_date=datetime(2018, 11, 1),
              catchup=False,
              default_args={'owner': 'airflow'})

    with dag:
        django_init()

        regions_dict = dict(region_choices)
        for region in regions_list:
            region_name = regions_dict[region].replace(" ", ".").replace("(", "").replace(")", "")
            r = DummyOperator(task_id=region_name)

            court_tasks = [generate_court_tasks(court) for court in Court.objects.filter(region=region)]
            r >> court_tasks

    return dag


for okrug_name, regions_list in district_dict.items():
    globals()[okrug_name] = create_district_dag(f'ВСЁ_{okrug_name}', '@once', regions_list)
