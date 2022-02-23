from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-0rkqr)ui_ag6b15jupm@6tjx2jyw4dkkw6a@%(kqmv+97%ve-v'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*', ]

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Email Provider
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

USE_MODEL = False
