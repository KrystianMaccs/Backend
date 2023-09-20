import dj_database_url
from .base import *
from gocreate.aws.conf import *

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

ALLOWED_HOSTS = ['web.gocreateafrica.app', 'gocreateafrica.app', 'www.web.gocreateafrica.app', '127.0.0.1']


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

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": config("DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": config("DB_NAME", BASE_DIR/"db.sqlite3"),
        "USER": config("DB_USER", "user"),
        "PASSWORD": config("DB_PASSWORD", "password"),
        "HOST": config("DB_HOST", "localhost"),
        "PORT": config("DB_PORT", "5432"),
    }
}

# db_from_env = dj_database_url.config(conn_max_age=600, ssl_require=True)
db_from_env = dj_database_url.config()
DATABASES['default'].update(db_from_env)
DATABASES['default']['CONN_MAX_AGE'] = 500

# Q_CLUSTER Settings

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
