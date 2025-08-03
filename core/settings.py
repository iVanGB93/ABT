from pathlib import Path
import os
from decouple import config
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')

DEBUG = config('DEBUG', default=False, cast=bool)

ADMINS = [('iVan', 'ivanguachbeltran@gmail.com')]

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'web.apps.WebConfig',
    'user.apps.UserConfig',
    'client.apps.ClientConfig',
    'job.apps.JobConfig',
    'item.apps.ItemConfig',
    'business.apps.BusinessConfig',
    'fontawesomefree',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'storages'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

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

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases


if config('DEBUG', default=False, cast=bool):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST'),
            'PORT': config('DB_PORT'),
            #'OPTIONS': {
            #    'connect_timeout': 10,
            #},
        }
    }

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

""" MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media') """

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CSRF_TRUSTED_ORIGINS = [
    'https://abt.qbared.com',
]

CORS_ALLOW_ALL_ORIGINS = True

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}

#configuracion de correo
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
#EMAIL_HOST = 'smtpout.secureserver.net'
#EMAIL_USE_SSL = False
EMAIL_USE_TLS = True
EMAIL_PORT = 587
#EMAIL_PORT = 80
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
#EMAIL_HOST_USER = 'admin@qbared.com'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')


#DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

AWS_ACCESS_KEY_ID = config('DO_SPACES_KEY')
AWS_SECRET_ACCESS_KEY = config('DO_SPACES_SECRET')

AWS_STORAGE_BUCKET_NAME = 'abt-media'
AWS_S3_REGION_NAME = 'nyc3'
AWS_S3_ENDPOINT_URL = f'https://{AWS_S3_REGION_NAME}.digitaloceanspaces.com'

AWS_QUERYSTRING_AUTH = False
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.{AWS_S3_REGION_NAME}.cdn.digitaloceanspaces.com'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'

STORAGES = {
    'default': {
        'BACKEND': 'core.storages.PublicMediaStorage',
        'OPTIONS': {
            'access_key': AWS_ACCESS_KEY_ID,
            'secret_key': AWS_SECRET_ACCESS_KEY,
            'bucket_name': AWS_STORAGE_BUCKET_NAME,
            'region_name': AWS_S3_REGION_NAME,
            'endpoint_url': AWS_S3_ENDPOINT_URL,
            'default_acl': 'public-read',
            'custom_domain': AWS_S3_CUSTOM_DOMAIN,
            'querystring_auth': False,
        }
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}