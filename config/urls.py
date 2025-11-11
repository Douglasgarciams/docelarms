# Em config/urls.py
from django.conf import settings 
from django.conf.urls.static import static 
from django.contrib import admin
from django.urls import path, include

# --- ✅ [1. IMPORTES ADICIONADOS] ---
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from imoveis.sitemaps import ImovelSitemap, StaticViewSitemap # (Você criou este arquivo no Passo 2)

# --- ✅ [2. DICIONÁRIO DO SITEMAP ADICIONADO] ---
# Isso diz ao Django quais classes usar para gerar o mapa
sitemaps = {
    'imoveis': ImovelSitemap,
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('contas/', include('contas.urls')),
    
    # --- ✅ [3. ROTAS DO SITEMAP E ROBOTS.TXT ADICIONADAS] ---
    # Esta linha gera o arquivo sitemap.xml
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    # Esta linha serve o arquivo robots.txt que você criou
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    
    # Esta rota principal deve vir por último
    path('', include('imoveis.urls')), 
]

# --- BLOCO ADICIONADO ---
# Servir arquivos de mídia (uploads) durante o desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# --- FIM DO BLOCO ---