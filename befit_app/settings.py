from pathlib import Path
from django.utils.translation import gettext_lazy as _
import os
import sys


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-@q_sm4h4&_)m5p*3r-k-)yde&0@bf@!c(76q!@t-y%yq*&6(*(')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'




ALLOWED_HOSTS = ['127.0.0.1', 'localhost']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.auth.decorators', # Ajouter pour logine required
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'befit_app',
    'gym_app',
    'cart',
    'django_q',
    'cookie_consent',
    'rest_framework',
    'api',
]


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # Autorise tous les utilisateurs
    ],
}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
     'django.middleware.locale.LocaleMiddleware',
]

# LOCALE_PATHS = [BASE_DIR / 'locale']



ROOT_URLCONF = 'befit_app.urls'

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
                'cart.context_processors.cart',
                'gym_app.context_processors.unread_messages_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'befit_app.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
Q_CLUSTER = {
    'name': 'DjangoQ',
    'workers': 2,
    'recycle': 500,
    'timeout': 90,
    'retry': 120,
    'queue_limit': 50,
    'bulk': 10,
    'django_redis': 'default',
    'orm': 'default',  # Utiliser l'ORM pour stocker les tâches dans la base de données
    'log_level': 'DEBUG',  # Active les logs détaillés
    
}



# Tâches planifiées
Q_CLUSTER['tasks'] = [
    {
        'func': 'gym_app.tasks.send_workout_reminder',
        'schedule_type': 'H',  # 'H' signifie qu'elle sera exécutée toutes les heures
        'repeats': -1,  # Répéter indéfiniment
        'minutes': 60   # Exécuter toutes les heures
    },
]



AUTH_USER_MODEL = 'gym_app.User'
LOGIN_URL = '/login/'
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_SECURE = False  # True si tu utilises HTTPS
SESSION_EXPIRE_AT_BROWSER_CLOSE = False # détermine si la session doit expirer à la fermeture du navigateur. Si True, entraîne  déconnexion après le changement de mot de passe, car la session pourrait être effacée
STRIPE_SECRET_KEY = 'sk_test_51NAZGUIuDh7cZGu7O2BQQX7pRdlKZ11nz91vU4buwTdCg9YjF1nTG2TrC6gtXzIASog4VnCpP2ENjkKh7vkem2d300yum2ChD2'
STRIPE_PUBLIC_KEY = 'pk_test_51NAZGUIuDh7cZGu7Fr7Atfzx99eYbTPTN2tWeFluHd2at0fmuif98iChDsRfCvg6Ob0oGF1LKmVe4ITP6e9nZUFo00qjHrXrX4'





# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/


sys.stdout.reconfigure(encoding='utf-8')  # Forcer l'encodage UTF-8

LANGUAGE_CODE = 'fr' 
PREFIX_DEFAULT_LANGUAGE = True

DEFAULT_CHARSET = 'utf-8'

TIME_ZONE = 'Europe/Brussels'  # Fuseau horaire

LANGUAGES = [
    ('fr', _('French')),
    ('nl', _('Dutch')),
    ('en', _('English')),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',  
]

USE_I18N = True
USE_L10N = True

USE_TZ = True
# WAGTAIL_I18N_ENABLED = True


# Option pour toujours afficher le préfixe de la langue, même pour la langue par défaut
PREFIX_DEFAULT_LANGUAGE = False  # Si tu veux forcer /fr/ dans l'URL pour la langue par défaut


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
