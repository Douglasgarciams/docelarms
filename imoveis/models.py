# imoveis/models.py
from django.db import models
from django.contrib.auth.models import User
from .utils import add_watermark

class Cidade(models.Model):
    nome = models.CharField(max_length=100)
    estado = models.CharField(max_length=2, help_text="Sigla do estado, ex: MS")

    def __str__(self):
        return f"{self.nome}, {self.estado}"

    class Meta:
        ordering = ['nome']
        verbose_name_plural = "Cidades" # Corrige o plural no admin

# --- NOVO MODELO DE BAIRRO ---
class Bairro(models.Model):
    cidade = models.ForeignKey(Cidade, on_delete=models.CASCADE, related_name="bairros")
    nome = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.nome} ({self.cidade.nome})"

    class Meta:
        ordering = ['nome']
        unique_together = ('cidade', 'nome') # Evita bairros duplicados na mesma cidade

class Imobiliaria(models.Model):
    # ... (seu modelo Imobiliaria continua aqui, sem alterações) ...
    nome = models.CharField(max_length=150)
    endereco = models.CharField(max_length=255, null=True, blank=True)
    cidade = models.ForeignKey(Cidade, on_delete=models.SET_NULL, null=True, blank=True)
    telefone = models.CharField(max_length=20, null=True, blank=True, verbose_name="Telefone Principal")
    telefone_secundario = models.CharField(max_length=20, null=True, blank=True, verbose_name="Telefone Secundário (ex: WhatsApp)")
    site = models.URLField(max_length=200, null=True, blank=True)
    rede_social = models.URLField(max_length=200, null=True, blank=True)
    def __str__(self): return self.nome
    class Meta: ordering = ['nome']

class Imovel(models.Model):
    class Finalidade(models.TextChoices):
        VENDA = 'VENDA', 'Venda'
        ALUGUEL = 'ALUGUEL', 'Aluguel'

    # --- CAMPOS COM verbose_name E help_text CORRIGIDOS ---
    finalidade = models.CharField(
        max_length=10,
        choices=Finalidade.choices,
        default=Finalidade.VENDA,
        verbose_name="Finalidade (Venda/Aluguel)"
    )
    destaque = models.BooleanField(default=False, verbose_name="Destaque?")
    aprovado = models.BooleanField(default=False, verbose_name="Aprovado?")
    
    proprietario = models.ForeignKey(User, on_delete=models.CASCADE) # Geralmente não editado pelo usuário no form
    cidade = models.ForeignKey(Cidade, on_delete=models.SET_NULL, null=True, verbose_name="Cidade")
    bairro = models.ForeignKey(Bairro, on_delete=models.SET_NULL, null=True, verbose_name="Bairro")
    imobiliaria = models.ForeignKey(Imobiliaria, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Imobiliária/Anunciante")
    
    titulo = models.CharField(max_length=100, verbose_name="Título do Anúncio")
    descricao = models.TextField(verbose_name="Descrição Completa")
    endereco = models.CharField(max_length=255, help_text="Apenas Rua e Número", verbose_name="Endereço (Rua, Número)")
    preco = models.DecimalField(max_digits=12, decimal_places=2, help_text="Preço (R$) ou Aluguel Mensal", verbose_name="Preço (R$)-(somente nº)")
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
    # --- FIM DAS CORREÇÕES ---

    def __str__(self):
        return self.titulo
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.foto_principal:
            add_watermark(self.foto_principal.path)

class Foto(models.Model):
    # ... (seu modelo Foto continua aqui, sem alterações) ...
    imovel = models.ForeignKey(Imovel, related_name='fotos', on_delete=models.CASCADE)
    imagem = models.ImageField(upload_to='fotos_galeria/')
    def __str__(self): return f"Foto de {self.imovel.titulo}"
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.imagem: add_watermark(self.imagem.path)