# imoveis/models.py
from django.db import models
from django.contrib.auth.models import User

# Importações necessárias para processar imagem em memória
from PIL import Image, ImageDraw, ImageFont
import os
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings


# --- Função de Marca d'Água (integrada aqui para simplificar) ---
def apply_watermark_to_image(in_memory_file):
    """
    Aplica marca d'água a um arquivo de imagem em memória (InMemoryUploadedFile).
    Retorna um novo InMemoryUploadedFile com a marca d'água.
    """
    try:
        img = Image.open(in_memory_file).convert("RGBA")
        txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))

        watermark_text = "DOCELARMS" # Seu texto
        font_path = os.path.join(settings.BASE_DIR, 'assets', 'fonts', 'Roboto-Regular.ttf')
        font_size = int(img.size[0] * 0.05)

        if not os.path.exists(font_path):
             print(f"ERRO: Arquivo de fonte não encontrado em {font_path}")
             in_memory_file.seek(0)
             return in_memory_file

        font = ImageFont.truetype(font_path, font_size)
        draw = ImageDraw.Draw(txt_layer)

        text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x = (img.width - text_width) / 2
        y = (img.height - text_height) / 2

        draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 128))

        watermarked_img = Image.alpha_composite(img, txt_layer).convert("RGB")

        buffer = BytesIO()
        watermarked_img.save(buffer, format='JPEG', quality=85)
        buffer.seek(0)

        new_image = InMemoryUploadedFile(
            buffer, 'ImageField', f"{os.path.splitext(in_memory_file.name)[0]}_wm.jpg",
            'image/jpeg', buffer.getbuffer().nbytes, None
        )
        return new_image

    except Exception as e:
        print(f"Erro detalhado ao aplicar marca d'água: {e}")
        in_memory_file.seek(0)
        return in_memory_file
# ------------------------------------------------------------------------

class Cidade(models.Model):
    nome = models.CharField(max_length=100)
    estado = models.CharField(max_length=2, help_text="Sigla do estado, ex: MS")

    def __str__(self):
        return f"{self.nome}, {self.estado}"

    class Meta:
        ordering = ['nome']
        verbose_name_plural = "Cidades"

class Bairro(models.Model):
    cidade = models.ForeignKey(Cidade, on_delete=models.CASCADE, related_name="bairros")
    nome = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.nome} ({self.cidade.nome})"

    class Meta:
        ordering = ['nome']
        unique_together = ('cidade', 'nome')

class Imobiliaria(models.Model):
    nome = models.CharField(max_length=150)
    endereco = models.CharField(max_length=255, null=True, blank=True, verbose_name="Endereço")
    cidade = models.ForeignKey(Cidade, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Cidade")
    telefone = models.CharField(max_length=20, null=True, blank=True, verbose_name="Telefone Principal")
    telefone_secundario = models.CharField(max_length=20, null=True, blank=True, verbose_name="Telefone Secundário (ex: WhatsApp)")
    site = models.URLField(max_length=200, null=True, blank=True, verbose_name="Site")
    rede_social = models.URLField(max_length=200, null=True, blank=True, verbose_name="Rede Social")

    def __str__(self):
        return self.nome

    class Meta:
        ordering = ['nome']
        verbose_name_plural = "Imobiliárias"

class Imovel(models.Model):
    class Finalidade(models.TextChoices):
        VENDA = 'VENDA', 'Venda'
        ALUGUEL = 'ALUGUEL', 'Aluguel'

    finalidade = models.CharField(
        max_length=10, choices=Finalidade.choices, default=Finalidade.VENDA,
        verbose_name="Finalidade (Venda/Aluguel)"
    )
    destaque = models.BooleanField(default=False, verbose_name="Destaque?")
    aprovado = models.BooleanField(default=False, verbose_name="Aprovado?")

    proprietario = models.ForeignKey(User, on_delete=models.CASCADE)
    cidade = models.ForeignKey(Cidade, on_delete=models.SET_NULL, null=True, verbose_name="Cidade") # Continua obrigatório no form

    # --- CORREÇÃO APLICADA AQUI ---
    bairro = models.ForeignKey(Bairro, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Bairro")
    # -------------------------------

    imobiliaria = models.ForeignKey(Imobiliaria, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Imobiliária/Anunciante")

    titulo = models.CharField(max_length=100, verbose_name="Título do Anúncio")
    descricao = models.TextField(verbose_name="Descrição Completa")
    endereco = models.CharField(max_length=255, help_text="Apenas Rua e Número", verbose_name="Endereço (Rua, Número)")
    preco = models.DecimalField(max_digits=12, decimal_places=2, help_text="Preço (R$) ou Aluguel Mensal", verbose_name="Preço (R$)")
    telefone_contato = models.CharField(max_length=20, null=True, blank=True, verbose_name="Telefone para Contato Direto")

    quartos = models.PositiveIntegerField(verbose_name="Nº de Quartos")
    suites = models.PositiveIntegerField(default=0, verbose_name="Nº de Suítes")
    banheiros = models.PositiveIntegerField(verbose_name="Nº de Banheiros")
    salas = models.PositiveIntegerField(default=0, verbose_name="Nº de Salas")
    cozinhas = models.PositiveIntegerField(default=0, verbose_name="Nº de Cozinhas")
    closets = models.PositiveIntegerField(default=0, verbose_name="Nº de Closets")
    area = models.PositiveIntegerField(help_text="Em metros quadrados (m²)", verbose_name="Área (m²)")
    foto_principal = models.ImageField(upload_to='fotos_imoveis/', null=True, blank=True, verbose_name="Foto Principal")
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        process_watermark = False
        if self.foto_principal and hasattr(self.foto_principal.file, 'content_type'):
             if self.pk:
                 try:
                     old_instance = Imovel.objects.get(pk=self.pk)
                     if old_instance.foto_principal != self.foto_principal:
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
        if self.imagem and hasattr(self.imagem.file, 'content_type'):
             if not self.pk: process_watermark = True

        if process_watermark:
             print("Processando marca d'água para Foto da Galeria...")
             self.imagem = apply_watermark_to_image(self.imagem.file)

        super().save(*args, **kwargs)