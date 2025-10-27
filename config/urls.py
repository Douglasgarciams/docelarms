# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings             # <<< 1. IMPORTE settings
from django.conf.urls.static import static   # <<< 2. IMPORTE static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('contas/', include('contas.urls')), 
    path('', include('imoveis.urls')),
]

# --- 3. ADICIONE ESTE BLOCO NO FINAL ---
# Serve arquivos de mídia (uploads) durante o desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# ------------------------------------