"""
ASGI config for config project.
"""

from dotenv import load_dotenv
load_dotenv() # <<< ADICIONADO AQUI

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_asgi_application()