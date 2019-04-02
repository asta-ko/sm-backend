import os
from django.conf import settings

import celery

# import raven
# from raven.contrib.celery import register_logger_signal, register_signal

C_PROJECT_STACK = os.environ.get('C_PROJECT_STACK', 'dev')


class Celery(celery.Celery):

    def on_configure(self):
        pass
        # client = raven.Client(**settings.RAVEN_CONFIG)
        #
        # # register a custom filter to filter out duplicate logs
        # register_logger_signal(client)
        #
        # # hook into the Celery error handler
        # register_signal(client)


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'oi_sud.config.{C_PROJECT_STACK}')

app = Celery('oi_sud')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
