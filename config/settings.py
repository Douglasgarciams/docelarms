"""
Django settings for config project.
"""
import os
import dj_database_url
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-mituc@yo-b49e!r=wdy^g(9!w57ilg363s9v%4@95ee&$dr%2j')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG') == 'True'

# ALLOWED_HOSTS CONFIGURATION FOR RENDER AND LOCAL
ALLOWED_HOSTS = ["docelarms.com.br", "www.docelarms.com.br"]
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
if DEBUG:
    ALLOWED_HOSTS.append('localhost')
    ALLOWED_HOSTS.append('127.0.0.1')

# Application definition
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

# Database
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600
    )
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# Internationalization
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Campo_Grande'
USE_I18N = True
USE_L10N = True
USE_THOUSAND_SEPARATOR = True
USE_TZ = True

# Static files (Configured for WhiteNoise)
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static'] 
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login/Logout URLs
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = 'login'

# Email Config
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('GMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# --- Configurações do Cloudflare R2 (VERSÃO FINAL REVISADA) ---

# Credenciais (Lidas do Ambiente)
AWS_ACCESS_KEY_ID = os.environ.get('CLOUDFLARE_R2_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('CLOUDFLARE_R2_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('CLOUDFLARE_R2_BUCKET_NAME')
CLOUDFLARE_ACCOUNT_ID = os.environ.get('CLOUDFLARE_R2_ACCOUNT_ID')

# 1. ENDPOINT DA API S3 (Para Boto3 fazer o upload)
AWS_S3_ENDPOINT_URL = f"https://{CLOUDFLARE_ACCOUNT_ID}.r2.cloudflarestorage.com"

# 2. DOMÍNIO PÚBLICO (Para o navegador exibir a imagem)
#    Sua URL Pública, APENAS O DOMÍNIO (sem https://)
R2_PUBLIC_DOMAIN = 'pub-b06bb61e03d3434889f102b1a56ce95d.r2.dev' 
AWS_S3_CUSTOM_DOMAIN = R2_PUBLIC_DOMAIN # Informa ao django-storages

# Configurações Adicionais
AWS_S3_REGION_NAME = 'auto'
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = False 

# --- CONFIGURAÇÃO EXPLÍCITA PARA O BOTO3 ---
AWS_S3_CLIENT_CONFIG = {
    'endpoint_url': AWS_S3_ENDPOINT_URL,
    'region_name': AWS_S3_REGION_NAME,
    'signature_version': AWS_S3_SIGNATURE_VERSION,
}
AWS_S3_ADDRESSING_STYLE = 'path'
# ---------------------------------------------

# Define o backend de armazenamento padrão para arquivos de mídia
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# --- Lógica de MEDIA_URL ATUALIZADA ---
if DEBUG:
    # Desenvolvimento Local
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'
else:
    # Produção (Render): Usa a URL Pública do R2
    AWS_LOCATION = 'media'
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/"
    MEDIA_ROOT = BASE_DIR / 'media'
# ----------------------------------------------------------------