# Em config/urls.py
from django.conf import settings             # Importar settings
from django.conf.urls.static import static # Importar static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('contas/', include('contas.urls')),
    path('', include('imoveis.urls')), 
]

# --- BLOCO ADICIONADO ---
# Servir arquivos de mídia (uploads) durante o desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# --- FIM DO BLOCO ---

# Nota: O WhiteNoise (configurado no settings.py) geralmente cuida
# dos arquivos estáticos (CSS/JS) da aplicação, mesmo em debug.
# Este bloco 'static' é especificamente para os arquivos de MÍDIA (uploads).