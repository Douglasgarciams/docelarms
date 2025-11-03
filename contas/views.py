# contas/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, UserUpdateForm, CustomPasswordChangeForm
from imoveis.models import Imovel, Foto, Plano, Assinatura 
from imoveis.forms import ImovelForm
from django.contrib.auth import update_session_auth_hash
import traceback 
import os 
import boto3 
from django.conf import settings 
from django.core.files.uploadedfile import InMemoryUploadedFile
import uuid
from pathlib import Path
import mercadopago

# Importar Pillow para manipulação de imagens
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# --- [IMPORTAÇÕES ADICIONADAS] ---
from django.utils import timezone
from datetime import timedelta
# ---------------------------------

# Função auxiliar para gerar nome de arquivo único
def generate_unique_filename(filename):
    """Gera um nome de arquivo único mantendo a extensão."""
    ext = Path(filename).suffix
    new_filename = f"{uuid.uuid4()}{ext}"
    return new_filename

# --- NOVA FUNÇÃO: Adicionar marca d'água ---
def add_watermark(image_file, watermark_text="USO EXCLUSIVO DE DOCELARMS", font_path=None):
    """
    Adiciona uma marca d'água centralizada e em negrito a uma imagem.
    image_file: objeto de arquivo (BytesIO ou similar) da imagem original.
    watermark_text: O texto da marca d'água.
    font_path: Caminho para um arquivo de fonte .ttf. Se None, usará uma fonte padrão.
    """
    print(f"--- Adicionando marca d'água: '{watermark_text}' ---")
    try:
        # Abre a imagem
        img = Image.open(image_file).convert("RGBA")
        width, height = img.size

        draw = ImageDraw.Draw(img)

        # Tenta carregar uma fonte negrito ou usa a padrão
        try:
            if font_path and os.path.exists(font_path):
                font = ImageFont.truetype(font_path, int(height / 20)) # Tamanho da fonte proporcional
            else:
                try:
                    font = ImageFont.truetype("arialbd.ttf", int(height / 20)) # Windows
                except IOError:
                    try:
                        font = ImageFont.truetype("DejaVuSans-Bold.ttf", int(height / 20)) # Linux/macOS
                    except IOError:
                        font = ImageFont.load_default()
                        print("Aviso: Nenhuma fonte negrito específica encontrada, usando fonte padrão.")

        except Exception as e:
            print(f"Erro ao carregar fonte, usando padrão: {e}")
            font = ImageFont.load_default()
        
        text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        x = (width - text_width) / 2
        y = (height - text_height) / 2

        draw.text((x, y), watermark_text, font=font, fill=(0, 0, 0, 255)) # Preto com opacidade total

        buffer = BytesIO()
        if img.mode == "RGBA":
            img.save(buffer, format="PNG")
        else:
            img.convert("RGB").save(buffer, format="JPEG")

        buffer.seek(0)
        print("Marca d'água adicionada com sucesso.")
        return buffer
    except Exception as e:
        print(f"!!! ERRO ao adicionar marca d'água: {e} !!!")
        traceback.print_exc()
        image_file.seek(0)
        return image_file

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
        
        file_obj.seek(0) 

        watermarked_file_buffer = add_watermark(file_obj)
        if watermarked_file_buffer != file_obj:
            try:
                temp_img = Image.open(watermarked_file_buffer)
                if temp_img.format == 'PNG':
                    content_type = 'image/png'
                elif temp_img.format == 'JPEG':
                    content_type = 'image/jpeg'
                else:
                    content_type = file_obj.content_type
                watermarked_file_buffer.seek(0)
            except Exception:
                content_type = file_obj.content_type
        else:
            content_type = file_obj.content_type
        
        print(f"Executando put_object: Bucket={bucket_name}, Key={object_name}, ContentType={content_type}")
        s3_client.put_object(
            Bucket=bucket_name,
            Key=object_name,
            Body=watermarked_file_buffer,
            ContentType=content_type
        )
        print(f"SUCESSO: Upload Boto3 concluído para {object_name}")
        return True
    except Exception as e:
        print(f"!!! ERRO no upload_to_b2 para {object_name} !!!")
        print(f"Tipo do erro: {type(e)}")
        print(f"Erro: {e}")
        traceback.print_exc()
        return False
        
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

# --- View do Dashboard "Meus Imóveis" (ATUALIZADA COM VERIFICAÇÃO DE EXPIRAÇÃO) ---
@login_required
def meus_imoveis(request):
    
    agora = timezone.now()

    # --- [INÍCIO DA CORREÇÃO - O "VIGIA"] ---
    # 1. Tenta verificar a assinatura do usuário
    try:
        assinatura = request.user.assinatura
        
        # 2. Se a assinatura está 'ATIVA' mas a data de expiração já passou...
        if assinatura.status == 'ATIVA' and assinatura.data_expiracao and assinatura.data_expiracao < agora:
            
            print(f"Assinatura (ID: {assinatura.id}) do usuário {request.user.username} expirou. Atualizando status...")
            
            # 3. Muda o status da ASSINATURA para 'EXPIRADA'
            assinatura.status = Assinatura.StatusAssinatura.EXPIRADA
            assinatura.save(update_fields=['status'])
            
            # 4. Muda o status de todos os IMÓVEIS ATIVOS dele para 'EXPIRADO'
            Imovel.objects.filter(
                proprietario=request.user,
                status_publicacao='ATIVO'
            ).update(status_publicacao=Imovel.StatusPublicacao.EXPIRADO)
            
            print("Imóveis ativos do usuário foram atualizados para 'Expirado'.")
            
    except Assinatura.DoesNotExist:
        pass # Sem assinatura, não faz nada
    except Exception as e:
        # Proteção para não quebrar a página se algo der errado na verificação
        print(f"Erro ao verificar expiração de assinatura: {e}")
    # --- [FIM DA CORREÇÃO] ---

    # Agora, a query de imóveis vai buscar os status ATUALIZADOS do banco
    imoveis_do_usuario = Imovel.objects.filter(proprietario=request.user).order_by('-data_cadastro')
    
    contexto = {
        'imoveis': imoveis_do_usuario
    }
    return render(request, 'contas/meus_imoveis.html', contexto)

# --- View "Anunciar Imóvel" (LOGICA ATUALIZADA) ---
@login_required
def anunciar_imovel(request):
    print(f"--- Iniciando anunciar_imovel ---")
    print(f"Método da Requisição: {request.method}")

    # --- [LÓGICA DE ASSINATURA ATUALIZADA] ---
    assinatura_usuario = None # Começa como 'Nenhuma'
    assinatura_valida_para_postar = False # Começa como 'Não'
    agora = timezone.now() # Pega a hora atual
    
    try:
        assinatura_usuario = request.user.assinatura
        
        # --- [CORREÇÃO AQUI] ---
        # 1. Verifica se o plano dela está ativo (visível)
        plano_esta_ativo = assinatura_usuario.plano and assinatura_usuario.plano.is_ativo
        
        # 2. Verifica se a ASSINATURA está Ativa (não pendente, não cancelada)
        assinatura_esta_ativa = assinatura_usuario.status == 'ATIVA'
        
        # 3. Verifica se a ASSINATURA não expirou
        assinatura_nao_expirou = assinatura_usuario.data_expiracao and assinatura_usuario.data_expiracao > agora

        if plano_esta_ativo and assinatura_esta_ativa and assinatura_nao_expirou:
            assinatura_valida_para_postar = True
        # --- [FIM DA CORREÇÃO] ---
            
    except Assinatura.DoesNotExist:
        pass # Não tem assinatura, 'assinatura_usuario' = None
    # --- [FIM DA LÓGICA DE ASSINATURA] ---

    if request.method == 'POST':
        form = ImovelForm(request.POST, request.FILES)
        print("--- DEBUG FORM POST (Anunciar) ---")
        print(f"request.FILES: {request.FILES}") 

        # --- [REGRA DE NEGÓCIO ATUALIZADA] ---
        # 3. VERIFICA SE O USUÁRIO TEM QUALQUER PLANO (MESMO PENDENTE)
        if not assinatura_usuario:
            messages.error(request, "Você não possui um plano selecionado. Por favor, escolha um plano para poder anunciar.")
            return redirect('listar_planos') 

        if form.is_valid():
            print("Formulário (Anunciar) é VÁLIDO.")

            # 4. Verificação de Limite de Anúncios
            limite_anuncios = assinatura_usuario.plano.limite_anuncios
            anuncios_existentes_count = Imovel.objects.filter(
                proprietario=request.user, 
                status_publicacao__in=['ATIVO', 'PEND_APROV']
            ).count()
            
            print(f"Plano: {assinatura_usuario.plano.nome}, Limite Anúncios: {limite_anuncios}, Anúncios Existentes: {anuncios_existentes_count}")

            # 5. APLICAR REGRA DE ANÚNCIO! (Só permite se a assinatura for válida)
            if not assinatura_valida_para_postar and anuncios_existentes_count >= limite_anuncios:
                messages.error(request, f"Erro: Seu plano ({assinatura_usuario.plano.nome}) não está ativo ou expirou. Você não pode postar novos anúncios.")
                return redirect('meus_imoveis') 
            elif anuncios_existentes_count >= limite_anuncios:
                messages.error(request, f"Erro: Seu plano ({assinatura_usuario.plano.nome}) permite no máximo {limite_anuncios} anúncio(s) ativo(s) ou em análise. Você já atingiu seu limite.")
                return redirect('meus_imoveis') 

            # 6. Verificação de Limite de Fotos
            limite_de_fotos = assinatura_usuario.plano.limite_fotos
            fotos_galeria_list = request.FILES.getlist('fotos_galeria')
            quantidade_enviada = len(fotos_galeria_list)
            
            print(f"Limite Fotos: {limite_de_fotos}, Enviadas: {quantidade_enviada}")

            if quantidade_enviada > limite_de_fotos:
                messages.error(request, f"Erro: Seu plano ({assinatura_usuario.plano.nome}) permite no máximo {limite_de_fotos} fotos na galeria, mas você tentou enviar {quantidade_enviada}.")
                contexto = {'form': form, 'assinatura': assinatura_usuario, 'assinatura_ativa': assinatura_valida_para_postar}
                return render(request, 'contas/anunciar_imovel.html', contexto)
            
            # --- [FIM DA LÓGICA ATUALIZADA] ---

            foto_principal_obj = form.cleaned_data.get('foto_principal')
            
            try:
                imovel = form.save(commit=False)
                imovel.proprietario = request.user
                imovel.foto_principal = None 
                print("Salvando dados do imóvel...")
                imovel.save() 
                print(f"Imóvel salvo (sem foto) ID: {imovel.id}")

                upload_principal_success = True
                if foto_principal_obj and isinstance(foto_principal_obj, InMemoryUploadedFile):
                    original_filename = foto_principal_obj.name
                    unique_filename = generate_unique_filename(original_filename)
                    b2_object_name = f"{settings.AWS_LOCATION}/fotos_imoveis/{unique_filename}" 
                    
                    print(f"Iniciando upload manual para foto principal: {b2_object_name}")
                    upload_principal_success = upload_to_b2(foto_principal_obj, b2_object_name)
                    
                    if upload_principal_success:
                        imovel.foto_principal.name = f"fotos_imoveis/{unique_filename}" 
                        print(f"Atualizando DB com caminho da foto principal: {imovel.foto_principal.name}")
                        imovel.save(update_fields=['foto_principal'])
                    else:
                        messages.error(request, f'Falha ao fazer upload da foto principal: {original_filename}')

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
                                Foto.objects.create(imovel=imovel, imagem=f"fotos_galeria/{unique_filename}")
                                print(f"Salvo no DB foto galeria: fotos_galeria/{unique_filename}")
                            else:
                                messages.warning(request, f'Falha ao fazer upload da foto da galeria: {original_filename}')

                if upload_principal_success:
                    messages.success(request, 'Seu imóvel foi enviado para análise! Ele aparecerá no site assim que o pagamento e o conteúdo forem aprovados.')
                    print("Redirecionando para meus_imoveis...") 
                    return redirect('meus_imoveis')

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
            
            contexto = {'form': form, 'assinatura': assinatura_usuario, 'assinatura_ativa': assinatura_valida_para_postar}
            return render(request, 'contas/anunciar_imovel.html', contexto)

    else: # Se for GET
        if not assinatura_usuario:
            messages.error(request, "Você precisa escolher um plano antes de anunciar.")
            return redirect('listar_planos') 

        form = ImovelForm()
        print("Renderizando formulário (Anunciar) para GET.") 
    
    contexto = {
        'form': form,
        'assinatura': assinatura_usuario,
        'assinatura_ativa': assinatura_valida_para_postar
    }
    print(f"Renderizando template com assinatura: {assinatura_usuario} | É válida? {assinatura_valida_para_postar}")
    return render(request, 'contas/anunciar_imovel.html', contexto)

# --- View "Editar Imóvel" (LOGICA ATUALIZADA) ---
@login_required
def editar_imovel(request, imovel_id):
    imovel = get_object_or_404(Imovel, id=imovel_id, proprietario=request.user)
    print(f"--- Iniciando editar_imovel para ID: {imovel_id} ---")
    print(f"Método da Requisição: {request.method}")

    # --- [LÓGICA DE ASSINATURA ATUALIZADA] ---
    assinatura_usuario = None
    assinatura_valida_para_postar = False
    agora = timezone.now()
    
    try:
        assinatura_usuario = request.user.assinatura
        
        # --- [CORREÇÃO AQUI] ---
        plano_esta_ativo = assinatura_usuario.plano and assinatura_usuario.plano.is_ativo
        assinatura_esta_ativa = assinatura_usuario.status == 'ATIVA'
        assinatura_nao_expirou = assinatura_usuario.data_expiracao and assinatura_usuario.data_expiracao > agora

        if plano_esta_ativo and assinatura_esta_ativa and assinatura_nao_expirou:
            assinatura_valida_para_postar = True
        # --- [FIM DA CORREÇÃO] ---
            
    except Assinatura.DoesNotExist:
        pass
    # --- [FIM DA LÓGICA DE ASSINATURA] ---


    if request.method == 'POST':
        form = ImovelForm(request.POST, request.FILES, instance=imovel) 
        print("--- DEBUG FORM POST (Editar) ---")
        print(f"request.FILES: {request.FILES}") 
        
        if not assinatura_usuario:
            messages.error(request, "Você não possui um plano ativo. Por favor, contate o suporte para editar seus anúncios.")
            return redirect('meus_imoveis') 

        if form.is_valid():
            print("Formulário (Editar) é VÁLIDO.")
            
            limite_de_fotos = assinatura_usuario.plano.limite_fotos
            fotos_atuais = Foto.objects.filter(imovel=imovel).count()
            fotos_galeria_list = request.FILES.getlist('fotos_galeria')
            quantidade_novas = len(fotos_galeria_list)
            total_fotos = fotos_atuais + quantidade_novas

            print(f"Plano: {assinatura_usuario.plano.nome}, Limite: {limite_de_fotos}, Fotos Atuais: {fotos_atuais}, Novas: {quantidade_novas}, Total: {total_fotos}")

            if total_fotos > limite_de_fotos:
                print("!!! ERRO: Usuário enviou mais fotos que o limite do plano (EDITAR).")
                messages.error(
                    request, 
                    f"Erro: Seu plano ({assinatura_usuario.plano.nome}) permite no máximo {limite_de_fotos} fotos. Você já possui {fotos_atuais} e tentou adicionar mais {quantidade_novas}, ultrapassando o limite."
                )
                contexto = {'form': form, 'assinatura': assinatura_usuario, 'assinatura_ativa': assinatura_valida_para_postar}
                return render(request, 'contas/anunciar_imovel.html', contexto)

            foto_principal_obj = form.cleaned_data.get('foto_principal')

            try:
                limpar_foto_principal = foto_principal_obj is False 
                imovel_atualizado = form.save(commit=False)
                foto_antiga = imovel.foto_principal.name if imovel.foto_principal else None

                if limpar_foto_principal or (foto_principal_obj and isinstance(foto_principal_obj, InMemoryUploadedFile)):
                    imovel_atualizado.foto_principal = None 

                print("Salvando dados do imóvel (sem/com foto antiga)...")
                imovel_atualizado.save()
                print(f"Imóvel atualizado (passo 1) ID: {imovel_atualizado.id}")

                upload_principal_success = True

                if limpar_foto_principal:
                    print("Limpando foto principal (já feito no save anterior).")
                
                elif foto_principal_obj and isinstance(foto_principal_obj, InMemoryUploadedFile):
                    original_filename = foto_principal_obj.name
                    unique_filename = generate_unique_filename(original_filename)
                    b2_object_name = f"{settings.AWS_LOCATION}/fotos_imoveis/{unique_filename}"
                    
                    print(f"Iniciando upload manual para NOVA foto principal: {b2_object_name}")
                    upload_principal_success = upload_to_b2(foto_principal_obj, b2_object_name)

                    if upload_principal_success:
                        imovel_atualizado.foto_principal.name = f"fotos_imoveis/{unique_filename}"
                        print(f"Atualizando DB com caminho da NOVA foto principal: {imovel_atualizado.foto_principal.name}")
                        imovel_atualizado.save(update_fields=['foto_principal'])
                    else:
                        messages.error(request, f'Falha ao fazer upload da NOVA foto principal: {original_filename}')

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
            
            contexto = {'form': form, 'assinatura': assinatura_usuario, 'assinatura_ativa': assinatura_valida_para_postar}
            return render(request, 'contas/anunciar_imovel.html', contexto)

    else: # Se for GET
        form = ImovelForm(instance=imovel)
        print("Renderizando formulário (Editar) para GET.") 

    contexto = {
        'form': form,
        'assinatura': assinatura_usuario,
        'assinatura_ativa': assinatura_valida_para_postar
    }
    print("Renderizando template anunciar_imovel.html (Editar)...") 
    return render(request, 'contas/anunciar_imovel.html', contexto)


# --- View "Excluir Imóvel" (Original) ---
@login_required
def excluir_imovel(request, imovel_id):
    imovel = get_object_or_404(Imovel, id=imovel_id, proprietario=request.user)
    if request.method == 'POST':
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
        foto.delete()
        messages.success(request, 'Foto excluída com sucesso.')
    else:
        messages.error(request, 'Você não tem permissão para excluir esta foto.')
    return redirect('editar_imovel', imovel_id=imovel_id) 

# --- View "Perfil" (Original - Sem mudanças) ---
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
            user_form = UserUpdateForm(request.POST, instance=request.user)
            password_form = CustomPasswordChangeForm(request.user, request.POST)
    
    else:
        user_form = UserUpdateForm(instance=request.user)
        password_form = CustomPasswordChangeForm(request.user)

    contexto = {
        'user_form': user_form,
        'password_form': password_form
    }
    return render(request, 'contas/perfil.html', contexto)

# --- VIEW: LISTAR PLANOS (ATUALIZADA) ---
def listar_planos(request):
    # Agora filtra apenas por planos que estão 'is_ativo'=True
    planos = Plano.objects.filter(is_ativo=True).order_by('preco')
    
    contexto = {
        'planos': planos
    }
    return render(request, 'contas/listar_planos.html', contexto)


# --- VIEW: PAGAMENTO MERCADO PAGO (ATUALIZADA) ---
@login_required
def criar_pagamento(request, plano_id):
    print(f"--- Iniciando criar_pagamento para Plano ID: {plano_id} ---")

    try:
        # Filtra também por 'is_ativo' para ninguém contratar plano desativado
        plano = get_object_or_404(Plano, id=plano_id, is_ativo=True) 
        print(f"Plano encontrado: {plano.nome}, Preço: {plano.preco}")
    except Exception:
        messages.error(request, "Plano não encontrado ou indisponível.")
        return redirect('/') 

    assinatura, criada = Assinatura.objects.get_or_create(
        usuario=request.user,
        defaults={'plano': plano, 'status': 'PENDENTE'}
    )
    
    if not criada:
        assinatura.plano = plano
        assinatura.status = 'PENDENTE'
        assinatura.data_inicio = None
        assinatura.data_expiracao = None
        assinatura.save()

    print(f"Assinatura (ID: {assinatura.id}) criada/atualizada para status PENDENTE.")
    
    # --- [INÍCIO] LÓGICA DO PLANO GRÁTIS ---
    if plano.preco == 0:
        print("Plano Grátis detectado. Ativando assinatura automaticamente.")
        
        assinatura.status = Assinatura.StatusAssinatura.ATIVA
        assinatura.data_inicio = timezone.now()
        assinatura.data_expiracao = timezone.now() + timedelta(days=plano.duracao_dias)
        assinatura.save(update_fields=['status', 'data_inicio', 'data_expiracao'])
        
        messages.success(request, f"Seu Plano Grátis ({plano.nome}) foi ativado! Você já pode anunciar.")
        
        return redirect('meus_imoveis') 
    # --- [FIM] LÓGICA DO PLANO GRÁTIS ---

    try:
        sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
    except Exception as e:
        print(f"!!! ERRO ao iniciar SDK Mercado Pago: {e}")
        messages.error(request, "Erro ao conectar ao sistema de pagamento.")
        return redirect('/')

    referencia_externa = f"assinatura_{assinatura.id}_usuario_{request.user.id}"
    print(f"Gerando preferência com external_reference: {referencia_externa}")

    base_url = "https://www.seudominio.com" 

    preference_data = {
        "items": [
            {
                "title": f"{plano.nome} - {request.user.email}",
                "quantity": 1,
                "unit_price": float(plano.preco),
            }
        ],
        "external_reference": referencia_externa,
        
        "back_urls": {
            "success": f"{base_url}/pagamento/sucesso/",
            "failure": f"{base_url}/pagamento/falha/",
            "pending": f"{base_url}/pagamento/pendente/"
        },
        "auto_return": "approved",
    }

    try:
        preference_response = sdk.preference().create(preference_data)
        
        if settings.DEBUG:
             checkout_url = preference_response["response"]["sandbox_init_point"]
             print("Modo DEBUG: Usando sandbox_init_point (TESTE)")
        else:
             checkout_url = preference_response["response"]["init_point"]
             print("Modo PRODUÇÃO: Usando init_point (REAL)")
        
        print(f"URL de Checkout: {checkout_url}")
        
        return redirect(checkout_url)

    except Exception as e:
        print(f"!!! ERRO ao criar preferência no Mercado Pago: {e} !!!")
        traceback.print_exc()
        messages.error(request, f"Erro ao gerar link de pagamento: {e}")
        return redirect('/')