# imoveis/views.py
from django.shortcuts import render, get_object_or_404
# 1. IMPORTAMOS OS MODELOS 'Assinatura' e 'Imovel' COMPLETOS
from .models import Imovel, Cidade, Imobiliaria, Bairro, Assinatura, Plano 
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils import timezone # Importação já existe

def lista_imoveis(request):
    
    # --- [INÍCIO DA CORREÇÃO "VIGIA GLOBAL"] ---
    agora = timezone.now()

    # 1. VIGIA DE ASSINATURAS: Encontra e expira Assinaturas vencidas
    # (Isso é importante para o painel do usuário)
    assinaturas_expiradas = Assinatura.objects.filter(
        status='ATIVA',
        data_expiracao__lt=agora # Menor que (lt) agora
    )
    if assinaturas_expiradas.exists():
        print(f"VIGIA GLOBAL: Encontradas {assinaturas_expiradas.count()} assinaturas expiradas. Atualizando...")
        assinaturas_expiradas.update(status=Assinatura.StatusAssinatura.EXPIRADA)

    # 2. VIGIA DE IMÓVEIS: Encontra e expira Imóveis vencidos
    # (Isso limpa a vitrine pública E o painel do usuário)
    imoveis_expirados = Imovel.objects.filter(
        status_publicacao='ATIVO',
        data_expiracao__lt=agora # Menor que (lt) agora
    )
    if imoveis_expirados.exists():
        print(f"VIGIA GLOBAL: Encontrados {imoveis_expirados.count()} imóveis expirados. Atualizando...")
        imoveis_expirados.update(status_publicacao=Imovel.StatusPublicacao.EXPIRADO)
    
    # --- [FIM DA CORREÇÃO "VIGIA GLOBAL"] ---


    # Agora, a busca principal só pega os que SÃO ATIVOS e NÃO EXPIRADOS
    imoveis_list = Imovel.objects.filter(
        status_publicacao='ATIVO',
        data_expiracao__gt=agora 
    ).order_by('-destaque', '-data_cadastro')
    
    cidades = Cidade.objects.all()
    imobiliarias = Imobiliaria.objects.all()
    
    imobiliaria_selecionada = None

    # Lógica de filtros (pegando os valores)
    finalidade = request.GET.get('finalidade')
    imobiliaria_id = request.GET.get('imobiliaria')
    cidade_id = request.GET.get('cidade')
    bairro_id = request.GET.get('bairro')
    
    quartos_min = request.GET.get('quartos')
    suites_min = request.GET.get('suites')
    banheiros_min = request.GET.get('banheiros')
    salas_min = request.GET.get('salas')
    cozinhas_min = request.GET.get('cozinhas')
    closets_min = request.GET.get('closets')
    area_min = request.GET.get('area')
    preco_max = request.GET.get('preco_max')

    # --- APLICANDO OS FILTROS COM VALIDAÇÃO ---

    if finalidade: 
        imoveis_list = imoveis_list.filter(finalidade=finalidade)
    
    if imobiliaria_id and imobiliaria_id.isdigit():
        imoveis_list = imoveis_list.filter(imobiliaria__id=imobiliaria_id)
        try: 
            imobiliaria_selecionada = Imobiliaria.objects.get(id=imobiliaria_id)
        except Imobiliaria.DoesNotExist: 
            imobiliaria_selecionada = None
            
    if cidade_id and cidade_id.isdigit(): 
        imoveis_list = imoveis_list.filter(cidade__id=cidade_id)
        
    if bairro_id and bairro_id.isdigit(): 
        imoveis_list = imoveis_list.filter(bairro__id=bairro_id)

    if quartos_min and quartos_min.isdigit(): 
        imoveis_list = imoveis_list.filter(quartos__gte=quartos_min)
        
    if suites_min and suites_min.isdigit(): 
        imoveis_list = imoveis_list.filter(suites__gte=suites_min)
        
    if banheiros_min and banheiros_min.isdigit(): 
        imoveis_list = imoveis_list.filter(banheiros__gte=banheiros_min)
        
    if salas_min and salas_min.isdigit(): 
        imoveis_list = imoveis_list.filter(salas__gte=salas_min)
        
    if cozinhas_min and cozinhas_min.isdigit(): 
        imoveis_list = imoveis_list.filter(cozinhas__gte=cozinhas_min)
        
    if closets_min and closets_min.isdigit(): 
        imoveis_list = imoveis_list.filter(closets__gte=closets_min)
        
    if area_min and area_min.isdigit(): 
        imoveis_list = imoveis_list.filter(area__gte=area_min)
        
    if preco_max and preco_max.isdigit(): 
        imoveis_list = imoveis_list.filter(preco__lte=preco_max)

    # --- Fim dos Filtros ---

    paginator = Paginator(imoveis_list, 50) 
    page_number = request.GET.get('page')
    imoveis_page = paginator.get_page(page_number)
    
    contexto = {
        'imoveis': imoveis_page,
        'cidades': cidades,
        'imobiliarias': imobiliarias,
        'imobiliaria_selecionada': imobiliaria_selecionada,
        'valores_filtro': request.GET
    }
    return render(request, 'imoveis/lista_imoveis.html', contexto)

def detalhe_imovel(request, id):
    
    agora = timezone.now()
    
    # O filtro de expiração aqui já estava correto
    imovel = get_object_or_404(
        Imovel, 
        id=id, 
        status_publicacao='ATIVO',
        data_expiracao__gt=agora
    )

    contexto = { 'imovel': imovel }
    return render(request, 'imoveis/detalhe_imovel.html', contexto)

# --- VIEW "ASSISTENTE" ---
def get_bairros(request):
    cidade_id = request.GET.get('cidade_id')
    bairros = Bairro.objects.filter(cidade_id=cidade_id).order_by('nome')
    return JsonResponse(list(bairros.values('id', 'nome')), safe=False)

# --- VIEW POLITICA DE USO ---
def politica_de_uso(request):
    return render(request, 'politica_de_uso.html') 

# --- VIEW POLITICA DE QUALIDADE ---
def politica_de_qualidade(request):
    return render(request, 'politica_de_qualidade.html')

# --- VIEW DICAS DE SEGURANÇA ---
def dicas_de_seguranca(request):
    return render(request, 'dicas_de_seguranca.html')