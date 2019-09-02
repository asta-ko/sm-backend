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

ALLOWED_HOSTS = ['oi_sud.ovdinfo.org']

# Application definition

INSTALLED_APPS = [

    #'suit',
    'jet',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'oi_sud.core',
    'oi_sud.courts.apps.CourtsConfig',
    'oi_sud.codex.apps.CodexConfig',
    'oi_sud.cases.apps.CasesConfig'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'oi_sud.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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
CELERY_RESULT_BACKEND = os.environ.get('BROKER_URL', 'redis://redis:6379/0')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_DEFAULT_QUEUE = 'main'
CELERY_IMPORTS = ('oi_sud.cases.tasks')

CELERYD_MAX_TASKS_PER_CHILD = 1

CELERY_ROUTES = {
                    'oi_sud.cases.tasks.main_get_koap_cases': {
                        'queue': 'main'
                    },
                    'oi_sud.cases.tasks.get_koap_cases': {
                        'queue': 'other'
                    },

                    'oi_sud.cases.tasks.main_get_uk_cases': {
                        'queue': 'main'
                    },
                    'oi_sud.cases.tasks.get_uk_cases': {
                        'queue': 'other'
                    },

                }


CELERY_BEAT_SCHEDULE = {
    'get-cases': {
        'task': 'oi_sud.cases.tasks.main_get_koap_cases',
        'schedule': crontab(minute='*/1')
    },
    'get-uk-cases': {
        'task': 'oi_sud.cases.tasks.main_get_uk_cases',
        'schedule': crontab(minute='*/1')
    },

}

JET_THEME = 'light-gray'

JET_SIDE_MENU_COMPACT = True