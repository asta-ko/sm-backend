from .default import *  # NOQA

DEBUG = True

# EMAIL CONFIGURATION
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
ALLOWED_HOSTS = ['127.0.0.1', 'backend', '*']
BASE_URL = 'http://127.0.0.1:8082'



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