from .default import *  # NOQA

SECRET_KEY = 'gl)+h@c5pg_9i(8mwzpah_h5#*lr1u13w1xl_h-*60(gb=+%j^'

DEBUG = True

# EMAIL CONFIGURATION
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
ALLOWED_HOSTS = ['127.0.0.1', 'backend', '*']
BASE_URL = 'http://127.0.0.1:8082'
FRONTEND_URL = 'http://127.0.0.1:3000'

CORS_ORIGIN_WHITELIST = (

    'http://127.0.0.1:8082',
    'http://localhost:3000',
    'http://127.0.0.1:3000'
)

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'sudmonster',
#         'USER': 'sudmonster',
#         'PASSWORD': 'okaysudmonster',
#         'HOST': '172.105.73.238',
#         'PORT': '5432',
#     }
# }

# REST_FRAMEWORK = {
#     'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
#     'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
#     'DATETIME_FORMAT': "%Y-%m-%d %H:%M",
#     'PAGE_SIZE': 10,
#     # 'DEFAULT_AUTHENTICATION_CLASSES': (
#     # 'rest_framework.authentication.TokenAuthentication',
#     #  ),
#     'DEFAULT_PERMISSION_CLASSES': (
#     'rest_framework.permissions.AllowAny',
#     ),
#     'DEFAULT_RENDERER_CLASSES': [
#         'rest_framework.renderers.JSONRenderer',
#         'rest_framework.renderers.BrowsableAPIRenderer',
#         'rest_framework.renderers.AdminRenderer'
#     ]
# }

# MIDDLEWARE = [
#     'oi_sud.core.utils.CORSMiddleware',
#     'django.middleware.security.SecurityMiddleware',
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     'django.middleware.clickjacking.XFrameOptionsMiddleware',
# ]