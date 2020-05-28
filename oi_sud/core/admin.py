import json

import requests
from django.http import HttpResponse
from django.shortcuts import render
from django.template.defaulttags import register
from oi_sud.celery import app


@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)


def admin_celery_view(request):
    r = requests.get('http://flower:8888/api/tasks?state=STARTED')

    arr = []
    for k, v in r.json().items():
        arr.append(v)
    context = {
        'title': 'Celery running tasks',
        'tasks': arr,
        }

    template = 'admin/celery_tasks.html'
    return render(request, template, context)


# admin.site.unregister(User)
# admin.site.unregister(Group)


PROGRESS_STATE = 'PROGRESS'


class Progress(object):

    def __init__(self, task_id):
        self.task_id = task_id
        self.result = app.AsyncResult(task_id)

    def get_info(self):
        if self.result.state in ['SUCCESS']:
            # success = self.result.successful()
            return {
                'complete': True,
                'success': True,
                'progress': _get_completed_progress(),
                # 'result': self.result.get(self.task_id) if success else None,
                }
        elif self.result.state == PROGRESS_STATE:
            return {
                'complete': False,
                'success': None,
                'progress': self.result.info,
                }
        elif self.result.state in ['PENDING', 'STARTED']:
            return {
                'complete': False,
                'success': None,
                'progress': _get_unknown_progress(),
                }
        return self.result.info


def get_progress(request, task_id):
    progress = Progress(task_id)
    return HttpResponse(json.dumps(progress.get_info()), content_type='application/json')


def _get_completed_progress():
    return {
        'current': 100,
        'total': 100,
        'percent': 100,
        }


def _get_unknown_progress():
    return {
        'current': 0,
        'total': 100,
        'percent': 0,
        }
