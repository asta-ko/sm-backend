import sys
from datetime import datetime

from airflow import DAG
from django_operator import DjangoOperator
from tasks import mark_risk_group, django_init

sys.path.append('/code')
sys.path.append('/code/oi_sud')

schedule = '@daily'

with DAG('Группы_риска_ВСЁ',
         schedule_interval=schedule,
         start_date=datetime(2018, 11, 1),
         catchup=False,
         default_args={'owner': 'airflow'}) as dag:
    django_init()

    from oi_sud.core.consts import region_choices

    regions_dict = dict(region_choices)
    for region, name in regions_dict.items():
        region_name = name.replace(" ", ".").replace("(", "").replace(")", "")
        DjangoOperator(task_id=f'risk-{region_name}',
                       python_callable=mark_risk_group,
                       op_args=[region, ])
