# imoveis/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # --- NOVA URL PARA A API DE BAIRROS ---
    path('api/bairros/', views.get_bairros, name='get_bairros'),

    path('', views.lista_imoveis, name='lista_imoveis'),
    path('imovel/<int:id>/', views.detalhe_imovel, name='detalhe_imovel'),
]