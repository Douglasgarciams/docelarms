# imoveis/utils.py
from PIL import Image, ImageDraw, ImageFont
import os
from django.conf import settings

def add_watermark(image_path):
    """
    Aplica uma marca d'água de texto no centro de uma imagem.
    """
    try:
        # Abre a imagem original
        img = Image.open(image_path).convert("RGBA")
        
        # Cria uma camada transparente para desenhar o texto
        txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
        
        # Define o texto e a fonte
        watermark_text = "Fotoexclusivadedocelarms.com.br" # <<< MODIFIQUE SEU TEXTO AQUI
        font_path = os.path.join(settings.BASE_DIR, 'assets', 'fonts', 'Roboto-Regular.ttf')
        font_size = int(img.size[0] * 0.05) # Tamanho da fonte como 5% da largura da imagem
        font = ImageFont.truetype(font_path, font_size)
        
        # Prepara para desenhar na camada transparente
        draw = ImageDraw.Draw(txt_layer)
        
        # Calcula a posição do texto para centralizá-lo
        text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x = (img.width - text_width) / 2
        y = (img.height - text_height) / 2
        
        # Desenha o texto com transparência (RGBA)
        # O último valor (128) é a opacidade (0=transparente, 255=opaco)
        draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 128))
        
        # Combina a imagem original com a camada de texto
        watermarked_img = Image.alpha_composite(img, txt_layer)
        
        # Salva a imagem final em RGB (formato mais comum para web)
        watermarked_img.convert("RGB").save(image_path)
        
    except Exception as e:
        print(f"Erro ao aplicar marca d'água: {e}")