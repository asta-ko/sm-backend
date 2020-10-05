import os
import sys

from airflow.operators.python_operator import PythonOperator

DJANGO_ENVIRONMENT_SETUP_DONE = False


def setup_django_for_airflow(path_to_settings_py: str, settings_file_name: str):
    global DJANGO_ENVIRONMENT_SETUP_DONE

    if DJANGO_ENVIRONMENT_SETUP_DONE:
        return

    base_directory = os.path.dirname(path_to_settings_py)

    # Add Django project root to path
    sys.path.append('/code/')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"oi_sud.config.{settings_file_name}")

    import django
    django.setup()

    DJANGO_ENVIRONMENT_SETUP_DONE = True


class DjangoOperator(PythonOperator):
    path_to_settings_py: str = os.getenv("AIRFLOW_DJANGO_PATH_TO_SETTINGS_PY", "/code/oi_sud/config")

    def pre_execute(self, *args, **kwargs):
        setup_django_for_airflow(self.path_to_settings_py, "tasks_airflow")
