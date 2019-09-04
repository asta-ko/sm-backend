from .default import *  # NOQA

DEBUG = True

CELERY_TASK_ALWAYS_EAGER = True

DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# EMAIL CONFIGURATION
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = False  # True

USE_TZ = True

TEST_MODE = True


CELERY_BEAT_SCHEDULE = {

}