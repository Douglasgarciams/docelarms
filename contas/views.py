# contas/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, UserUpdateForm, CustomPasswordChangeForm
from imoveis.models import Imovel, Foto
from imoveis.forms import ImovelForm
from django.contrib.auth import update_session_auth_hash
import traceback # Importar para o traceback

# --- View de Cadastro (Original) ---
def cadastro(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Conta criada com sucesso para {username}! Você já pode fazer o login.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'contas/cadastro.html', {'form': form})

# --- View do Dashboard "Meus Imóveis" (Original) ---
@login_required
def meus_imoveis(request):
    imoveis_do_usuario = Imovel.objects.filter(proprietario=request.user).order_by('-data_cadastro')
    contexto = {
        'imoveis': imoveis_do_usuario
    }
    return render(request, 'contas/meus_imoveis.html', contexto)

# --- View "Anunciar Imóvel" (COM DEBUG ADICIONADO) ---
@login_required
def anunciar_imovel(request):
    # --- DEBUG INICIAL ---
    print(f"--- Iniciando anunciar_imovel ---")
    print(f"Método da Requisição: {request.method}")
    # --- FIM DEBUG ---

    if request.method == 'POST':
        form = ImovelForm(request.POST, request.FILES)

        # --- DEBUG FORM POST ---
        print("--- DEBUG FORM POST (Anunciar) ---")
        print(f"Formulário instanciado com POST e FILES.")
        # Limitando o print do request.POST para não poluir muito o log
        print(f"request.POST (primeiros 500 chars): {str(request.POST)[:500]}") 
        print(f"request.FILES: {request.FILES}") # MUITO IMPORTANTE: Mostra os arquivos enviados
        print(f"Form is_bound: {form.is_bound}")
        # --- FIM DEBUG ---

        if form.is_valid():
            # --- DEBUG FORM VÁLIDO ---
            print("Formulário (Anunciar) é VÁLIDO.")
            # Limitando cleaned_data para evitar logs excessivos com descrição
            cleaned_data_preview = {k: v for k, v in form.cleaned_data.items() if k != 'descricao'}
            print(f"Dados limpos (sem descricao): {cleaned_data_preview}")
            print(f"Foto principal nos dados limpos: {form.cleaned_data.get('foto_principal')}")
            # --- FIM DEBUG ---
            try:
                # --- DEBUG ANTES DO SAVE ---
                print("Tentando salvar o formulário (form.save(commit=False))...")
                # --- FIM DEBUG ---
                
                imovel = form.save(commit=False)
                imovel.proprietario = request.user
                
                # --- DEBUG ANTES DO SAVE FINAL ---
                print(f"Instância Imovel criada: {imovel}")
                print(f"Foto principal ANTES do imovel.save(): {imovel.foto_principal.name if imovel.foto_principal else 'None'}")
                print("Executando imovel.save()...")
                # --- FIM DEBUG ---

                imovel.save() # A MÁGICA (ou falha) do upload acontece aqui

                # --- DEBUG DEPOIS DO SAVE ---
                print("imovel.save() EXECUTADO com sucesso.")
                print(f"Imóvel salvo ID: {imovel.id}")
                # Recarrega do banco para ter certeza
                imovel_recarregado = Imovel.objects.get(id=imovel.id) 
                print(f"Foto principal NO BANCO após save: {imovel_recarregado.foto_principal.name if imovel_recarregado.foto_principal else 'None'}")
                if imovel_recarregado.foto_principal:
                    print(f"URL da foto principal gerada: {imovel_recarregado.foto_principal.url}")
                # --- FIM DEBUG ---

                fotos_galeria = request.FILES.getlist('fotos_galeria')
                print(f"Processando {len(fotos_galeria)} fotos da galeria...") # DEBUG
                for f in fotos_galeria:
                    try:
                        foto_obj = Foto.objects.create(imovel=imovel, imagem=f) 
                        print(f"Foto da galeria salva: {foto_obj.imagem.name}, URL: {foto_obj.imagem.url}") # DEBUG
                    except Exception as e_galeria:
                        print(f"!!! ERRO ao salvar foto da galeria: {f.name} !!!") # DEBUG
                        print(e_galeria) # DEBUG
                
                messages.success(request, 'Seu imóvel foi enviado para análise!')
                print("Redirecionando para meus_imoveis...") # DEBUG
                return redirect('meus_imoveis')

            except Exception as e: # Captura QUALQUER erro durante o save
                 # --- DEBUG ERRO NO SAVE ---
                print(f"!!! ERRO CRÍTICO DURANTE O SAVE (anunciar_imovel) !!!")
                print(f"Tipo do erro: {type(e)}")
                print(f"Erro: {e}")
                traceback.print_exc() # Imprime o traceback completo do erro
                 # --- FIM DEBUG ---
                messages.error(request, f'Ocorreu um erro inesperado ao salvar: {e}')
                # Não redireciona

        else: # Se form.is_valid() for False
             # --- DEBUG FORM INVÁLIDO ---
            print("Formulário (Anunciar) NÃO é válido.")
            print("Erros do formulário:")
            # Usar as_text para logs mais limpos que as_json
            print(form.errors.as_text()) 
             # --- FIM DEBUG ---
            messages.error(request, 'Por favor, corrija os erros no formulário.')

    else: # Se for GET
        form = ImovelForm()
        print("Renderizando formulário (Anunciar) para GET.") # DEBUG
    
    # Renderiza o template em caso de GET ou erro no POST
    print("Renderizando template anunciar_imovel.html (Anunciar)...") # DEBUG
    return render(request, 'contas/anunciar_imovel.html', {'form': form})

# --- View "Editar Imóvel" (COM DEBUG ADICIONADO) ---
@login_required
def editar_imovel(request, imovel_id):
    imovel = get_object_or_404(Imovel, id=imovel_id, proprietario=request.user)
    print(f"--- Iniciando editar_imovel para ID: {imovel_id} ---")
    print(f"Método da Requisição: {request.method}")

    if request.method == 'POST':
        form = ImovelForm(request.POST, request.FILES, instance=imovel)
        print("--- DEBUG FORM POST (Editar) ---")
        print(f"request.POST (primeiros 500 chars): {str(request.POST)[:500]}")
        print(f"request.FILES: {request.FILES}")
        print(f"Form is_bound: {form.is_bound}")

        if form.is_valid():
            print("Formulário (Editar) é VÁLIDO.")
            cleaned_data_preview = {k: v for k, v in form.cleaned_data.items() if k != 'descricao'}
            print(f"Dados limpos (sem descricao): {cleaned_data_preview}")
            print(f"Foto principal nos dados limpos: {form.cleaned_data.get('foto_principal')}")

            # --- INÍCIO DO TESTE DIRETO BOTO3 ---
            print("\n--- INICIANDO TESTE DIRETO BOTO3 ---")
            try:
                print("Tentando criar cliente S3 Boto3...")
                # Usar as credenciais e endpoint lidos pelo settings.py via os.getenv
                s3_client = boto3.client(
                    's3',
                    region_name=os.getenv("B2_REGION_NAME", "us-east-005"),
                    endpoint_url=f"https://{os.getenv('B2_ENDPOINT')}",
                    aws_access_key_id=os.getenv("B2_ACCESS_KEY_ID"),
                    aws_secret_access_key=os.getenv("B2_SECRET_ACCESS_KEY")
                )
                print("Cliente S3 Boto3 criado com sucesso.")
                print("Tentando listar buckets via Boto3...")
                response = s3_client.list_buckets()
                # A resposta real pode ser grande, logar apenas confirmação
                print(f"Boto3 list_buckets SUCESSO. Encontrados {len(response.get('Buckets', []))} buckets.")
                print(f"(Resposta parcial: {str(response)[:200]}...)") # Log parcial da resposta
            except Exception as boto_err:
                print(f"!!! ERRO no teste direto Boto3 !!!")
                print(f"Tipo do erro: {type(boto_err)}")
                print(f"Erro: {boto_err}")
                traceback.print_exc() # Imprime o traceback completo do erro Boto3
            print("--- FIM TESTE DIRETO BOTO3 ---\n")
            # --- FIM DO TESTE DIRETO BOTO3 ---

            try:
                print("Tentando salvar o formulário (form.save())...")
                imovel_salvo = form.save()
                print("form.save() EXECUTADO com sucesso.")
                imovel_recarregado = Imovel.objects.get(id=imovel_salvo.id)
                print(f"Foto principal NO BANCO após save: {imovel_recarregado.foto_principal.name if imovel_recarregado.foto_principal else 'None'}")
                if imovel_recarregado.foto_principal:
                    print(f"URL da foto principal gerada: {imovel_recarregado.foto_principal.url}")

                fotos_galeria = request.FILES.getlist('fotos_galeria')
                print(f"Processando {len(fotos_galeria)} fotos da galeria...")
                for f in fotos_galeria:
                    try:
                        foto_obj = Foto.objects.create(imovel=imovel_salvo, imagem=f)
                        print(f"Foto da galeria salva: {foto_obj.imagem.name}, URL: {foto_obj.imagem.url}")
                    except Exception as e_galeria:
                        print(f"!!! ERRO ao salvar foto da galeria: {f.name} !!!")
                        print(e_galeria)

                messages.success(request, 'Imóvel atualizado com sucesso!')
                print("Redirecionando para meus_imoveis...")
                return redirect('meus_imoveis')

            except Exception as e:
                print(f"!!! ERRO CRÍTICO DURANTE form.save() (editar_imovel) !!!")
                print(f"Tipo do erro: {type(e)}")
                print(f"Erro: {e}")
                traceback.print_exc()
                messages.error(request, f'Ocorreu um erro inesperado ao salvar: {e}')

        else:
            print("Formulário (Editar) NÃO é válido.")
            print("Erros do formulário:")
            print(form.errors.as_text())
            messages.error(request, 'Por favor, corrija os erros no formulário.')

    else:
        form = ImovelForm(instance=imovel)
        print("Renderizando formulário (Editar) para GET.")

    print("Renderizando template anunciar_imovel.html (Editar)...")
    return render(request, 'contas/anunciar_imovel.html', {'form': form})


# --- View "Excluir Imóvel" (Original) ---
@login_required
def excluir_imovel(request, imovel_id):
    imovel = get_object_or_404(Imovel, id=imovel_id, proprietario=request.user)
    if request.method == 'POST':
        # (Futura melhoria: excluir fotos do B2)
        imovel.delete()
        messages.success(request, 'Imóvel excluído com sucesso!')
        return redirect('meus_imoveis')
    contexto = {
        'imovel': imovel
    }
    return render(request, 'contas/excluir_imovel.html', contexto)

# --- View "Excluir Foto" (Original) ---
@login_required
def excluir_foto(request, foto_id):
    foto = get_object_or_404(Foto, id=foto_id)
    imovel_id = foto.imovel.id
    if foto.imovel.proprietario == request.user:
        # (Futura melhoria: excluir foto do B2)
        foto.delete()
        messages.success(request, 'Foto excluída com sucesso.')
    else:
        messages.error(request, 'Você não tem permissão para excluir esta foto.')
    # Corrigido para usar o ID do imóvel correto
    return redirect('editar_imovel', imovel_id=imovel_id) 

# --- View "Perfil" (Original) ---
@login_required
def perfil(request):
    if request.method == 'POST':
        if 'update_user' in request.POST:
            user_form = UserUpdateForm(request.POST, instance=request.user)
            password_form = CustomPasswordChangeForm(request.user) # Mantém o form de senha limpo
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Suas informações foram atualizadas com sucesso!')
                return redirect('perfil')
            # Se o user_form não for válido, renderiza ambos os forms com erros
        
        elif 'change_password' in request.POST:
            password_form = CustomPasswordChangeForm(request.user, request.POST)
            user_form = UserUpdateForm(instance=request.user) # Mantém o form de usuário com dados atuais
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Sua senha foi alterada com sucesso!')
                return redirect('perfil')
            # Se o password_form não for válido, renderiza ambos os forms com erros
        
        # Se nenhum botão foi pressionado ou houve erro, inicializa ambos
        else:
             user_form = UserUpdateForm(request.POST, instance=request.user) # Recarrega com POST data se houver erro
             password_form = CustomPasswordChangeForm(request.user, request.POST) # Recarrega com POST data se houver erro
    
    # Se for GET ou se houve erro no POST e precisamos re-renderizar
    else:
        user_form = UserUpdateForm(instance=request.user)
        password_form = CustomPasswordChangeForm(request.user)

    contexto = {
        'user_form': user_form,
        'password_form': password_form
    }
    return render(request, 'contas/perfil.html', contexto)