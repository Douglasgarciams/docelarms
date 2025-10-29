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
from django.core.files.storage import default_storage
from django.conf import settings             # <-- 1. ADICIONE ESTE IMPORT
from django.conf.urls.static import static # <-- 2. ADICIONE ESTE IMPORT

# --- CORREÇÃO 1: Adicionar a função que estava faltando ---
def generate_unique_filename(filename):
    """Gera um nome de arquivo único mantendo a extensão."""
    ext = Path(filename).suffix
    new_filename = f"{uuid.uuid4()}{ext}"
    return new_filename

# --- CORREÇÃO 2: Corrigir a função upload_to_b2 ---
# Função auxiliar para fazer o upload (USANDO DJANGO STORAGE PADRÃO E FONTE PADRÃO)
def upload_to_b2(file_obj, object_name):
    """Faz upload de um objeto de arquivo usando o storage padrão do Django, 
       aplicando marca d'água grande com fonte padrão."""
    print(f"--- Iniciando upload_to_b2 para: {object_name} ---")
    
    file_obj_to_upload = None 
    # --- Definir variáveis de fallback PRIMEIRO ---
    file_obj.seek(0) 
    file_obj_to_upload = file_obj
    content_type_to_upload = file_obj.content_type 
    watermark_applied = False 

    # --- ETAPA 1: Tentar Aplicar Marca D'água ---
    try:
        print(f"Abrindo imagem para marca d'água...")
        img = Image.open(file_obj).convert("RGBA") 
        img_width, img_height = img.size
        
        watermark_layer = Image.new('RGBA', img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(watermark_layer) # Criar o objeto Draw aqui
        
        text = "uso exclusivo de Docelarms"
        text_color = (0, 0, 0, 128) # Preto, ~50% alfa
        
        # --- Carregar Fonte Padrão ---
        try:
            print("Carregando fonte padrão do Pillow...")
            font = ImageFont.load_default() 
        except Exception as font_e:
            print(f"Erro CRÍTICO ao carregar fonte padrão: {font_e}. Pulando marca d'água.")
            raise # Re-levanta a exceção para pular para o bloco 'except img_e'

        # --- Desenhar Texto Pequeno Temporário ---
        if font:
            # CORREÇÃO: Usar draw.textbbox() para medir o texto com a fonte padrão
            try:
                # Usa textbbox para obter a caixa delimitadora (esquerda, topo, direita, baixo)
                text_bbox_orig = draw.textbbox((0, 0), text, font=font)
                text_width_orig = text_bbox_orig[2] - text_bbox_orig[0]
                text_height_orig = text_bbox_orig[3] - text_bbox_orig[1]
                print(f"Dimensões originais do texto padrão: {text_width_orig}x{text_height_orig}")
            except AttributeError:
                 # Fallback (caso textbbox não esteja disponível, o que é raro)
                 print("draw.textbbox não disponível? Usando textlength.")
                 text_width_orig = draw.textlength(text, font=font)
                 text_height_orig = 10 # Estima altura
                 print(f"Dimensões estimadas do texto padrão: {text_width_orig}x{text_height_orig}")


            if text_width_orig <= 0 or text_height_orig <= 0:
                  print("Fonte padrão retornou tamanho inválido. Pulando marca d'água.")
                  raise ValueError("Tamanho de fonte padrão inválido")

            # Cria imagem temporária só pro texto original
            text_img_orig = Image.new('RGBA', (text_width_orig, text_height_orig), (0,0,0,0))
            text_draw_orig = ImageDraw.Draw(text_img_orig)
            text_draw_orig.text((0, 0), text, font=font, fill=text_color) 

            # --- Redimensionar a Imagem do Texto ---
            target_font_width_ratio = 0.75 
            target_text_width = int(img_width * target_font_width_ratio)
            aspect_ratio = text_height_orig / text_width_orig
            target_text_height = int(target_text_width * aspect_ratio)

            if target_text_width > 0 and target_text_height > 0:
                print(f"Redimensionando texto de ({text_width_orig}x{text_height_orig}) para ({target_text_width}x{target_text_height})")
                text_img_resized = text_img_orig.resize((target_text_width, target_text_height), Image.Resampling.LANCZOS)
    
                # --- Rotação (Opcional) ---
                angle = 20 # Mantenha 0 se não quiser rotação
                if angle != 0:
                    print(f"Rotacionando texto em {angle} graus...")
                    pad_w = int(target_text_width * 0.1)
                    pad_h = int(target_text_height * 0.1)
                    padded_resized_img = Image.new('RGBA', (target_text_width + 2*pad_w, target_text_height + 2*pad_h), (0,0,0,0))
                    padded_resized_img.paste(text_img_resized, (pad_w, pad_h))
                    final_text_img = padded_resized_img.rotate(angle, expand=1, resample=Image.BICUBIC)
                else:
                    final_text_img = text_img_resized # Sem rotação
                
                final_text_width, final_text_height = final_text_img.size
                x = (img_width - final_text_width) / 2
                y = (img_height - final_text_height) / 2
                
                print(f"Colando marca d'água final em ({x},{y})")
                watermark_layer.paste(final_text_img, (int(x), int(y)), final_text_img) 
                
                img = Image.alpha_composite(img, watermark_layer)
                watermark_applied = True
            else:
                print("Dimensões calculadas inválidas. Pulando marca d'água.")
        else:
              print("Não foi possível carregar fonte padrão. Pulando marca d'água.")

        # --- ETAPA 2: Salvar Imagem Modificada em Memória (SE APLICADA) ---
        if watermark_applied:
            output_buffer = BytesIO()
            original_format = Image.open(file_obj).format 
            print(f"Salvando imagem COM marca d'água no formato: {original_format}")        
            save_format = 'JPEG' if original_format and original_format.upper() != 'PNG' else 'PNG'        
            if save_format == 'JPEG':
                 img = img.convert('RGB') 
                 img.save(output_buffer, format=save_format, quality=85) 
            else: 
                 img.save(output_buffer, format=save_format)              
            output_buffer.seek(0) 
            file_obj_to_upload = output_buffer 
            content_type_to_upload = f'image/{save_format.lower()}'          
            print("Imagem com marca d'água pronta para salvar.")
        # Se watermark_applied for False, as variáveis de fallback (imagem original) são usadas

    except Exception as img_e:
        print(f"!!! ERRO GERAL ao aplicar marca d'água !!!") 
        print(f"Erro: {img_e}")
        traceback.print_exc()
        print("Prosseguindo com salvamento da imagem ORIGINAL.")
        file_obj.seek(0) 
        file_obj_to_upload = file_obj 
        content_type_to_upload = file_obj.content_type 

    # --- ETAPA 3: Upload/Save usando o Storage Padrão ---
    try:
        if file_obj_to_upload is None: 
              print("!!! ERRO: file_obj_to_upload não definido. Pulando save. !!!")
              return False

        print(f"Executando default_storage.save(): Name={object_name}")
        actual_name = default_storage.save(object_name, file_obj_to_upload) 
        print(f"SUCESSO: default_storage.save() concluído. Nome real salvo: {actual_name}")
        return actual_name 

    except Exception as e:
        print(f"!!! ERRO no default_storage.save() para {object_name} !!!")
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
                    final_foto_principal_name = None # Guarda o nome final
                    if foto_principal_obj and isinstance(foto_principal_obj, InMemoryUploadedFile):
                        original_filename = foto_principal_obj.name
                        unique_filename = generate_unique_filename(original_filename)
                        # Caminho completo é necessário para default_storage.save()
                        b2_object_name = f"{settings.AWS_LOCATION}/fotos_imoveis/{unique_filename}" 
                        print(f"Iniciando upload manual B2 para foto principal: {b2_object_name}")
                        
                        saved_name = upload_to_b2(foto_principal_obj, b2_object_name) 
                        
                        if saved_name:
                            # Salva SOMENTE o nome relativo no banco
                            final_foto_principal_name = saved_name.replace(f"{settings.AWS_LOCATION}/", "", 1) 
                            imovel.foto_principal.name = final_foto_principal_name
                            imovel.save(update_fields=['foto_principal']) 
                            print(f"DB Atualizado com foto principal: {final_foto_principal_name}")
                            upload_principal_success = True
                        else:
                            messages.error(request, f'Falha ao fazer upload da foto principal: {original_filename}')
                            upload_principal_success = False
                    
                    if upload_principal_success and fotos_galeria_list:
                        print(f"Processando {len(fotos_galeria_list)} fotos da galeria B2...")
                        for file_obj in fotos_galeria_list:
                             if isinstance(file_obj, InMemoryUploadedFile):
                                original_filename = file_obj.name
                                unique_filename = generate_unique_filename(original_filename)
                                b2_object_name = f"{settings.AWS_LOCATION}/fotos_galeria/{unique_filename}"
                                print(f"Iniciando upload manual B2 para foto galeria: {b2_object_name}")
                                
                                saved_name = upload_to_b2(file_obj, b2_object_name)
                                
                                if saved_name:
                                    final_galeria_name = saved_name.replace(f"{settings.AWS_LOCATION}/", "", 1)
                                    Foto.objects.create(imovel=imovel, imagem=final_galeria_name)
                                    print(f"DB Salvo foto galeria: {final_galeria_name}")
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
                    print("Executando form.save() para salvar localmente...")
                    imovel.save() # FileSystemStorage (local) cuida de tudo
                    print(f"Imóvel salvo localmente ID: {imovel.id}")
                    if imovel.foto_principal:
                         print(f"URL foto principal local: {imovel.foto_principal.url}")

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
                    final_foto_principal_name = None # Guarda o nome final
                    if limpar_foto_principal:
                        print("Limpando foto principal B2 (lógica de delete futura aqui).")
                        # TODO: Adicionar delete_from_b2(foto_antiga)
                    
                    elif foto_principal_obj and isinstance(foto_principal_obj, InMemoryUploadedFile):
                        original_filename = foto_principal_obj.name
                        unique_filename = generate_unique_filename(original_filename)
                        b2_object_name = f"{settings.AWS_LOCATION}/fotos_imoveis/{unique_filename}"
                        print(f"Iniciando upload manual B2 para NOVA foto principal: {b2_object_name}")
                        
                        saved_name = upload_to_b2(foto_principal_obj, b2_object_name)
                        
                        if saved_name:
                            final_foto_principal_name = saved_name.replace(f"{settings.AWS_LOCATION}/", "", 1)
                            imovel_atualizado.foto_principal.name = final_foto_principal_name
                            imovel_atualizado.save(update_fields=['foto_principal'])
                            print(f"DB Atualizado com NOVA foto principal: {final_foto_principal_name}")
                            upload_principal_success = True
                            # TODO: Adicionar delete_from_b2(foto_antiga)
                        else:
                            messages.error(request, f'Falha ao fazer upload da NOVA foto principal: {original_filename}')
                            upload_principal_success = False
                    
                    if upload_principal_success and fotos_galeria_list:
                        print(f"Processando {len(fotos_galeria_list)} NOVAS fotos da galeria B2...")
                        for file_obj in fotos_galeria_list:
                             if isinstance(file_obj, InMemoryUploadedFile):
                                original_filename = file_obj.name
                                unique_filename = generate_unique_filename(original_filename)
                                b2_object_name = f"{settings.AWS_LOCATION}/fotos_galeria/{unique_filename}"
                                print(f"Iniciando upload manual B2 para NOVA foto galeria: {b2_object_name}")
                                
                                saved_name = upload_to_b2(file_obj, b2_object_name)

                                if saved_name:
                                    final_galeria_name = saved_name.replace(f"{settings.AWS_LOCATION}/", "", 1)
                                    Foto.objects.create(imovel=imovel_atualizado, imagem=final_galeria_name)
                                    print(f"DB Salvo NOVA foto galeria: {final_galeria_name}")
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
                    print("Executando form.save() para atualizar localmente...")
                    imovel_atualizado = form.save() 
                    print(f"Imóvel atualizado localmente ID: {imovel_atualizado.id}")
                    if imovel_atualizado.foto_principal:
                         print(f"URL foto principal local: {imovel_atualizado.foto_principal.url}")

                    fotos_galeria_list = request.FILES.getlist('fotos_galeria')
                    print(f"Processando {len(fotos_galeria_list)} NOVAS fotos da galeria localmente...")
                    for file_obj in fotos_galeria_list:
                         if isinstance(file_obj, InMemoryUploadedFile):
                            try:
                                foto_obj = Foto(imovel=imovel_atualizado, imagem=file_obj) 
                                foto_obj.save() 
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