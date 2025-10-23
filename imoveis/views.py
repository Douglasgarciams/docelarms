# imoveis/views.py
from django.shortcuts import render, get_object_or_404
from .models import Imovel, Cidade, Imobiliaria, Bairro
from django.core.paginator import Paginator
from django.http import JsonResponse

def lista_imoveis(request):
    imoveis_list = Imovel.objects.filter(aprovado=True).order_by('-destaque', '-data_cadastro')
    
    cidades = Cidade.objects.all()
    imobiliarias = Imobiliaria.objects.all()
    
    imobiliaria_selecionada = None

    # Lógica de filtros (sem alterações)
    finalidade = request.GET.get('finalidade')
    imobiliaria_id = request.GET.get('imobiliaria')
    cidade_id = request.GET.get('cidade')
    # ... (restante dos seus filtros)
    quartos_min = request.GET.get('quartos')
    suites_min = request.GET.get('suites')
    banheiros_min = request.GET.get('banheiros')
    salas_min = request.GET.get('salas')
    cozinhas_min = request.GET.get('cozinhas')
    closets_min = request.GET.get('closets')
    area_min = request.GET.get('area')
    preco_max = request.GET.get('preco_max')

    if finalidade: imoveis_list = imoveis_list.filter(finalidade=finalidade)
    if imobiliaria_id:
        imoveis_list = imoveis_list.filter(imobiliaria__id=imobiliaria_id)
        try: imobiliaria_selecionada = Imobiliaria.objects.get(id=imobiliaria_id)
        except Imobiliaria.DoesNotExist: imobiliaria_selecionada = None
    if cidade_id: imoveis_list = imoveis_list.filter(cidade__id=cidade_id)
    if quartos_min: imoveis_list = imoveis_list.filter(quartos__gte=quartos_min)
    if suites_min: imoveis_list = imoveis_list.filter(suites__gte=suites_min)
    if banheiros_min: imoveis_list = imoveis_list.filter(banheiros__gte=banheiros_min)
    if salas_min: imoveis_list = imoveis_list.filter(salas__gte=salas_min)
    if cozinhas_min: imoveis_list = imoveis_list.filter(cozinhas__gte=cozinhas_min)
    if closets_min: imoveis_list = imoveis_list.filter(closets__gte=closets_min)
    if area_min: imoveis_list = imoveis_list.filter(area__gte=area_min)
    if preco_max: imoveis_list = imoveis_list.filter(preco__lte=preco_max)

    # Lógica de paginação (sem alterações)
    paginator = Paginator(imoveis_list, 15) 
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
    imovel = get_object_or_404(Imovel, id=id, aprovado=True)
    contexto = { 'imovel': imovel }
    return render(request, 'imoveis/detalhe_imovel.html', contexto)

# --- VIEW "ASSISTENTE" COM A INDENTAÇÃO CORRETA ---
def get_bairros(request):
    # As linhas abaixo precisam estar indentadas
    cidade_id = request.GET.get('cidade_id')
    bairros = Bairro.objects.filter(cidade_id=cidade_id).order_by('nome')
    return JsonResponse(list(bairros.values('id', 'nome')), safe=False)