# contas/urls.py
from django.urls import path, include # Adicione 'include' aqui
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Nossas views customizadas
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', auth_views.LoginView.as_view(template_name='contas/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('perfil/', views.perfil, name='perfil'),
    path('meus-imoveis/', views.meus_imoveis, name='meus_imoveis'),
    path('anunciar/', views.anunciar_imovel, name='anunciar_imovel'),
    path('editar-imovel/<int:imovel_id>/', views.editar_imovel, name='editar_imovel'),
    path('excluir-imovel/<int:imovel_id>/', views.excluir_imovel, name='excluir_imovel'),
    path('excluir-foto/<int:foto_id>/', views.excluir_foto, name='excluir_foto'),

    # --- ROTA DE PAGAMENTO ADICIONADA ---
    path('planos/', views.listar_planos, name='listar_planos'),
    path('pagar/<int:plano_id>/', views.criar_pagamento, name='criar_pagamento'),
    
    # URLs de recuperação de senha do Django
    # Elas procurarão os templates dentro de 'registration/' por padrão
    path('', include('django.contrib.auth.urls')), 
    # Nota: Isso inclui URLs como:
    # password_reset/ [name='password_reset']
    # password_reset/done/ [name='password_reset_done']
    # reset/<uidb64>/<token>/ [name='password_reset_confirm']
    # reset/done/ [name='password_reset_complete']
]