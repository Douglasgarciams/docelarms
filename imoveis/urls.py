# imoveis/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # --- NOVA URL PARA A API DE BAIRROS ---
    path('api/bairros/', views.get_bairros, name='get_bairros'),

    path('', views.lista_imoveis, name='lista_imoveis'),
    path('imovel/<int:id>/', views.detalhe_imovel, name='detalhe_imovel'),
    
    # --- Páginas Estáticas ---
    path('politica-de-uso/', views.politica_de_uso, name='politica_de_uso'),
    path('politica-de-qualidade/', views.politica_de_qualidade, name='politica_de_qualidade'),
    path('dicas-de-seguranca/', views.dicas_de_seguranca, name='dicas_de_seguranca'),
    
    # --- ✅ [LINHA ADICIONADA] ---
    path('fale-conosco/', views.fale_conosco, name='fale_conosco'),
    # --- ✅ [NOVAS URLs DE PARCEIROS ADICIONADAS] ---
    path('parceiros/', views.listar_parceiros, name='listar_parceiros'),
    path('parceiros/cadastrar/', views.cadastrar_parceiro, name='cadastrar_parceiro'),
]