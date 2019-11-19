from .default import *  # NOQA

DEBUG = True

# EMAIL CONFIGURATION
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
ALLOWED_HOSTS = ['127.0.0.1', 'backend']
BASE_URL = 'http://127.0.0.1:8082'
