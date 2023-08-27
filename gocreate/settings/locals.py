import os
from datetime import timedelta
from pathlib import Path


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).resolve().parent.parent



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = bool(os.environ.get("DEBUG", default=0))

# 'DJANGO_ALLOWED_HOSTS' should be a single string of hosts with a space between each.
# For example: 'DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]'
ALLOWED_HOSTS = ["*"]

# Application definition
INSTALLED_APPS = [
'django.contrib.admin',
'django.contrib.auth',
'django.contrib.contenttypes',
'django.contrib.sessions',
'django.contrib.messages',
'django.contrib.staticfiles',

'subscriptions',
'systemcontrol',
'accounts',
'frontend',
'payouts',
'royalty',
'adverts',
'songs',
'sso',

'django_q',
'debug_toolbar',
'storages',
'drf_yasg',
'corsheaders',
'rest_framework',
]

MIDDLEWARE = [
'corsheaders.middleware.CorsMiddleware',

'django.middleware.security.SecurityMiddleware',
'django.contrib.sessions.middleware.SessionMiddleware',

'django.middleware.common.CommonMiddleware',
'django.middleware.csrf.CsrfViewMiddleware',
'django.contrib.auth.middleware.AuthenticationMiddleware',
'django.contrib.messages.middleware.MessageMiddleware',
'django.middleware.clickjacking.XFrameOptionsMiddleware',
'debug_toolbar.middleware.DebugToolbarMiddleware',

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
    "default": {
        "ENGINE": os.environ.get("DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("DB_NAME", BASE_DIR/"db.sqlite3"),
        "USER": os.environ.get("DB_USER", "user"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "password"),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

# DATABASES["default"] = dj_database_url.parse(
#     os.getenv("PROD_DATABASE_URL"),
#     conn_max_age=600,
# )

INTERNAL_IPS = [
"127.0.0.1",
]


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

Q_CLUSTER = {
'name': 'go_create_async_worker',
'retry': 150,
'workers': 8,
'recycle': 500,
'timeout': 120,
'compress': True,
'save_limit': 250,
'queue_limit': 500,
'cpu_affinity': 1,
'label': 'Go Create Q',
'redis': 'redis://localhost:6379'
}

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

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

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'mail.privateemail.com'
# EMAIL_PORT = 587
# EMAIL_HOST_USER = "noreply@gocreateafrica.app"
# EMAIL_HOST_PASSWORD = 'Makeit123'
# EMAIL_HOST_USER = " admin@gocreateapps.app"
# EMAIL_HOST_PASSWORD = 'Makeithappen123'
# EMAIL_USE_TLS = True

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_HOST_USER = "gocreateapps@gmail.com"
# EMAIL_HOST_PASSWORD = 'ebqqpbeqqjklwjlv'
# EMAIL_USE_TLS = True



EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_EMAIL = 'gocreateapps@gmail.com'



CORS_ALLOW_CREDENTIALS = True

HOST_SCHEME = "http://"
SECURE_PROXY_SSL_HEADER = None
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = None
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_FRAME_DENY = False

# EMAIL_HOST = 'localhost'
# EMAIL_PORT = 1025

# FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440 # i.e. 2.5 MB
CORS_ORIGIN_ALLOW_ALL = True


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