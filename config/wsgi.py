"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from dotenv import load_dotenv

load_dotenv() # Loads .env file if present

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Get the standard Django application first
application = get_wsgi_application()

# (Optional but recommended) Explicitly wrap with WhiteNoise
# This can help ensure static files are served correctly by the WSGI server
# from whitenoise import WhiteNoise
# application = WhiteNoise(application)