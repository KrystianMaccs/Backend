import os

from datetime import timedelta
from gocreate.aws.conf import *

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    'SECRET_KEY', 'eHIW$&G*&H$G&P(W*HFOhco2hrpv78yvp87yrv78y')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

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

WSGI_APPLICATION = 'gocreate.wsgi.application'

ROOT_URLCONF = 'gocreate.urls'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

#USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

AUTHENTICATION_BACKENDS = [
    'accounts.backends.CustomArtistBackend',
    'django.contrib.auth.backends.ModelBackend',
]



REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'sso.authentication.SSOAuthWebTokenAuthenticate',
        # 'accounts.authentication.GCJSONWebTokenAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 200,
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.JSONParser',
    ],
}


JWT_AUTH = {
    'JWT_ENCODE_HANDLER':
    'rest_framework_simplejwt.utils.jwt_encode_handler',
    'JWT_DECODE_HANDLER':
    'rest_framework_simplejwt.utils.jwt_decode_handler',
    'JWT_PAYLOAD_HANDLER':
    'rest_framework_simplejwt.utils.jwt_payload_handler',
    'JWT_PAYLOAD_GET_USER_ID_HANDLER':
    'rest_framework_simplejwt.utils.jwt_get_user_id_from_payload_handler',
    'JWT_RESPONSE_PAYLOAD_HANDLER':
    'rest_framework_simplejwt.utils.jwt_response_payload_handler',

    'JWT_SECRET_KEY': SECRET_KEY,
    'JWT_GET_USER_SECRET_KEY': None,
    'JWT_PUBLIC_KEY': None,
    'JWT_PRIVATE_KEY': None,
    'JWT_ALGORITHM': 'HS256',
    'JWT_VERIFY': True,
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_LEEWAY': 0,
    'JWT_EXPIRATION_DELTA': timedelta(hours=1),
    'JWT_AUDIENCE': None,
    'JWT_ISSUER': None,
    'JWT_ALLOW_REFRESH': False,
    'JWT_REFRESH_EXPIRATION_DELTA': timedelta(hours=1),
    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
    'JWT_AUTH_COOKIE': None,
}

CORS_ORIGIN_WHITELIST = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

TWILIO_SID = os.getenv("TWILIO_SID", None)
# Found on Twilio Console Dashboard
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", None)
TWILIO_SENDER_NUMBER = os.getenv('TWILIO_SENDER_NUMBER', None)

PAYSTACK_TEST_SECRET_KEY = os.getenv('PAYSTACK_TEST_SECRET_KEY', None)
PAYSTACK_LIVE_SECRET_KEY = os.getenv('PAYSTACK_LIVE_SECRET_KEY', None)

STRIPE_TEST_KEY = os.getenv('STRIPE_TEST_KEY', None)
STRIPE_LIVE_KEY = os.getenv('STRIPE_LIVE_KEY', None)

PAYMENT_IS_LIVE = os.getenv('PAYMENT_IS_LIVE', None)

EVEARA_CLIENT_ID = os.getenv('EVEARA_CLIENT_ID', None)
EVEARA_CLIENT_SECRET = os.getenv('EVEARA_CLIENT_SECRET', None)

EVEARA_PRODUCTION_ID = os.getenv('EVEARA_PRODUCTION_CLIENT_ID', None)
EVEARA_PRODUCTION_SECRET = os.getenv('EVEARA_PRODUCTION_CLIENT_SECRET', None)

EVEARA_SAND_BOX_URL = 'https://staging.eveara.com/api/v0.9'
EVEARA_LIVE_URL = 'https://api.eveara.com/v0.9'

EVEARA_URL = EVEARA_LIVE_URL
EVEARA_ID = EVEARA_PRODUCTION_ID
EVEARA_SECRET = EVEARA_PRODUCTION_SECRET


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', None)
EMAIL_PORT = os.getenv('EMAIL_PORT', None)
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', None)
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', None)
EMAIL_USE_TLS = True

