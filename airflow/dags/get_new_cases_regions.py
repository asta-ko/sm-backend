import sys
from datetime import datetime

from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from django_operator import DjangoOperator
from tasks import collect_rf_cases, parse_rf_cases, group_cases, django_init

sys.path.append('/code')
sys.path.append('/code/oi_sud')

district_dict = {
    'Центральный': (31, 32, 33, 36, 37, 40, 44, 46, 48, 50, 57, 62, 67, 68, 69, 71, 76),
    'Северо-Западный': (10, 11, 29, 35, 39, 47, 51, 53, 60, 78, 83),
    'Дальневосточный': (3, 14, 25, 27, 28, 41, 49, 65, 75, 79),
    'Южный-и-Северо-Кавказский': (1, 8, 23, 30, 34, 61, 82, 92, 5, 6, 7, 9, 15, 26, 95),
    'Приволжский': (2, 12, 13, 16, 18, 21, 43, 52, 56, 58, 59, 63, 64, 73),
    'Уральский': (45, 66, 72, 74, 82, 94),
    'Сибирский': (4, 17, 19, 22, 24, 38, 42, 54, 55, 70)
}


def generate_tasks(v):
    kw = {}
    court = kw['court'] = v[2]
    region = court.region
    kw['instance'] = v[1]
    kw['codex'] = v[0]

    collect_task = DjangoOperator(task_id=f'{court.id}-{v[0]}-{v[1]}-get',
                                  python_callable=collect_rf_cases,
                                  priority_weight=1,
                                  retries=2,
                                  weight_rule='absolute',
                                  op_kwargs={**kw})

    parse_task = DjangoOperator(
        task_id=f'{court.id}-{v[0]}-{v[1]}-parse',
        priority_weight=3,
        weight_rule='absolute',
        python_callable=parse_rf_cases,
        op_kwargs={**kw})

    group_task = DjangoOperator(task_id=f'group_{region}', wait_for_downstream=True, python_callable=group_cases,
                                op_args=[region, ],
                                weight_rule='absolute',
                                priority_weight=0)

    collect_task >> parse_task
    parse_task >> group_task
    return collect_task


def generate_court_tasks(c):
    court_title = c.title.split(' (')[0].replace(' ', '.')
    court_task = DummyOperator(task_id=f'{court_title}', priority_weight=5,
                               weight_rule='absolute')
    variants = [('koap', 1, c), ('koap', 2, c), ('uk', 1, c), ('uk', 2, c)]
    t = [generate_tasks(v) for v in variants]
    court_task >> t
    return court_task


# 81,80

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
        regions_dict = dict(region_choices)
        for region in regions_list:
            region_name = regions_dict[region].replace(" ", ".").replace("(", "").replace(")", "")
            r = DummyOperator(task_id=region_name)
            court_tasks = [generate_court_tasks(court) for court in Court.objects.filter(region=region)]
            r >> court_tasks

    return dag


for okrug_name, regions_list in district_dict.items():
    globals()[okrug_name] = create_district_dag(f'СВЕЖЕЕ_{okrug_name}', '0 */48 * * *', regions_list)

important_regions = [78, ]

globals()['freq'] = create_district_dag(f'СВЕЖЕЕ_СПБ_И_ДРУГИЕ', '0 */4 * * *', important_regions)
