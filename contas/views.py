# contas/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, UserUpdateForm, CustomPasswordChangeForm
from imoveis.models import Imovel, Foto # Importar Imovel, Foto
from imoveis.forms import ImovelForm
from django.contrib.auth import update_session_auth_hash
import traceback 
import os 
import boto3 
from django.conf import settings 
from django.core.files.uploadedfile import InMemoryUploadedFile # Importar para checar tipo

# Função auxiliar para gerar nome de arquivo único (opcional, mas bom)
import uuid
from pathlib import Path

def generate_unique_filename(filename):
    """Gera um nome de arquivo único mantendo a extensão."""
    ext = Path(filename).suffix
    new_filename = f"{uuid.uuid4()}{ext}"
    return new_filename

# Função auxiliar para fazer o upload manual via Boto3
def upload_to_b2(file_obj, object_name):
    """Faz upload de um objeto de arquivo para B2 usando Boto3."""
    print(f"--- Iniciando upload_to_b2 para: {object_name} ---")
    try:
        s3_client = boto3.client(
            's3',
            region_name=os.getenv("B2_REGION_NAME", "us-east-005"),
            endpoint_url=f"https://{os.getenv('B2_ENDPOINT')}",
            aws_access_key_id=os.getenv("B2_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("B2_SECRET_ACCESS_KEY")
        )
        print("Cliente S3 Boto3 criado.")

        bucket_name = os.getenv("B2_BUCKET_NAME")
        
        # Voltar ao início do arquivo para leitura
        file_obj.seek(0) 
        
        print(f"Executando put_object: Bucket={bucket_name}, Key={object_name}, ContentType={file_obj.content_type}")
        s3_client.put_object(
            Bucket=bucket_name,
            Key=object_name,
            Body=file_obj,
            ContentType=file_obj.content_type # Usa o content type detectado pelo Django
        )
        print(f"SUCESSO: Upload Boto3 concluído para {object_name}")
        return True # Indica sucesso
    except Exception as e:
        print(f"!!! ERRO no upload_to_b2 para {object_name} !!!")
        print(f"Tipo do erro: {type(e)}")
        print(f"Erro: {e}")
        traceback.print_exc()
        return False # Indica falha
        
# --- View de Cadastro (Original - Sem mudanças) ---
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

# --- View do Dashboard "Meus Imóveis" (Original - Sem mudanças) ---
@login_required
def meus_imoveis(request):
    imoveis_do_usuario = Imovel.objects.filter(proprietario=request.user).order_by('-data_cadastro')
    contexto = {
        'imoveis': imoveis_do_usuario
    }
    return render(request, 'contas/meus_imoveis.html', contexto)

# --- View "Anunciar Imóvel" (Usa a lógica condicional DEBUG/PRODUÇÃO) ---
@login_required
def anunciar_imovel(request):
    print(f"--- Iniciando anunciar_imovel ---")
    print(f"Método da Requisição: {request.method}")

    if request.method == 'POST':
        form = ImovelForm(request.POST, request.FILES)
        print("--- DEBUG FORM POST (Anunciar) ---")
        print(f"request.FILES: {request.FILES}") 

        if form.is_valid():
            print("Formulário (Anunciar) é VÁLIDO.")
            foto_principal_obj = form.cleaned_data.get('foto_principal')
            fotos_galeria_list = request.FILES.getlist('fotos_galeria') # Pegar direto do request.FILES

            try:
                # 1. Salva os dados do Imovel SEM a foto principal primeiro
                imovel = form.save(commit=False)
                imovel.proprietario = request.user
                imovel.foto_principal = None # Limpa o campo de foto temporariamente
                print("Salvando dados do imóvel (sem foto ainda)...")
                imovel.save() 
                print(f"Imóvel salvo (sem foto) ID: {imovel.id}")

                # 2. Faz o upload manual da foto principal, se houver
                upload_principal_success = True # Assume sucesso se não houver foto
                if foto_principal_obj and isinstance(foto_principal_obj, InMemoryUploadedFile):
                    original_filename = foto_principal_obj.name
                    unique_filename = generate_unique_filename(original_filename)
                    # Caminho completo no B2 (incluindo AWS_LOCATION)
                    b2_object_name = f"{settings.AWS_LOCATION}/fotos_imoveis/{unique_filename}" 
                    
                    print(f"Iniciando upload manual para foto principal: {b2_object_name}")
                    upload_principal_success = upload_to_b2(foto_principal_obj, b2_object_name)
                    
                    if upload_principal_success:
                        # 3. Atualiza o campo foto_principal no banco SÓ COM O CAMINHO
                        imovel.foto_principal.name = f"fotos_imoveis/{unique_filename}" 
                        print(f"Atualizando DB com caminho da foto principal: {imovel.foto_principal.name}")
                        imovel.save(update_fields=['foto_principal']) # Salva apenas este campo
                    else:
                         messages.error(request, f'Falha ao fazer upload da foto principal: {original_filename}')
                         # Decide se quer continuar ou parar se o upload principal falhar
                         # return render(request, 'contas/anunciar_imovel.html', {'form': form})

                # 4. Faz o upload manual das fotos da galeria, se houver e principal deu certo
                if upload_principal_success and fotos_galeria_list:
                    print(f"Processando {len(fotos_galeria_list)} fotos da galeria manualmente...")
                    for file_obj in fotos_galeria_list:
                         if isinstance(file_obj, InMemoryUploadedFile):
                            original_filename = file_obj.name
                            unique_filename = generate_unique_filename(original_filename)
                            b2_object_name = f"{settings.AWS_LOCATION}/fotos_galeria/{unique_filename}"
                            
                            print(f"Iniciando upload manual para foto galeria: {b2_object_name}")
                            upload_galeria_success = upload_to_b2(file_obj, b2_object_name)
                            
                            if upload_galeria_success:
                                # Cria o objeto Foto no banco SÓ COM O CAMINHO
                                Foto.objects.create(imovel=imovel, imagem=f"fotos_galeria/{unique_filename}")
                                print(f"Salvo no DB foto galeria: fotos_galeria/{unique_filename}")
                            else:
                                messages.warning(request, f'Falha ao fazer upload da foto da galeria: {original_filename}')
                                # Continua processando as outras fotos da galeria

                if upload_principal_success: # Se o principal deu certo (mesmo que galeria falhe)
                    messages.success(request, 'Seu imóvel foi enviado para análise!')
                    print("Redirecionando para meus_imoveis...") 
                    return redirect('meus_imoveis')
                # Se chegou aqui, o upload principal falhou e não redirecionamos antes

            except Exception as e: 
                print(f"!!! ERRO CRÍTICO GERAL (anunciar_imovel) !!!")
                print(f"Tipo do erro: {type(e)}")
                print(f"Erro: {e}")
                traceback.print_exc() 
                messages.error(request, f'Ocorreu um erro inesperado: {e}')
                
        else: # Se form.is_valid() for False
            print("Formulário (Anunciar) NÃO é válido.")
            print(form.errors.as_text()) 
            messages.error(request, 'Por favor, corrija os erros no formulário.')

    else: # Se for GET
        form = ImovelForm()
        print("Renderizando formulário (Anunciar) para GET.") 
    
    print("Renderizando template anunciar_imovel.html (Anunciar)...") 
    return render(request, 'contas/anunciar_imovel.html', {'form': form})

# --- View "Editar Imóvel" (COM UPLOAD MANUAL BOTO3) ---
@login_required
def editar_imovel(request, imovel_id):
    imovel = get_object_or_404(Imovel, id=imovel_id, proprietario=request.user)
    print(f"--- Iniciando editar_imovel para ID: {imovel_id} ---")
    print(f"Método da Requisição: {request.method}")

    if request.method == 'POST':
        form = ImovelForm(request.POST, request.FILES, instance=imovel)
        print("--- DEBUG FORM POST (Editar) ---")
        print(f"request.FILES: {request.FILES}") 
        
        if form.is_valid():
            print("Formulário (Editar) é VÁLIDO.")
            foto_principal_obj = form.cleaned_data.get('foto_principal') # Pode ser None, False ou um arquivo
            fotos_galeria_list = request.FILES.getlist('fotos_galeria')

            try:
                # 1. Salva os dados do Imovel SEM a foto principal
                # Verifica se o campo foto_principal foi marcado para limpar (checkbox no form?)
                # Se o form inclui um checkbox "limpar foto", form.cleaned_data['foto_principal'] será False
                limpar_foto_principal = foto_principal_obj is False 

                imovel_atualizado = form.save(commit=False) # Não salva ainda

                # Guarda o nome da foto antiga, caso precise deletar do B2 (futuro)
                foto_antiga = imovel.foto_principal.name if imovel.foto_principal else None

                # Se for limpar ou se uma nova foto foi enviada, limpa o campo antes do save principal
                if limpar_foto_principal or (foto_principal_obj and isinstance(foto_principal_obj, InMemoryUploadedFile)):
                     imovel_atualizado.foto_principal = None 

                print("Salvando dados do imóvel (sem/com foto antiga)...")
                imovel_atualizado.save()
                print(f"Imóvel atualizado (passo 1) ID: {imovel_atualizado.id}")

                # 2. Processa a foto principal (limpar ou fazer upload novo)
                upload_principal_success = True # Assume sucesso por padrão

                if limpar_foto_principal:
                    print("Limpando foto principal (já feito no save anterior).")
                    # Aqui você poderia adicionar a lógica para deletar 'foto_antiga' do B2
                
                elif foto_principal_obj and isinstance(foto_principal_obj, InMemoryUploadedFile):
                    # Nova foto enviada, faz upload manual
                    original_filename = foto_principal_obj.name
                    unique_filename = generate_unique_filename(original_filename)
                    b2_object_name = f"{settings.AWS_LOCATION}/fotos_imoveis/{unique_filename}"
                    
                    print(f"Iniciando upload manual para NOVA foto principal: {b2_object_name}")
                    upload_principal_success = upload_to_b2(foto_principal_obj, b2_object_name)

                    if upload_principal_success:
                        # Atualiza o campo no banco SÓ COM O CAMINHO
                        imovel_atualizado.foto_principal.name = f"fotos_imoveis/{unique_filename}"
                        print(f"Atualizando DB com caminho da NOVA foto principal: {imovel_atualizado.foto_principal.name}")
                        imovel_atualizado.save(update_fields=['foto_principal'])
                        # Aqui você poderia adicionar a lógica para deletar 'foto_antiga' do B2
                    else:
                        messages.error(request, f'Falha ao fazer upload da NOVA foto principal: {original_filename}')
                        # Decide se quer parar ou continuar
                        # return render(request, 'contas/anunciar_imovel.html', {'form': form})

                # 3. Processa fotos da galeria (APENAS NOVAS FOTOS)
                if upload_principal_success and fotos_galeria_list:
                    print(f"Processando {len(fotos_galeria_list)} NOVAS fotos da galeria manualmente...")
                    for file_obj in fotos_galeria_list:
                         if isinstance(file_obj, InMemoryUploadedFile):
                            original_filename = file_obj.name
                            unique_filename = generate_unique_filename(original_filename)
                            b2_object_name = f"{settings.AWS_LOCATION}/fotos_galeria/{unique_filename}"
                            
                            print(f"Iniciando upload manual para NOVA foto galeria: {b2_object_name}")
                            upload_galeria_success = upload_to_b2(file_obj, b2_object_name)
                            
                            if upload_galeria_success:
                                Foto.objects.create(imovel=imovel_atualizado, imagem=f"fotos_galeria/{unique_filename}")
                                print(f"Salvo no DB NOVA foto galeria: fotos_galeria/{unique_filename}")
                            else:
                                messages.warning(request, f'Falha ao fazer upload da NOVA foto da galeria: {original_filename}')
                
                if upload_principal_success:
                    messages.success(request, 'Imóvel atualizado com sucesso!')
                    print("Redirecionando para meus_imoveis...") 
                    return redirect('meus_imoveis')

            except Exception as e: 
                print(f"!!! ERRO CRÍTICO GERAL (editar_imovel) !!!")
                print(f"Tipo do erro: {type(e)}")
                print(f"Erro: {e}")
                traceback.print_exc() 
                messages.error(request, f'Ocorreu um erro inesperado ao atualizar: {e}')

        else: # Se form.is_valid() for False
            print("Formulário (Editar) NÃO é válido.")
            print(form.errors.as_text()) 
            messages.error(request, 'Por favor, corrija os erros no formulário.')

    else: # Se for GET
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

# --- View "Perfil" (Original - Sem mudanças) ---
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