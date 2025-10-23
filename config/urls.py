# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings             # Importe settings
from django.conf.urls.static import static   # Importe static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('contas/', include('contas.urls')), # Adicione esta linha
    path('', include('imoveis.urls')),
]

# Adicione esta linha no final do arquivo
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)