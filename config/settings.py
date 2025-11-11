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
    'django-insecure-mituc@yo-b49e!r=wdy^g(9!w57ilg363s9v%4@95ee&$dr%2j' # Default only for local dev
)

# --- DEBUG SETTING ---
# Reads DEBUG from environment variable (like 'False' on Render)
# Defaults to True for local development if not set.
DEBUG = os.environ.get('DEBUG', 'True') == 'True' 

# --- ALLOWED HOSTS ---
# Defined conditionally later based on DEBUG status

# --- CSRF CONFIG ---
# Add Render's hostname if available (useful even in dev if using preview URLs)
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
    'whitenoise.runserver_nostatic', # Use only if needed locally, usually handled differently in prod
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
    # WhiteNoise middleware goes AFTER SecurityMiddleware
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
# Uses DATABASE_URL from Render environment, falls back to local SQLite
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
# Directory where Django looks for static files locally (your CSS, JS, etc.)
STATICFILES_DIRS = [BASE_DIR / 'static']
# Directory where collectstatic gathers all static files for deployment
STATIC_ROOT = BASE_DIR / 'staticfiles' 
# Recommended storage for WhiteNoise in production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- MEDIA FILES (User Uploads - Conditional Config) ---
MEDIA_ROOT = BASE_DIR / 'mediafiles' # Local path for DEBUG=True

if DEBUG:
    # --- Development Settings ---
    ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
    # Add Render preview URL if needed during dev
    if RENDER_EXTERNAL_HOSTNAME:
         ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

    # Use local filesystem for media files
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    
    # --- [INÍCIO DA ALTERAÇÃO] ---
    # Necessário porque a view 'upload_to_b2' faz upload manual
    # e precisa desta variável mesmo em modo DEBUG.
    AWS_LOCATION = 'media'
    
    # Vamos construir a URL completa do B2, assim como no modo de Produção,
    # já que 'upload_to_b2' está enviando os arquivos para lá.
    B2_ENDPOINT = os.getenv("B2_ENDPOINT")
    AWS_STORAGE_BUCKET_NAME = os.getenv("B2_BUCKET_NAME")

    if B2_ENDPOINT and AWS_STORAGE_BUCKET_NAME:
        MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.{B2_ENDPOINT}/{AWS_LOCATION}/'
    else:
        # Fallback se as variáveis de ambiente não estiverem carregadas
        print("!!! WARNING (DEBUG): B2_ENDPOINT ou B2_BUCKET_NAME não encontradas. MEDIA_URL pode falhar. !!!")
        MEDIA_URL = '/media/' # Mantém o antigo se falhar
    # --- [FIM DA ALTERAÇÃO] ---

    # Email backend for development (prints emails to console)
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

else:
    # --- Production Settings (Render) ---
    ALLOWED_HOSTS = ["docelarms.com.br", "www.docelarms.com.br"]
    if RENDER_EXTERNAL_HOSTNAME:
        ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

    # Use Backblaze B2 via django-storages
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

    # B2 Credentials and Config
    AWS_ACCESS_KEY_ID = os.getenv("B2_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("B2_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = os.getenv("B2_BUCKET_NAME")
    AWS_S3_REGION_NAME = os.getenv("B2_REGION_NAME", "us-east-005") # Default region
    AWS_S3_ENDPOINT_URL = f"https://{os.getenv('B2_ENDPOINT')}" # e.g., https://s3.us-east-005.backblazeb2.com
    
    # Standard B2/S3 settings for django-storages
    AWS_QUERYSTRING_AUTH = False # If bucket is public, set to False
    AWS_DEFAULT_ACL = None # B2 doesn't use ACLs like S3 standard
    AWS_S3_FILE_OVERWRITE = False # Keep False for safety
    AWS_LOCATION = 'media' # Subdirectory within the bucket

    # Construct the MEDIA_URL for B2 (bucket as subdomain is standard S3 style)
    # Ensure B2_ENDPOINT env var does NOT include 'https://'
    B2_ENDPOINT = os.getenv("B2_ENDPOINT")
    if B2_ENDPOINT and AWS_STORAGE_BUCKET_NAME:
        MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.{B2_ENDPOINT}/{AWS_LOCATION}/'
    else:
        # Fallback or raise error if env vars are missing
        print("!!! WARNING: B2_ENDPOINT or B2_BUCKET_NAME missing for MEDIA_URL construction !!!")
        MEDIA_URL = '/placeholder-media-error/' # Or raise ImproperlyConfigured

    # --- Production Email Config ---
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.environ.get('GMAIL_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD')
    DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# --- DEFAULT PRIMARY KEY ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- LOGIN / LOGOUT ---
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = 'login'

# --- DEBUG PRINTS (Keep for now) ---
# Note: These will print during build AND when the app starts if DEBUG=False
print("--- DEBUG STATUS ---")
print(f"DEBUG = {DEBUG}")
print("--- INICIANDO DEBUG DE STORAGE B2 (Only relevant if DEBUG=False) ---")
if not DEBUG: # Only print B2 details if in production mode
    print(f"B2_ENDPOINT (raw): {os.getenv('B2_ENDPOINT')}")
    print(f"B2_BUCKET_NAME (raw): {os.getenv('B2_BUCKET_NAME')}")
    print(f"B2_ACCESS_KEY_ID (raw): {os.getenv('B2_ACCESS_KEY_ID')}")
    # Consider removing SECRET_KEY print for security
    # print(f"B2_SECRET_ACCESS_KEY (raw): {os.getenv('B2_SECRET_ACCESS_KEY')}")
    print("---")
    print(f"AWS_S3_ENDPOINT_URL (final): {AWS_S3_ENDPOINT_URL if not DEBUG else 'N/A'}")
    print(f"AWS_STORAGE_BUCKET_NAME (final): {AWS_STORAGE_BUCKET_NAME if not DEBUG else 'N/A'}")
    print(f"MEDIA_URL (final): {MEDIA_URL}")
else:
    print("Running in DEBUG mode, B2 settings not actively used by default.")
    print(f"Local MEDIA_ROOT: {MEDIA_ROOT}")
    # Esta linha agora deve mostrar a URL do B2
    print(f"Local MEDIA_URL: {MEDIA_URL}") 
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
        "storages": { # Logger do django-storages
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "botocore": { # Logger principal do Boto3/Botocore
             "handlers": ["console"],
             "level": "DEBUG", 
             "propagate": False,
         },
         "boto3": { # Às vezes logs aparecem aqui também
             "handlers": ["console"],
             "level": "DEBUG",
             "propagate": False,
         },
         "urllib3": { # Logs de conexão de rede
             "handlers": ["console"],
             "level": "DEBUG", # Can be noisy, set to INFO if needed
             "propagate": False,
         }
    },
    # Set root logger level based on DEBUG status
    "root": {
        "handlers": ["console"],
        "level": "DEBUG" if DEBUG else "INFO", # DEBUG locally, INFO in production
    },
}
# --- FIM DA SEÇÃO LOGGING ---
MERCADOPAGO_ACCESS_TOKEN = 'TEST-2115056379086026-011214-f6d39061f853500ce2e17cbd6bdb43b0-83157671'
# settings.py (no final do arquivo)

SITE_ID = 1