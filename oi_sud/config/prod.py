import os

from .default import *  # NOQA

DEBUG = False
ALLOWED_HOSTS = ['sm.ovdinfo.org','sudmonster.ovdinfo.org',]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'sudmonster',
        'USER': 'sudmonster',
        'PASSWORD': os.environ.get('DB_PASS'),
        'HOST': 'db',
        'PORT': '5432',
    }
}
