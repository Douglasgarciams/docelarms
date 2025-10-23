"""
Django settings for config project.
"""
import os
import dj_database_url
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Consider moving this to an environment variable in production
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-mituc@yo-b49e!r=wdy^g(9!w57ilg363s9v%4@95ee&$dr%2j') # Default for local dev

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG') == 'True' # Reads from .env locally

# --- ALLOWED_HOSTS CONFIGURATION FOR RENDER ---
ALLOWED_HOSTS = []
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
# Add 'localhost' and '127.0.0.1' for local development if needed
if DEBUG:
    ALLOWED_HOSTS.append('localhost')
    ALLOWED_HOSTS.append('127.0.0.1')
# -----------------------------------------------


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic', # Important for serving static files locally with WhiteNoise
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'imoveis',
    'contas',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # --- WHITENOISE MIDDLEWARE ADDED ---
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # ----------------------------------
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
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
# --- DATABASE CONFIGURATION USING dj_database_url ---
DATABASES = {
    'default': dj_database_url.config(
        # Uses DATABASE_URL from environment if available, otherwise falls back to SQLite
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600 # Recommended for persistent connections
    )
}
# ----------------------------------------------------


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Campo_Grande'
USE_I18N = True
USE_L10N = True
USE_THOUSAND_SEPARATOR = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/
STATIC_URL = 'static/'
# --- STATICFILES CONFIGURATION FOR WHITENOISE ---
# This setting tells Django where to find your static files in development
STATICFILES_DIRS = [BASE_DIR / 'static'] # Assuming you have a /static/ folder in your project root for global static files
# This setting tells Django where to collect all static files for production
STATIC_ROOT = BASE_DIR / 'staticfiles'
# This setting tells WhiteNoise how to handle static files efficiently
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# ---------------------------------------------

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuração para arquivos de mídia (uploads dos usuários) - Remains the same
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Login/Logout URLs - Remains the same
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = 'login'

# Configuração de E-mail para Produção (Gmail com Senha de App) - Remains the same
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('GMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER