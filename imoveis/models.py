# imoveis/models.py
from django.db import models
from django.contrib.auth.models import User
# Importações da marca d'água REMOVIDAS

class Cidade(models.Model):
    nome = models.CharField(max_length=100)
    estado = models.CharField(max_length=2, help_text="Sigla do estado, ex: MS")
    def __str__(self): return f"{self.nome}, {self.estado}"
    class Meta: ordering = ['nome']; verbose_name_plural = "Cidades"

class Bairro(models.Model):
    cidade = models.ForeignKey(Cidade, on_delete=models.CASCADE, related_name="bairros")
    nome = models.CharField(max_length=150)
    def __str__(self): return f"{self.nome} ({self.cidade.nome})"
    class Meta: ordering = ['nome']; unique_together = ('cidade', 'nome')

class Imobiliaria(models.Model):
    nome = models.CharField(max_length=150)
    endereco = models.CharField(max_length=255, null=True, blank=True, verbose_name="Endereço")
    cidade = models.ForeignKey(Cidade, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Cidade")
    telefone = models.CharField(max_length=20, null=True, blank=True, verbose_name="Telefone Principal")
    telefone_secundario = models.CharField(max_length=20, null=True, blank=True, verbose_name="Telefone Secundário (ex: WhatsApp)")
    site = models.URLField(max_length=200, null=True, blank=True, verbose_name="Site")
    rede_social = models.URLField(max_length=200, null=True, blank=True, verbose_name="Rede Social")
    def __str__(self): return self.nome
    class Meta: ordering = ['nome']; verbose_name_plural = "Imobiliárias"

class Imovel(models.Model):
    class Finalidade(models.TextChoices):
        VENDA = 'VENDA', 'Venda'
        ALUGUEL = 'ALUGUEL', 'Aluguel'

    # --- TODOS OS CAMPOS AGORA SÃO OPCIONAIS (null=True, blank=True) ---
    
    finalidade = models.CharField(
        max_length=10, choices=Finalidade.choices, default=Finalidade.VENDA,
        verbose_name="Finalidade (Venda/Aluguel)", null=True, blank=True
    )
    destaque = models.BooleanField(default=False, verbose_name="Destaque?")
    aprovado = models.BooleanField(default=False, verbose_name="Aprovado?")
    
    proprietario = models.ForeignKey(User, on_delete=models.CASCADE) # Este é o único obrigatório (definido na view)
    cidade = models.ForeignKey(Cidade, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Cidade")
    bairro = models.ForeignKey(Bairro, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Bairro")
    imobiliaria = models.ForeignKey(Imobiliaria, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Imobiliária/Anunciante")
    
    titulo = models.CharField(max_length=100, verbose_name="Título do Anúncio", null=True, blank=True)
    descricao = models.TextField(verbose_name="Descrição Completa", null=True, blank=True)
    endereco = models.CharField(max_length=255, help_text="Apenas Rua e Número", verbose_name="Endereço (Rua, Número)", null=True, blank=True)
    preco = models.DecimalField(max_digits=12, decimal_places=2, help_text="Preço (R$) ou Aluguel Mensal", verbose_name="Preço (R$)", null=True, blank=True)
    telefone_contato = models.CharField(max_length=20, null=True, blank=True, verbose_name="Telefone para Contato Direto")
    
    quartos = models.PositiveIntegerField(verbose_name="Nº de Quartos", null=True, blank=True, default=0)
    suites = models.PositiveIntegerField(default=0, verbose_name="Nº de Suítes", null=True, blank=True)
    banheiros = models.PositiveIntegerField(verbose_name="Nº de Banheiros", null=True, blank=True, default=0)
    salas = models.PositiveIntegerField(default=0, verbose_name="Nº de Salas", null=True, blank=True)
    cozinhas = models.PositiveIntegerField(default=0, verbose_name="Nº de Cozinhas", null=True, blank=True)
    closets = models.PositiveIntegerField(default=0, verbose_name="Nº de Closets", null=True, blank=True)
    area = models.PositiveIntegerField(help_text="Em metros quadrados (m²)", verbose_name="Área (m²)", null=True, blank=True, default=0)
    foto_principal = models.ImageField(upload_to='fotos_imoveis/', null=True, blank=True, verbose_name="Foto Principal")
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.titulo:
            return self.titulo
        return f"Imóvel ID {self.id}" # Fallback se o título estiver vazio
    
    # MÉTODO SAVE CUSTOMIZADO REMOVIDO

class Foto(models.Model):
    imovel = models.ForeignKey(Imovel, related_name='fotos', on_delete=models.CASCADE)
    imagem = models.ImageField(upload_to='fotos_galeria/')
    def __str__(self): return f"Foto de {self.imovel.titulo or self.imovel.id}"
    # MÉTODO SAVE CUSTOMIZADO REMOVIDO