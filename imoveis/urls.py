# imoveis/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # --- NOVA URL PARA A API DE BAIRROS ---
    path('api/bairros/', views.get_bairros, name='get_bairros'),

    path('', views.lista_imoveis, name='lista_imoveis'),
    path('imovel/<int:id>/', views.detalhe_imovel, name='detalhe_imovel'),
    # --- [LINHA ADICIONADA] ---
    path('politica-de-uso/', views.politica_de_uso, name='politica_de_uso'),
    # --- [LINHA ADICIONADA] ---
    path('politica-de-qualidade/', views.politica_de_qualidade, name='politica_de_qualidade'),
    # --- [LINHA ADICIONADA] ---
    path('dicas-de-seguranca/', views.dicas_de_seguranca, name='dicas_de_seguranca'),
]