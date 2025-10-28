"""
Django settings for config project.
"""
import os
import dj_database_url
from pathlib import Path

# --- BASE DIR ---
BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = True

# --- SECURITY ---
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-mituc@yo-b49e!r=wdy^g(9!w57ilg363s9v%4@95ee&$dr%2j'
)
DEBUG = os.environ.get('DJANGO_DEBUG') == 'True'

# --- ALLOWED HOSTS ---
ALLOWED_HOSTS = ["docelarms.com.br", "www.docelarms.com.br"]
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
if DEBUG:
    ALLOWED_HOSTS.extend(['localhost', '127.0.0.1'])

# --- INSTALLED APPS ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'storages',
    'imoveis',
    'contas',
]

# --- MIDDLEWARE ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# --- TEMPLATES ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# --- DATABASE ---
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600
    )
}

# --- PASSWORD VALIDATION ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- INTERNATIONALIZATION ---
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Campo_Grande'
USE_I18N = True
USE_L10N = True
USE_THOUSAND_SEPARATOR = True
USE_TZ = True

# --- STATIC FILES (WhiteNoise) ---
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- DEFAULT PRIMARY KEY ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- LOGIN / LOGOUT ---
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = 'login'

# --- EMAIL CONFIG ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('GMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# --- MEDIA / FILE STORAGE ---
AWS_ACCESS_KEY_ID = os.environ.get('B2_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('B2_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('B2_BUCKET_NAME')
AWS_S3_REGION_NAME = os.environ.get('B2_REGION_NAME')
AWS_S3_ENDPOINT_URL = f"https://{os.environ.get('B2_ENDPOINT')}"  # Ex: s3.us-east-005.backblazeb2.com
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = 'public-read'
AWS_QUERYSTRING_AUTH = False
AWS_S3_ADDRESSING_STYLE = 'path'

# Pasta dentro do bucket
AWS_LOCATION = 'media'

if DEBUG:
    # LOCAL STORAGE
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
else:
    # BACKBLAZE B2 STORAGE
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_S3_ENDPOINT_URL}/file/{AWS_STORAGE_BUCKET_NAME}"
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/"
    MEDIA_ROOT = None  # não usado no B2
# --- LOGGING DETALHADO (para debug em produção e storage) ---
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "DEBUG"},
        "storages": {"handlers": ["console"], "level": "DEBUG"},
    },
}
