"""
Django settings for oi_sud project.

Generated by 'django-admin startproject' using Django 2.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os

from celery.schedules import crontab

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'gl)+h@c5pg_9i(8mwzpah_h5#*lr1u13w1xl_h-*60(gb=+%j^'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

DEBUG_REQUESTS = False

ALLOWED_HOSTS = ['sudmonster.ovdinfo.org']

BASE_URL = 'https://sudmonster.ovdinfo.org'
# Application definition

INSTALLED_APPS = [

    # 'suit',
    'jet',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'celery_progress',
    'rest_framework',
    'django_filters',
    'django_celery_results',
    'django_celery_beat',
    'django.contrib.postgres',
    'reversion',  # https://github.com/etianen/django-reversion
    'reversion_compare',  # https://github.com/jedie/django-reversion-compare
    'oi_sud.core',
    'oi_sud.courts.apps.CourtsConfig',
    'oi_sud.codex.apps.CodexConfig',
    'oi_sud.cases.apps.CasesConfig',
    'oi_sud.users.apps.UsersConfig',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "versioning.middleware.VersioningMiddleware",
]

ROOT_URLCONF = 'oi_sud.urls'
TEMP_DIR = os.path.join(BASE_DIR, 'templates')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMP_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'oi_sud.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'sudmonster',
        'USER': 'sudmonster',
        'PASSWORD': 'sudmonster',
        'HOST': 'db',
        'PORT': '5432',
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'users.CustomUser'

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'ru-RU'  # 'en-us'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = False  # True

USE_TZ = True

DATETIME_FORMAT = 'd.m.y | H:i'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/static'

# CELERY

CELERY_BROKER_URL = os.environ.get('BROKER_URL', 'redis://redis:6379/0')
# CELERY_RESULT_BACKEND = os.environ.get('BROKER_URL', 'redis://redis:6379/0')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_DEFAULT_QUEUE = 'main'
CELERY_IMPORTS = ('oi_sud.cases.tasks')

CELERYD_MAX_TASKS_PER_CHILD = 1

CELERY_RESULT_BACKEND = 'django-db'

CELERY_CACHE_BACKEND = 'django-cache'

CELERY_ROUTES = {
    'oi_sud.cases.tasks.main_get_cases': {
        'queue': 'main'
    },

    'oi_sud.cases.tasks.get_cases_from_region': {
        'queue': 'main'
    },
    'oi_sud.cases.tasks.get_uk_cases': {
        'queue': 'other'
    },

    'oi_sud.cases.tasks.get_koap_cases': {
        'queue': 'other'
    },

}

# CELERY_BEAT_SCHEDULE = {
#     'get-cases': {
#         'task': 'oi_sud.cases.tasks.main_get_cases',
#         'schedule': crontab(minute='*/1')
#     },
#
# }

JET_THEME = 'light-gray'

JET_SIDE_MENU_COMPACT = True

TEST_MODE = False

JET_SIDE_MENU_ITEMS = [

    {'app_label': 'codex', 'items': [
        {'name': 'koapcodexarticle'},
        {'name': 'ukcodexarticle'},
    ]},
    {'app_label': 'cases', 'items': [
        {'name': 'koapcase'},
        {'name': 'ukcase'},
        {'name': 'defendant'},
    ]},
    {'app_label': 'courts', 'items': [
        {'name': 'court'},
        {'name': 'judge'},
    ]},

    {'app_label': 'django_celery_results', 'items': [
        {'name': 'taskresult'},
        # {'label': 'Running tasks', 'url': '/admin/active_celery_tasks', 'url_blank': True},
    ]},
    {'app_label': 'django_celery_beat', 'items': [
        {'name': 'intervalschedule'},
        {'name': 'periodictask'},

    ]},

    {'app_label': 'API', 'items': [
        {'label': 'Cases count', 'url': '/api/v1/countcases'},
        {'label': 'Cases', 'url': '/api/v1/cases'},

    ]},

]

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'DATETIME_FORMAT': "%Y-%m-%d %H:%M",
    'PAGE_SIZE': 10,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework.renderers.AdminRenderer'
    ]
}

# Add reversion models to admin interface:
ADD_REVERSION_ADMIN=True