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

# --- Configurações do Backblaze B2 ---

AWS_ACCESS_KEY_ID = os.environ.get('B2_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('B2_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('B2_BUCKET_NAME')
B2_ENDPOINT = os.environ.get('B2_ENDPOINT') # Ex: s3.us-east-005.backblazeb2.com
B2_REGION = os.environ.get('B2_REGION_NAME') # Ex: us-east-005 (o nome da região B2)

# O endpoint que o Boto3 usa para fazer requisições (uploads, etc.)
AWS_S3_ENDPOINT_URL = f"https://{B2_ENDPOINT}"

# O domínio personalizado para acesso público aos arquivos.
# O B2 usa um formato específico para URLs amigáveis:
# bucket-name.s3.region-code.backblazeb2.com (se for um endpoint do tipo S3)
# OU, se você configurou um CNAME no Cloudflare para o seu bucket
# (o que você provavelmente fez para o R2, mas estamos usando o B2 agora):
# files.docelarms.com.br (se você apontou esse CNAME para a URL amigável do B2)

# VAMOS USAR O DOMÍNIO AMIGÁVEL DIRETO DO B2 (sem Cloudflare para simplificar)
# Formato: https://f005.backblazeb2.com/file/seu-nome-de-bucket/
# OU: https://seu-nome-de-bucket.s3.REGION.backblazeb2.com/ (se o endpoint S3 for usado)
# Baseado na sua configuração anterior, vamos assumir que B2_ENDPOINT já é o endpoint S3.
# Se B2_ENDPOINT for 's3.us-east-005.backblazeb2.com', então a URL base para o bucket é 'seu-bucket-name.s3.us-east-005.backblazeb2.com'
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.{B2_ENDPOINT}"

AWS_S3_REGION_NAME = B2_REGION
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = 'public-read' # Essencial para buckets públicos
AWS_QUERYSTRING_AUTH = False 
AWS_S3_ADDRESSING_STYLE = 'virtual' # B2 usa estilo 'virtual' (bucket.endpoint.com)

# --- Lógica de ARMAZENAMENTO E MEDIA (CORRIGIDA) ---
if DEBUG:
    # --- DESENVOLVIMENTO LOCAL ---
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
else:
    # --- PRODUÇÃO (RENDER) ---
    
    # ATIVA O ARMAZENAMENTO DO S3/B2
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    
    # Define a pasta raiz dentro do bucket (se usarmos)
    AWS_LOCATION = 'media'
    
    # Define a URL de exibição
    # A URL para arquivos no B2 é: https://[B2_BUCKET_NAME].[B2_ENDPOINT]/[AWS_LOCATION]/[nome_do_arquivo]
    # Se você quiser o caminho completo como no S3:
    MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.{B2_ENDPOINT}/{AWS_LOCATION}/"
    # Certifique-se de que B2_ENDPOINT não inclui "https://"
    
    MEDIA_ROOT = BASE_DIR / 'media' # Ainda aponta para a pasta local, mas não será usada em prod
# ----------------------------------------------------------------