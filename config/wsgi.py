"""
WSGI config for config project.
"""

# --- GARANTIR QUE load_dotenv() SEJA A PRIMEIRA COISA ACONTECER ---
from dotenv import load_dotenv
load_dotenv()
# -------------------------------------------------------------

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()