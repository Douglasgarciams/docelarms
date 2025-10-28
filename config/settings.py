"""
Django settings for config project.
"""
import os
import dj_database_url
from pathlib import Path

# --- BASE DIR ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- SECURITY ---
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-mituc@yo-b49e!r=wdy^g(9!w57ilg363s9v%4@95ee&$dr%2j'
)

# ⚙️ Em produção, mantenha sempre False
DEBUG = False

# --- ALLOWED HOSTS ---
ALLOWED_HOSTS = ["docelarms.com.br", "www.docelarms.com.br"]
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# --- CSRF CONFIG ---
CSRF_TRUSTED_ORIGINS = [
    "https://www.docelarms.com.br",
    "https://docelarms.com.br",
]

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
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
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

# --- BACKBLAZE B2 STORAGE CONFIG (CORRIGIDO) ---
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

AWS_ACCESS_KEY_ID = os.getenv("B2_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("B2_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("B2_BUCKET_NAME")
AWS_S3_REGION_NAME = os.getenv("B2_REGION_NAME", "us-east-005")
AWS_S3_ENDPOINT_URL = f"https://{os.getenv('B2_ENDPOINT')}"
AWS_QUERYSTRING_AUTH = False
AWS_DEFAULT_ACL = None
AWS_S3_FILE_OVERWRITE = False

# Pasta dentro do bucket
AWS_LOCATION = 'media'

# --- CORREÇÃO APLICADA AQUI ---

# 1. AWS_S3_CUSTOM_DOMAIN NÃO deve ter "https://" no início.
#    Usamos os.getenv('B2_ENDPOINT') diretamente.
AWS_S3_CUSTOM_DOMAIN = f"{os.getenv('B2_ENDPOINT')}/file/{AWS_STORAGE_BUCKET_NAME}"

# 2. MEDIA_URL deve ser apenas o CAMINHO (path) relativo ao custom_domain.
#    O django-storages irá juntar: https:// + AWS_S3_CUSTOM_DOMAIN + MEDIA_URL
MEDIA_URL = f"/{AWS_LOCATION}/"

# --- FIM DA CORREÇÃO ---


# --- INÍCIO DO BLOCO DE DEPURAÇÃO (AÇÃO) ---
print("--- INICIANDO DEBUG DE STORAGE B2 ---")
print(f"B2_ENDPOINT (raw): {os.getenv('B2_ENDPOINT')}")
print(f"B2_BUCKET_NAME (raw): {os.getenv('B2_BUCKET_NAME')}")
print(f"B2_ACCESS_KEY_ID (raw): {os.getenv('B2_ACCESS_KEY_ID')}")
print(f"B2_SECRET_ACCESS_KEY (raw): {os.getenv('B2_SECRET_ACCESS_KEY')}")
print("---")
print(f"AWS_S3_ENDPOINT_URL (final): {AWS_S3_ENDPOINT_URL}")
print(f"AWS_STORAGE_BUCKET_NAME (final): {AWS_STORAGE_BUCKET_NAME}")
print(f"AWS_S3_CUSTOM_DOMAIN (final): {AWS_S3_CUSTOM_DOMAIN}")
print(f"MEDIA_URL (final): {MEDIA_URL}")
print("--- FIM DO DEBUG DE STORAGE B2 ---")
# --- FIM DO BLOCO DE DEPURAÇÃO ---


