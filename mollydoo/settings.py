"""
Generated by 'django-admin startproject' using Django 3.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path

use_grappelli = False
use_jazzmin = False
assert not(use_grappelli & use_jazzmin), 'both grappelli and jazzmin specified in setting.py'

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'yv6@$$hwe=ko=3muvr#hpjzb6tcw9(xi174v2^2$446afcrij-'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

INTERNAL_IPS = [ # added
    # ...
    '127.0.0.1',
    # ...
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    #'django.contrib.admin.apps.SimpleAdminConfig', # added
    'django.contrib.auth',
    #'polymorphic',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'erp',
    #'simple_history',
  #  'nested_admin',
    'import_export',
   # 'smart_selects',
    #'debug_toolbar',
  #  'stuff',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    #'simple_history.middleware.HistoryRequestMiddleware',
]

ROOT_URLCONF = 'mollydoo.urls'


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

if use_grappelli: 
    INSTALLED_APPS.insert(0,'grappelli') # must go at the beginning
    TEMPLATES[0]['OPTIONS']['context_processors'].append('django.template.context_processors.request')

if use_jazzmin: 
    INSTALLED_APPS.insert(0,'jazzmin') # must go at the beginning
    from .jazzmin_settings import JAZZMIN_SETTINGS, JAZZMIN_UI_TWEAKS # will use defaults if not specified

if DEBUG:
    INSTALLED_APPS.extend(["debug_toolbar"]) # "django_extensions"
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
    #DEBUG_TOOLBAR_CONFIG = {"SHOW_TOOLBAR_CALLBACK": lambda _: False}


WSGI_APPLICATION = 'mollydoo.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-gb' #added

TIME_ZONE = 'Europe/London' #'UTC' #added

USE_I18N = True

USE_L10N = True

USE_TZ = True
#
# DATE_INPUT_FORMATS = ('%d-%m-%Y','%Y-%m-%d')


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'

#SIMPLE_HISTORY_REVERT_DISABLED = True

#USE_DJANGO_JQUERY = True #added

