from .default import *  # NOQA

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'model_clone',
    'django.contrib.postgres',
    'reversion',  # https://github.com/etianen/django-reversion
    'reversion_compare',  # https://github.com/jedie/django-reversion-compare
    'oi_sud.core',
    'oi_sud.courts.apps.CourtsConfig',
    'oi_sud.codex.apps.CodexConfig',
    'oi_sud.cases.apps.CasesConfig',
    'oi_sud.users.apps.UsersConfig',
    'oi_sud.presets.apps.PresetsConfig'
]

AUTH_USER_MODEL = "users.CustomUser"

MIDDLEWARE = [

    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'oi_sud.urls_d'

SECRET_KEY = 'gl)+h@c5pg_9i(8mwzpah_h5#*lr1u13w1xl_h-*60(gb=+%j^'

DEBUG = False

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

