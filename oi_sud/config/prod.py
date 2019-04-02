import os

from .default import *  # NOQA

DEBUG = False
ALLOWED_HOSTS = ['*',]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'oi_sud',
        'USER': 'oi_sud',
        'PASSWORD': os.environ.get('DB_PASS'),
        'HOST': 'db',
        'PORT': '5432',
    }
}
