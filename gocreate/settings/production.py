import dj_database_url
from datetime import timedelta
from pathlib import Path

import os

from gocreate.aws.conf import *

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).resolve().parent.parent



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    'SECRET_KEY', 'eHIW$&G*&H$G&P(W*HFOhco2hrpv78yvp87yrv78y')

DEBUG = True

ALLOWED_HOSTS = ["*"]

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = os.getenv('DEBUG', True)

# ALLOWED_HOSTS = ['web.gocreateafrica.app', 'gocreateafrica.app', 'www.web.gocreateafrica.app', '127.0.0.1', "backend-prod2.us-east-2.elasticbeanstalk.com"]

# Application definition

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

LOCAL_APPS = [
     'subscriptions',
    'systemcontrol',
    'accounts',
    'frontend',
    'payouts',
    'royalty',
    'adverts',
    'songs',
    'sso',
]
THIRD_PARTY_APPS = [
    'django_q',
    'storages',
    'drf_yasg',
    'corsheaders',
    'rest_framework',
]
INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS + THIRD_PARTY_APPS


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',

    'corsheaders.middleware.CorsMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'gocreate.urls'

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


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# db_from_env = dj_database_url.config(conn_max_age=600, ssl_require=True)
# DATABASES["default"] = dj_database_url.parse(
#     os.getenv("PROD_DATABASE_URL"),
#     conn_max_age=600,
# )

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators
Q_CLUSTER = {
    'name': 'go_create_async_worker',
    'workers': 3,
    'recycle': 500,
    'compress': True,
    'save_limit': 5000,
    'queue_limit': 10000,
    'timeout': 120 * 10,
    'cpu_affinity': 1,
    'label': 'Go Create Q',
    'redis': os.environ.get('REDIS_URL', 'redis://localhost:6379')
    # 'redis': os.environ.get("REDIS_TLS_URL", os.environ.get('REDIS_URL', 'redis://localhost:6379'))
}

CORS_REPLACE_HTTPS_REFERER = True
HOST_SCHEME = "https://"
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 1000000
SECURE_FRAME_DENY = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTHENTICATION_BACKENDS = [
    'accounts.backends.CustomArtistBackend',
    'django.contrib.auth.backends.ModelBackend',
]

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,

    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,

    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",

    "JTI_CLAIM": "jti",

    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=60),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),

    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",

}

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'accounts.custom_jwt.CustomJWTAuthentication',
    ),
    # 'DEFAULT_AUTHENTICATION_CLASSES': (
    #     "rest_framework_simplejwt.authentication import JWTAuthentication",
    #     # 'sso.authentication.SSOAuthWebTokenAuthenticate',
    #     # 'accounts.authentication.GCJSONWebTokenAuthentication',
    # ),
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

AUTH_USER_MODEL = "accounts.CustomUser"

PAYSTACK_TEST_SECRET_KEY = 'sk_test_eea883ea13202804a14a8aa4acc7074aac8f1d04'
PAYSTACK_LIVE_SECRET_KEY = 'sk_live_ac187e53e2b5f1dbf885378d30da9c99c3754b33'

PAYMENT_IS_LIVE = os.getenv('PAYMENT_IS_LIVE', None)

EVEARA_CLIENT_ID = 'F1EF64E1BBC616DA8464299202D553AD'
EVEARA_CLIENT_SECRET = 'pBden/RSOOW2yHgPE0DfkjQqtTj2FH8lzBNxuP3OV0Zy4zAQZ9J5F5dwuB+Gf2F/8RQ='

EVEARA_SAND_BOX_URL = 'https://staging.eveara.com/api/v0.9'
EVEARA_LIVE_URL = 'https://api.eveara.com/v0.9'

EVEARA_URL = EVEARA_SAND_BOX_URL
EVEARA_ID = EVEARA_CLIENT_ID
EVEARA_SECRET = EVEARA_CLIENT_SECRET

# Found on Twilio Console Dashboard
TWILIO_SID = 'AC3cfe867cfeace2c3042a56842fffbccd'
TWILIO_AUTH_TOKEN = 'f5f7d6aa43fc255a79da1c620bbff8ca'
TWILIO_SENDER_NUMBER = '+12015818651'

STRIPE_TEST_KEY = 'sk_test_51IjjhCKVJpjSXxYpvgnIH1ebVwK2Bz3WK1jZS8WwauBNSMv5tK0dAbIOYFt8ESqBgLkMsl9giBA2uQiN68GHX4lf00IpvSQDVf'
STRIPE_LIVE_KEY = ''

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.privateemail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = "noreply@gocreateafrica.app"
EMAIL_HOST_PASSWORD = 'Makeit123'
EMAIL_HOST_USER = " admin@gocreateapps.app"
EMAIL_HOST_PASSWORD = 'Makeithappen123'
EMAIL_USE_TLS = True