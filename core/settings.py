import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = 'isz25o*o=gu9ao&y3kxcr(mfl@7ayz@=)ik@pr*^f$jsvh&r1('
DEBUG = False

TEMPLATE_DEBUG = False
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'database.urls'

WSGI_APPLICATION = 'database.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', 
        'NAME': 'forums_db',
        'USER': 'root',
        'PASSWORD': 'alex18661866',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'

USE_I18N = True
USE_L10N = True
USE_TZ = True