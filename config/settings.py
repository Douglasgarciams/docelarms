"""
Django settings for config project.
"""
from dotenv import load_dotenv
import os
import dj_database_url
from pathlib import Path

# --- BASE DIR ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- CARREGAR .env ---
# Adicione estas linhas para ler o .env da pasta raiz do projeto
# (um nível acima de onde este settings.py está)
env_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=env_path)
# ---------------------

# --- SECURITY ---
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-mituc@yo-b49e!r=wdy^g(9!w57ilg363s9v%4@95ee&$dr%2j' # Default only for local dev
)

# --- DEBUG SETTING ---
DEBUG = os.environ.get('DEBUG', 'True') == 'True' 

# --- ALLOWED HOSTS ---
# Defined conditionally later based on DEBUG status

# --- CSRF CONFIG ---
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
CSRF_TRUSTED_ORIGINS = [
    "https://www.docelarms.com.br",
    "https://docelarms.com.br",
]
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_EXTERNAL_HOSTNAME}")

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
    'storages', # Needed for production
    'imoveis',
    'contas',
    'django.contrib.sites',
    'django.contrib.sitemaps',]

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
USE_I1N = True
USE_L10N = True
USE_THOUSAND_SEPARATOR = True
USE_TZ = True

# --- STATIC FILES (Shared Config) ---
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles' 
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# --- [INÍCIO DA CORREÇÃO] ---

# --- MEDIA FILES (User Uploads - Configuração GLOBAL) ---
MEDIA_ROOT = BASE_DIR / 'mediafiles' 

# Configurações de Storage B2 GLOBAIS (para DEBUG=True e DEBUG=False)
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

# B2 Credentials and Config
AWS_ACCESS_KEY_ID = os.getenv("B2_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("B2_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("B2_BUCKET_NAME")
AWS_S3_REGION_NAME = os.getenv("B2_REGION_NAME", "us-east-005") 
AWS_S3_ENDPOINT_URL = f"https://{os.getenv('B2_ENDPOINT')}" 

# Standard B2/S3 settings
AWS_QUERYSTRING_AUTH = False 
AWS_DEFAULT_ACL = None 
AWS_S3_FILE_OVERWRITE = False 
AWS_LOCATION = 'media' # Subdiretório no B2

# Constrói a MEDIA_URL (globalmente)
B2_ENDPOINT = os.getenv("B2_ENDPOINT")
if B2_ENDPOINT and AWS_STORAGE_BUCKET_NAME:
    MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.{B2_ENDPOINT}/{AWS_LOCATION}/'
else:
    print("!!! ERRO CRÍTICO: B2_ENDPOINT ou B2_BUCKET_NAME não definidas no .env !!!")
    MEDIA_URL = '/media-error/' 

if DEBUG:
    # --- Development Settings ---
    ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
    if RENDER_EXTERNAL_HOSTNAME:
        ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
    
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

else:
    # --- Production Settings (Render) ---
    ALLOWED_HOSTS = ["docelarms.com.br", "www.docelarms.com.br"]
    if RENDER_EXTERNAL_HOSTNAME:
        ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.environ.get('GMAIL_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD')
    DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# --- [FIM DA CORREÇÃO] ---


# --- DEFAULT PRIMARY KEY ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- LOGIN / LOGOUT ---
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = 'login'

# --- DEBUG PRINTS (Keep for now) ---
print("--- DEBUG STATUS ---")
print(f"DEBUG = {DEBUG}")
print("--- INICIANDO DEBUG DE STORAGE B2 ---") 
if not DEBUG: 
    print(f"B2_ENDPOINT (raw): {os.getenv('B2_ENDPOINT')}")
    print(f"B2_BUCKET_NAME (raw): {os.getenv('B2_BUCKET_NAME')}")
    print(f"B2_ACCESS_KEY_ID (raw): {os.getenv('B2_ACCESS_KEY_ID')}")
    print("---")
    print(f"AWS_S3_ENDPOINT_URL (final): {AWS_S3_ENDPOINT_URL}")
    print(f"AWS_STORAGE_BUCKET_NAME (final): {AWS_STORAGE_BUCKET_NAME}")
    print(f"MEDIA_URL (final): {MEDIA_URL}")
else:
    print("Running in DEBUG mode, but using B2 for media storage.")
    print(f"Local MEDIA_ROOT: {MEDIA_ROOT}")
    print(f"B2 MEDIA_URL: {MEDIA_URL}") 
print("--- FIM DO DEBUG DE STORAGE B2 ---")


# --- LOGGING (VERSÃO MAIS DETALHADA - Keep for now) ---
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {name} [{process:d}:{thread:d}] {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose", 
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO", 
            "propagate": False, 
        },
        "storages": { 
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "botocore": {
             "handlers": ["console"],
             "level": "DEBUG", 
             "propagate": False,
         },
          "boto3": { 
             "handlers": ["console"],
             "level": "DEBUG",
             "propagate": False,
         },
          "urllib3": { 
             "handlers": ["console"],
             "level": "DEBUG", 
             "propagate": False,
         }
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG" if DEBUG else "INFO", 
    },
}
# --- FIM DA SEÇÃO LOGGING ---
MERCADOPAGO_ACCESS_TOKEN = 'TEST-2115056379086026-011214-f6d39061f853500ce2e17cbd6bdb43b0-83157671'
# settings.py (no final do arquivo)

SITE_ID = 1