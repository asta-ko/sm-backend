from .default import *  # NOQA

DEBUG = True

# EMAIL CONFIGURATION
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
ALLOWED_HOSTS = ['127.0.0.1','backend']
