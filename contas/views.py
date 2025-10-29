# contas/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, UserUpdateForm, CustomPasswordChangeForm
from imoveis.models import Imovel, Foto 
from imoveis.forms import ImovelForm
from django.contrib.auth import update_session_auth_hash
import traceback 
import os 
import boto3 
from django.conf import settings 
from django.core.files.uploadedfile import InMemoryUploadedFile 
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import uuid
from pathlib import Path
import math

# Função generate_unique_filename (mantida)
def generate_unique_filename(filename):
    ext = Path(filename).suffix
    new_filename = f"{uuid.uuid4()}{ext}"
    return new_filename

# Função upload_to_b2 (mantida, só será chamada em produção)
def upload_to_b2(file_obj, object_name):
    """Faz upload de um objeto de arquivo para B2 usando Boto3, aplicando marca d'ГЎgua repetida."""
    print(f"--- Iniciando upload_to_b2 para: {object_name} ---")
    
    # --- ETAPA 1: Aplicar Marca D'ГЎgua ---
    try:
        print(f"Abrindo imagem para marca d'água...")
        img = Image.open(file_obj).convert("RGBA") # Abre a imagem garantindo canal Alpha
        img_width, img_height = img.size
        
        # Cria uma camada transparente para o texto, do mesmo tamanho da imagem original
        watermark_layer = Image.new('RGBA', img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(watermark_layer)
        
        text = "uso exclusivo de Docelarms"
        
        # Define a cor e opacidade (PRETO com 50% de alfa)
        text_color = (0, 0, 0, 128) # RGBA -> Preto, A=128 é ~50% de 255
        
        # --- Seleção da Fonte ---
        # Ajuste o divisor para controlar o tamanho do texto repetido
        # Um valor menor aqui = texto maior, um valor maior = texto menor
        font_size = int(min(img_width, img_height) / 25) # Ex: Fonte menor para caber mais repetições
        if font_size < 10: font_size = 10 # Tamanho mínimo
        
        font = None
        font_path = None 
        try:
             # Se você adicionar um arquivo de fonte:
             # font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'arial.ttf') # Exemplo
             if font_path and os.path.exists(font_path):
                 font = ImageFont.truetype(font_path, font_size)
                 print(f"Usando fonte: {font_path}")
             else:
                 print("Fonte específica não encontrada, tentando fonte padrão...")
                 font = ImageFont.truetype("arial.ttf", font_size) 
        except IOError:
             print("Não foi possível carregar a fonte 'arial.ttf', usando fonte padrão do Pillow.")
             try:
                 # Fonte padrão pode não aceitar tamanho, testar
                 font = ImageFont.load_default() 
             except Exception as font_e:
                 print(f"Erro ao carregar fonte: {font_e}. Marca d'água pode falhar.")

        if font:
            # Calcula o tamanho aproximado do texto (pode variar com a fonte)
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]

            # Define o espaçamento entre as repetições (ajuste conforme necessário)
            x_spacing = text_width * 1.5 
            y_spacing = text_height * 4 # Espaçamento vertical maior

            # Loop para desenhar o texto em toda a imagem
            print(f"Desenhando marca d'água repetida...")
            y = 0
            row_count = 0
            while y < img_height + text_height: # Continua um pouco além da borda inferior
                # Alterna o início do X para criar um padrão diagonal/tijolo
                start_x = -int(x_spacing / 2) if row_count % 2 != 0 else 0 
                x = start_x
                while x < img_width + text_width: # Continua um pouco além da borda direita
                    # Desenha o texto na camada transparente
                    draw.text((x, y), text, font=font, fill=text_color)
                    x += x_spacing
                y += y_spacing
                row_count += 1
            
            # Combina a camada de marca d'água com a imagem original
            # Image.alpha_composite requer que ambas tenham canal alfa
            img = Image.alpha_composite(img, watermark_layer)
        
        # --- ETAPA 2: Salvar Imagem Modificada em Memória ---
        # (Esta parte continua igual à anterior)
        output_buffer = BytesIO()
        original_format = Image.open(file_obj).format 
        print(f"Salvando imagem com marca d'água no formato: {original_format}")        
        save_format = 'JPEG' if original_format and original_format.upper() != 'PNG' else 'PNG'        
        if save_format == 'JPEG':
             img = img.convert('RGB') 
             img.save(output_buffer, format=save_format, quality=85) 
        else: 
             img.save(output_buffer, format=save_format)              
        output_buffer.seek(0) 
        file_obj_to_upload = output_buffer 
        content_type_to_upload = f'image/{save_format.lower()}'         
        print("Imagem com marca d'água pronta para upload.")

    except Exception as img_e:
        print(f"!!! ERRO ao aplicar marca d'água !!!")
        print(f"Erro: {img_e}")
        traceback.print_exc()
        print("Prosseguindo com upload da imagem ORIGINAL.")
        file_obj.seek(0) 
        file_obj_to_upload = file_obj 
        content_type_to_upload = file_obj.content_type 

    # --- ETAPA 3: Upload para B2 (usando file_obj_to_upload) ---
    # (Esta parte continua igual à anterior)
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
        print(f"Executando put_object: Bucket={bucket_name}, Key={object_name}, ContentType={content_type_to_upload}")
        s3_client.put_object(
            Bucket=bucket_name,
            Key=object_name,
            Body=file_obj_to_upload, 
            ContentType=content_type_to_upload 
        )
        print(f"SUCESSO: Upload Boto3 concluído para {object_name}")
        return True 

    except Exception as e:
        print(f"!!! ERRO no upload_to_b2 para {object_name} !!!")
        print(f"Erro: {e}")
        traceback.print_exc()
        return False

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

# --- View "Anunciar Imóvel" (COM UPLOAD MANUAL BOTO3) ---
@login_required
def anunciar_imovel(request):
    print(f"--- Iniciando anunciar_imovel --- | DEBUG={settings.DEBUG}") # Log DEBUG status
    print(f"Método da Requisição: {request.method}")

    if request.method == 'POST':
        form = ImovelForm(request.POST, request.FILES)
        print(f"request.FILES: {request.FILES}") 

        if form.is_valid():
            print("Formulário (Anunciar) é VÁLIDO.")
            
            # --- LÓGICA CONDICIONAL ---
            if not settings.DEBUG: 
                # --- LÓGICA DE PRODUÇÃO (Render com B2 Manual) ---
                print("--- MODO PRODUÇÃO (B2 Manual) ---")
                foto_principal_obj = form.cleaned_data.get('foto_principal')
                fotos_galeria_list = request.FILES.getlist('fotos_galeria') 
                try:
                    imovel = form.save(commit=False)
                    imovel.proprietario = request.user
                    imovel.foto_principal = None # Limpa temporariamente
                    imovel.save() 
                    print(f"Imóvel salvo (sem foto) ID: {imovel.id}")

                    upload_principal_success = True
                    if foto_principal_obj and isinstance(foto_principal_obj, InMemoryUploadedFile):
                        original_filename = foto_principal_obj.name
                        unique_filename = generate_unique_filename(original_filename)
                        b2_object_name = f"{settings.AWS_LOCATION}/fotos_imoveis/{unique_filename}" 
                        print(f"Iniciando upload manual B2 para foto principal: {b2_object_name}")
                        upload_principal_success = upload_to_b2(foto_principal_obj, b2_object_name)
                        if upload_principal_success:
                            imovel.foto_principal.name = f"fotos_imoveis/{unique_filename}" 
                            imovel.save(update_fields=['foto_principal']) 
                        else:
                            messages.error(request, f'Falha ao fazer upload da foto principal: {original_filename}')
                    
                    if upload_principal_success and fotos_galeria_list:
                        print(f"Processando {len(fotos_galeria_list)} fotos da galeria B2...")
                        for file_obj in fotos_galeria_list:
                             if isinstance(file_obj, InMemoryUploadedFile):
                                original_filename = file_obj.name
                                unique_filename = generate_unique_filename(original_filename)
                                b2_object_name = f"{settings.AWS_LOCATION}/fotos_galeria/{unique_filename}"
                                print(f"Iniciando upload manual B2 para foto galeria: {b2_object_name}")
                                if upload_to_b2(file_obj, b2_object_name):
                                    Foto.objects.create(imovel=imovel, imagem=f"fotos_galeria/{unique_filename}")
                                else:
                                    messages.warning(request, f'Falha ao fazer upload da foto da galeria: {original_filename}')

                    if upload_principal_success:
                        messages.success(request, 'Seu imóvel foi enviado para análise!')
                        return redirect('meus_imoveis')

                except Exception as e: 
                    print(f"!!! ERRO CRÍTICO GERAL (anunciar_imovel - PRODUÇÃO) !!! | Erro: {e}")
                    traceback.print_exc() 
                    messages.error(request, f'Ocorreu um erro inesperado: {e}')
            
            else: 
                # --- LÓGICA DE DESENVOLVIMENTO LOCAL (FileSystemStorage) ---
                print("--- MODO DEBUG (FileSystemStorage) ---")
                try:
                    imovel = form.save(commit=False)
                    imovel.proprietario = request.user
                    # O form.save() AGORA vai lidar com o salvamento da foto localmente
                    print("Executando form.save() para salvar localmente...")
                    imovel.save() 
                    print(f"Imóvel salvo localmente ID: {imovel.id}")
                    if imovel.foto_principal:
                         print(f"Caminho foto principal local: {imovel.foto_principal.path}")
                         print(f"URL foto principal local: {imovel.foto_principal.url}")

                    # Salvar fotos da galeria localmente (usando o FileSystemStorage padrão)
                    fotos_galeria_list = request.FILES.getlist('fotos_galeria')
                    print(f"Processando {len(fotos_galeria_list)} fotos da galeria localmente...")
                    for file_obj in fotos_galeria_list:
                         if isinstance(file_obj, InMemoryUploadedFile):
                            try:
                                foto_obj = Foto(imovel=imovel, imagem=file_obj) 
                                foto_obj.save() # FileSystemStorage cuida disso
                                print(f"Salvo localmente foto galeria: {foto_obj.imagem.name}, URL: {foto_obj.imagem.url}")
                            except Exception as e_galeria:
                                print(f"!!! ERRO ao salvar foto da galeria localmente: {file_obj.name} !!! | Erro: {e_galeria}")
                    
                    messages.success(request, 'Seu imóvel foi salvo localmente!')
                    return redirect('meus_imoveis')

                except Exception as e:
                    print(f"!!! ERRO CRÍTICO GERAL (anunciar_imovel - LOCAL) !!! | Erro: {e}")
                    traceback.print_exc()
                    messages.error(request, f'Ocorreu um erro local inesperado: {e}')

        else: # Se form.is_valid() for False
            print("Formulário (Anunciar) NÃO é válido.")
            print(form.errors.as_text()) 
            messages.error(request, 'Por favor, corrija os erros no formulário.')

    else: # Se for GET
        form = ImovelForm()
        print("Renderizando formulário (Anunciar) para GET.") 
    
    print("Renderizando template anunciar_imovel.html (Anunciar)...") 
    return render(request, 'contas/anunciar_imovel.html', {'form': form})


# --- View "Editar Imóvel" (COM LÓGICA CONDICIONAL DEBUG/PRODUÇÃO) ---
@login_required
def editar_imovel(request, imovel_id):
    imovel = get_object_or_404(Imovel, id=imovel_id, proprietario=request.user)
    print(f"--- Iniciando editar_imovel para ID: {imovel_id} --- | DEBUG={settings.DEBUG}")
    print(f"Método da Requisição: {request.method}")

    if request.method == 'POST':
        form = ImovelForm(request.POST, request.FILES, instance=imovel)
        print(f"request.FILES: {request.FILES}") 
        
        if form.is_valid():
            print("Formulário (Editar) é VÁLIDO.")

            # --- LÓGICA CONDICIONAL ---
            if not settings.DEBUG:
                # --- LÓGICA DE PRODUÇÃO (Render com B2 Manual) ---
                print("--- MODO PRODUÇÃO (B2 Manual - Editar) ---")
                foto_principal_obj = form.cleaned_data.get('foto_principal') 
                fotos_galeria_list = request.FILES.getlist('fotos_galeria')
                limpar_foto_principal = foto_principal_obj is False 

                try:
                    imovel_atualizado = form.save(commit=False)
                    foto_antiga = imovel.foto_principal.name if imovel.foto_principal else None
                    
                    if limpar_foto_principal or (foto_principal_obj and isinstance(foto_principal_obj, InMemoryUploadedFile)):
                         imovel_atualizado.foto_principal = None 

                    imovel_atualizado.save() # Salva outros campos e talvez limpe a foto
                    print(f"Imóvel atualizado (passo 1) ID: {imovel_atualizado.id}")

                    upload_principal_success = True
                    if limpar_foto_principal:
                        print("Limpando foto principal B2 (lógica de delete futura aqui).")
                        # TODO: Adicionar delete_from_b2(foto_antiga)
                    
                    elif foto_principal_obj and isinstance(foto_principal_obj, InMemoryUploadedFile):
                        original_filename = foto_principal_obj.name
                        unique_filename = generate_unique_filename(original_filename)
                        b2_object_name = f"{settings.AWS_LOCATION}/fotos_imoveis/{unique_filename}"
                        print(f"Iniciando upload manual B2 para NOVA foto principal: {b2_object_name}")
                        upload_principal_success = upload_to_b2(foto_principal_obj, b2_object_name)
                        if upload_principal_success:
                            imovel_atualizado.foto_principal.name = f"fotos_imoveis/{unique_filename}"
                            imovel_atualizado.save(update_fields=['foto_principal'])
                            # TODO: Adicionar delete_from_b2(foto_antiga)
                        else:
                            messages.error(request, f'Falha ao fazer upload da NOVA foto principal: {original_filename}')
                    
                    if upload_principal_success and fotos_galeria_list:
                        print(f"Processando {len(fotos_galeria_list)} NOVAS fotos da galeria B2...")
                        for file_obj in fotos_galeria_list:
                             if isinstance(file_obj, InMemoryUploadedFile):
                                original_filename = file_obj.name
                                unique_filename = generate_unique_filename(original_filename)
                                b2_object_name = f"{settings.AWS_LOCATION}/fotos_galeria/{unique_filename}"
                                print(f"Iniciando upload manual B2 para NOVA foto galeria: {b2_object_name}")
                                if upload_to_b2(file_obj, b2_object_name):
                                    Foto.objects.create(imovel=imovel_atualizado, imagem=f"fotos_galeria/{unique_filename}")
                                else:
                                    messages.warning(request, f'Falha ao fazer upload da NOVA foto da galeria: {original_filename}')
                    
                    if upload_principal_success:
                        messages.success(request, 'Imóvel atualizado com sucesso!')
                        return redirect('meus_imoveis')

                except Exception as e: 
                    print(f"!!! ERRO CRÍTICO GERAL (editar_imovel - PRODUÇÃO) !!! | Erro: {e}")
                    traceback.print_exc() 
                    messages.error(request, f'Ocorreu um erro inesperado ao atualizar: {e}')

            else:
                # --- LÓGICA DE DESENVOLVIMENTO LOCAL (FileSystemStorage) ---
                print("--- MODO DEBUG (FileSystemStorage - Editar) ---")
                try:
                    # Com FileSystemStorage, form.save() cuida de tudo
                    print("Executando form.save() para atualizar localmente...")
                    imovel_atualizado = form.save() 
                    print(f"Imóvel atualizado localmente ID: {imovel_atualizado.id}")
                    if imovel_atualizado.foto_principal:
                         print(f"Caminho foto principal local: {imovel_atualizado.foto_principal.path}")
                         print(f"URL foto principal local: {imovel_atualizado.foto_principal.url}")

                    # Salvar NOVAS fotos da galeria localmente
                    fotos_galeria_list = request.FILES.getlist('fotos_galeria')
                    print(f"Processando {len(fotos_galeria_list)} NOVAS fotos da galeria localmente...")
                    for file_obj in fotos_galeria_list:
                         if isinstance(file_obj, InMemoryUploadedFile):
                            try:
                                foto_obj = Foto(imovel=imovel_atualizado, imagem=file_obj) 
                                foto_obj.save() # FileSystemStorage cuida disso
                                print(f"Salvo localmente NOVA foto galeria: {foto_obj.imagem.name}, URL: {foto_obj.imagem.url}")
                            except Exception as e_galeria:
                                print(f"!!! ERRO ao salvar NOVA foto da galeria localmente: {file_obj.name} !!! | Erro: {e_galeria}")

                    messages.success(request, 'Imóvel atualizado localmente!')
                    return redirect('meus_imoveis')

                except Exception as e:
                    print(f"!!! ERRO CRÍTICO GERAL (editar_imovel - LOCAL) !!! | Erro: {e}")
                    traceback.print_exc()
                    messages.error(request, f'Ocorreu um erro local inesperado ao atualizar: {e}')
        
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