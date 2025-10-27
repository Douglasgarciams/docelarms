# imoveis/models.py
from django.db import models
from django.contrib.auth.models import User

# Importações necessárias para processar imagem em memória
from PIL import Image, ImageDraw, ImageFont
import os
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings
import traceback # Para log de erro detalhado

# --- Função de Marca d'Água (integrada e corrigida) ---
def apply_watermark_to_image(in_memory_file):
    print(f"--- Iniciando apply_watermark_to_image para: {getattr(in_memory_file, 'name', 'Nome não disponível')}")
    try:
        img = Image.open(in_memory_file).convert("RGBA")
        txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))

        watermark_text = "DOCELARMS" # Seu texto
        font_path = os.path.join(settings.BASE_DIR, 'assets', 'fonts', 'Roboto-Regular.ttf')
        font_size = int(img.size[0] * 0.05) # Ajuste este fator (0.05 = 5%) se necessário

        if not os.path.exists(font_path):
            print(f"ERRO CRÍTICO: Arquivo de fonte NÃO ENCONTRADO em {font_path}")
            in_memory_file.seek(0)
            return in_memory_file

        font = ImageFont.truetype(font_path, font_size)
        draw = ImageDraw.Draw(txt_layer)

        # --- CÁLCULO DE POSIÇÃO (GARANTIR QUE ESTÁ AQUI) ---
        text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x = (img.width - text_width) / 2
        y = (img.height - text_height) / 2
        # --------------------------------------------------

        # Desenha o texto usando x e y
        draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 128))
        print(f"--- Texto '{watermark_text}' desenhado na posição ({x:.0f}, {y:.0f})")

        watermarked_img = Image.alpha_composite(img, txt_layer).convert("RGB")
        print("--- Marca d'água aplicada à imagem em memória.")

        buffer = BytesIO()
        watermarked_img.save(buffer, format='JPEG', quality=85)
        buffer.seek(0)
        print(f"--- Imagem com marca d'água salva no buffer. Tamanho: {buffer.getbuffer().nbytes} bytes.")

        original_name = getattr(in_memory_file, 'name', 'unknown_file')
        name, ext = os.path.splitext(original_name)
        # Usar um nome de arquivo mais simples pode evitar problemas
        new_filename = f"{name}_wm.jpg" 

        new_image = InMemoryUploadedFile(
            buffer, 'ImageField', new_filename,
            'image/jpeg', buffer.getbuffer().nbytes, None
        )
        print(f"--- Retornando novo InMemoryUploadedFile: {new_filename}, Tipo: {new_image.content_type}, Tamanho: {new_image.size}")
        return new_image

    except Exception as e:
        print(f"--- ERRO DETALHADO em apply_watermark_to_image: {e}")
        traceback.print_exc()
        in_memory_file.seek(0)
        print("--- Retornando arquivo original devido a erro.")
        return in_memory_file
# ------------------------------------------------------------------------

class Cidade(models.Model):
    # ... (sem alterações) ...

class Bairro(models.Model):
    # ... (sem alterações) ...

class Imobiliaria(models.Model):
    # ... (sem alterações) ...

class Imovel(models.Model):
    # ... (campos sem alterações) ...
    foto_principal = models.ImageField(upload_to='fotos_imoveis/', null=True, blank=True, verbose_name="Foto Principal")
    # ...

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        process_watermark = False
        if self.foto_principal and hasattr(self.foto_principal.file, 'content_type'):
             if self.pk:
                 try:
                     old_instance = Imovel.objects.get(pk=self.pk)
                     # Só processa se o arquivo for realmente diferente
                     if hasattr(old_instance.foto_principal, 'file') and hasattr(self.foto_principal, 'file'):
                         if old_instance.foto_principal.file.name != self.foto_principal.file.name or old_instance.foto_principal.size != self.foto_principal.size:
                              process_watermark = True
                     elif self.foto_principal and not old_instance.foto_principal: # Adicionando foto onde não havia
                          process_watermark = True
                 except Imovel.DoesNotExist: process_watermark = True
             else: process_watermark = True

        if process_watermark:
             print("Processando marca d'água para Foto Principal...")
             self.foto_principal = apply_watermark_to_image(self.foto_principal.file)

        super().save(*args, **kwargs)

class Foto(models.Model):
    imovel = models.ForeignKey(Imovel, related_name='fotos', on_delete=models.CASCADE)
    imagem = models.ImageField(upload_to='fotos_galeria/')

    def __str__(self): return f"Foto de {self.imovel.titulo}"

    def save(self, *args, **kwargs):
        process_watermark = False
        # Simplificado: aplica marca d'água sempre que uma nova Foto for criada
        if self.imagem and hasattr(self.imagem.file, 'content_type') and not self.pk:
             process_watermark = True

        if process_watermark:
             print("Processando marca d'água para Foto da Galeria...")
             self.imagem = apply_watermark_to_image(self.imagem.file)

        super().save(*args, **kwargs)