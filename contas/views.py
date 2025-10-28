# contas/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, UserUpdateForm, CustomPasswordChangeForm
from imoveis.models import Imovel, Foto
from imoveis.forms import ImovelForm
from django.contrib.auth import update_session_auth_hash

# --- IMPORTAÇÕES ADICIONADAS PARA O UPLOAD MANUAL BOTO3 ---
import boto3
import os
import traceback
from django.conf import settings
from io import BytesIO
# -----------------------------------------------------------

# --- FUNÇÃO HELPER PARA UPLOAD MANUAL BOTO3 ---
def upload_arquivo_para_b2(arquivo_em_memoria, nome_arquivo_no_bucket):
    """
    Usa boto3 puro para enviar um arquivo para o Backblaze B2.
    """
    try:
        # Pega as credenciais diretamente (como no nosso teste que funcionou)
        s3_client = boto3.client(
            's3',
            endpoint_url=f"https://{os.environ.get('B2_ENDPOINT')}",
            aws_access_key_id=os.environ.get('B2_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('B2_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('B2_REGION_NAME'),
            config=boto3.session.Config(signature_version='s3v4'),
        )
        
        bucket_name = os.environ.get('B2_BUCKET_NAME')
        
        # Reposiciona o ponteiro do arquivo para o início
        arquivo_em_memoria.seek(0)
        
        # Define o caminho completo dentro do bucket (conforme settings.py)
        caminho_completo = f"media/{nome_arquivo_no_bucket}"
        
        s3_client.put_object(
            Bucket=bucket_name,
            Key=caminho_completo,
            Body=arquivo_em_memoria,
            ContentType=arquivo_em_memoria.content_type,
            ACL='public-read' # Garante que o arquivo seja público
        )
        print(f"Boto3 SUCESSO: Enviado {caminho_completo}")
        
        # Retorna o caminho que será salvo no banco de dados
        return nome_arquivo_no_bucket
        
    except Exception as e:
        print(f"--- ERRO BOTO3 UPLOAD MANUAL: {e} ---")
        traceback.print_exc()
        return None
# ----------------------------------------

# --- View de Cadastro (sem alterações) ---
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

# --- View do Dashboard "Meus Imóveis" (sem alterações) ---
@login_required
def meus_imoveis(request):
    imoveis_do_usuario = Imovel.objects.filter(proprietario=request.user).order_by('-data_cadastro')
    contexto = {
        'imoveis': imoveis_do_usuario
    }
    return render(request, 'contas/meus_imoveis.html', contexto)

# --- View "Anunciar Imóvel" (MODIFICADA para Boto3) ---
@login_required
def anunciar_imovel(request):
    if request.method == 'POST':
        form = ImovelForm(request.POST, request.FILES)
        if form.is_valid():
            imovel = form.save(commit=False)
            imovel.proprietario = request.user
            
            foto_principal = form.cleaned_data.get('foto_principal')
            imovel.foto_principal = None # Limpa temporariamente

            imovel.save() # Salva o Imovel primeiro para ter um ID
            
            if foto_principal:
                path_foto_principal = Imovel._meta.get_field('foto_principal').upload_to(imovel, foto_principal.name)
                
                caminho_salvo = upload_arquivo_para_b2(foto_principal, path_foto_principal)
                if caminho_salvo:
                    imovel.foto_principal.name = caminho_salvo
                    imovel.save() # Atualiza o Imovel com o caminho da foto
                else:
                    messages.error(request, "Falha ao enviar a foto principal.")
                    imovel.delete()
                    return render(request, 'contas/anunciar_imovel.html', {'form': form})
            
            fotos_galeria = request.FILES.getlist('fotos_galeria')
            fotos_com_falha = []
            for f in fotos_galeria:
                path_foto_galeria = Foto._meta.get_field('imagem').upload_to(None, f.name)
                
                caminho_foto_salva = upload_arquivo_para_b2(f, path_foto_galeria)
                if caminho_foto_salva:
                    Foto.objects.create(imovel=imovel, imagem=caminho_foto_salva)
                else:
                    fotos_com_falha.append(f.name)
            
            if fotos_com_falha:
                messages.warning(request, f"Imóvel anunciado, mas falha ao enviar algumas fotos da galeria: {', '.join(fotos_com_falha)}")
            else:
                messages.success(request, 'Seu imóvel foi anunciado com sucesso!')
            
            return redirect('meus_imoveis')
    else:
        form = ImovelForm()
    
    return render(request, 'contas/anunciar_imovel.html', {'form': form})

# --- View "Editar Imóvel" (MODIFICADA para Boto3) ---
@login_required
def editar_imovel(request, imovel_id):
    imovel = get_object_or_404(Imovel, id=imovel_id, proprietario=request.user)
    
    if request.method == 'POST':
        form = ImovelForm(request.POST, request.FILES, instance=imovel)
        if form.is_valid():
            imovel_editado = form.save(commit=False)
            
            foto_principal = request.FILES.get('foto_principal')
            if foto_principal: # Se uma nova foto principal foi enviada
                path_foto_principal = Imovel._meta.get_field('foto_principal').upload_to(imovel_editado, foto_principal.name)
                caminho_salvo = upload_arquivo_para_b2(foto_principal, path_foto_principal)
                
                if caminho_salvo:
                    imovel_editado.foto_principal.name = caminho_salvo
                else:
                    messages.error(request, "Falha ao enviar a nova foto principal.")
                    return render(request, 'contas/anunciar_imovel.html', {'form': form})
            
            imovel_editado.save()
            form.save_m2m()
            
            fotos_galeria = request.FILES.getlist('fotos_galeria')
            fotos_com_falha = []
            for f in fotos_galeria:
                path_foto_galeria = Foto._meta.get_field('imagem').upload_to(None, f.name)
                
                caminho_foto_salva = upload_arquivo_para_b2(f, path_foto_galeria)
                if caminho_foto_salva:
                    Foto.objects.create(imovel=imovel_editado, imagem=caminho_foto_salva)
                else:
                    fotos_com_falha.append(f.name)

            if fotos_com_falha:
                 messages.warning(request, f"Imóvel atualizado, mas falha ao enviar novas fotos da galeria: {', '.join(fotos_com_falha)}")
            else:
                messages.success(request, 'Imóvel atualizado com sucesso!')
            
            return redirect('meus_imoveis')
    else:
        form = ImovelForm(instance=imovel)
        
    return render(request, 'contas/anunciar_imovel.html', {'form': form})

# --- View "Excluir Imóvel" (sem alterações) ---
@login_required
def excluir_imovel(request, imovel_id):
    imovel = get_object_or_404(Imovel, id=imovel_id, proprietario=request.user)
    if request.method == 'POST':
        # (Futura melhoria: excluir fotos do B2 antes de deletar o imóvel)
        imovel.delete()
        messages.success(request, 'Imóvel excluído com sucesso!')
        return redirect('meus_imoveis')
    contexto = {
        'imovel': imovel
    }
    return render(request, 'contas/excluir_imovel.html', contexto)

# --- View "Excluir Foto" (MODIFICADA para Boto3) ---
@login_required
def excluir_foto(request, foto_id):
    foto = get_object_or_404(Foto, id=foto_id)
    imovel_id = foto.imovel.id
    
    if foto.imovel.proprietario == request.user:
        try:
            s3_client = boto3.client(
                's3',
                endpoint_url=f"https://{os.environ.get('B2_ENDPOINT')}",
                aws_access_key_id=os.environ.get('B2_ACCESS_KEY_ID'),
                aws_secret_access_key=os.environ.get('B2_SECRET_ACCESS_KEY'),
                region_name=os.environ.get('B2_REGION_NAME'),
                config=boto3.session.Config(signature_version='s3v4'),
            )
            bucket_name = os.environ.get('B2_BUCKET_NAME')
            
            caminho_completo = f"media/{foto.imagem.name}"
            
            s3_client.delete_object(Bucket=bucket_name, Key=caminho_completo)
            print(f"Boto3 SUCESSO: Excluído {caminho_completo}")
            
            foto.delete()
            messages.success(request, 'Foto excluída com sucesso.')
            
        except Exception as e:
            print(f"--- ERRO BOTO3 EXCLUIR FOTO: {e} ---")
            traceback.print_exc()
            messages.error(request, 'Falha ao excluir a foto do armazenamento.')
        
    else:
        messages.error(request, 'Você não tem permissão para excluir esta foto.')
        
    return redirect('editar_imovel', imovel_id=imovel_id)

# --- View "Perfil" (sem alterações) ---
@login_required
def perfil(request):
    if request.method == 'POST':
        if 'update_user' in request.POST:
            user_form = UserUpdateForm(request.POST, instance=request.user)
            password_form = CustomPasswordChangeForm(request.user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Suas informações foram atualizadas com sucesso!')
                return redirect('perfil')
        
        elif 'change_password' in request.POST:
            password_form = CustomPasswordChangeForm(request.user, request.POST)
            user_form = UserUpdateForm(instance=request.user)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Sua senha foi alterada com sucesso!')
                return redirect('perfil')
    else:
        user_form = UserUpdateForm(instance=request.user)
        password_form = CustomPasswordChangeForm(request.user)

    contexto = {
        'user_form': user_form,
        'password_form': password_form
    }
    return render(request, 'contas/perfil.html', contexto)