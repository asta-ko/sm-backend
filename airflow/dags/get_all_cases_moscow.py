import sys
from datetime import datetime

from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from django_operator import DjangoOperator
from tasks import collect_moscow_cases, parse_moscow_cases, django_init, group_cases

sys.path.append('/code')
sys.path.append('/code/oi_sud')

dag_id = 'ВСЁ_Москва'
schedule = '@once'

group_task = DjangoOperator(task_id='group', wait_for_downstream=True, python_callable=group_cases, op_args=[77, ],
                            weight_rule='absolute',
                            priority_weight=0)


def generate_tasks(v, year):
    kw = {}
    court = kw['court'] = v[2]
    kw['instance'] = v[1]
    kw['codex'] = v[0]
    kw['date_from'] = f'01.01.{year}'
    kw['date_to'] = f'31.12.{year}'

    collect_task = DjangoOperator(task_id=f'{court.id}-{v[0]}-{v[1]}-get-{year}',
                                  python_callable=collect_moscow_cases,
                                  priority_weight=1,
                                  retries=2,
                                  weight_rule='absolute',
                                  op_kwargs={**kw})

    parse_task = DjangoOperator(
        task_id=f'{court.id}-{v[0]}-{v[1]}-parse-{year}',
        priority_weight=3,
        weight_rule='absolute',
        python_callable=parse_moscow_cases,
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


with DAG(dag_id,
         schedule_interval=schedule,
         start_date=datetime(2018, 11, 1),
         catchup=False,
         default_args={'owner': 'airflow', 'provide_context': True}) as dag:
    django_init()
    from oi_sud.courts.models import Court

    court_tasks = [generate_court_tasks(c) for c in Court.objects.filter(region=77)[:2]]
