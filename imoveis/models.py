# imoveis/models.py

from django.db import models
from django.conf import settings 
from django.utils import timezone

# -----------------------------------------------------------------
# MODELOS 'Cidade', 'Bairro' (Sem mudanças)
# -----------------------------------------------------------------
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

# -----------------------------------------------------------------
# MODELO 'Imobiliaria' (ATUALIZADO)
# -----------------------------------------------------------------
class Imobiliaria(models.Model):
    
    # --- [CAMPO DE VÍNCULO] ---
    # Liga o perfil da Imobiliária à conta do Usuário
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='imobiliaria_profile', 
        null=True, 
        blank=True
    )
    # ---------------------------

    nome = models.CharField(max_length=150)
    
    # --- [CAMPO REMOVIDO] ---
    # creci = ... (Removido conforme sua solicitação)
    # ---------------------------

    endereco = models.CharField(max_length=255, null=True, blank=True, verbose_name="Endereço")
    cidade = models.ForeignKey(Cidade, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Cidade")
    telefone = models.CharField(max_length=20, null=True, blank=True, verbose_name="Telefone Principal")
    telefone_secundario = models.CharField(max_length=20, null=True, blank=True, verbose_name="Telefone Secundário (ex: WhatsApp)")
    site = models.URLField(max_length=200, null=True, blank=True, verbose_name="Site")
    rede_social = models.URLField(max_length=200, null=True, blank=True, verbose_name="Rede Social")
    
    def __str__(self): return self.nome
    class Meta: ordering = ['nome']; verbose_name_plural = "Imobiliárias"

# -----------------------------------------------------------------
# MODELO: PLANO (Sem mudanças)
# -----------------------------------------------------------------
class Plano(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome do Plano")
    descricao = models.TextField(
        verbose_name="Descrição", 
        help_text="O que este plano oferece? (Ex: Destaque na home, mais fotos, etc.)",
        blank=True,
        null=True
    )
    preco = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço (R$)")
    duracao_dias = models.IntegerField(help_text="Duração do anúncio em dias (ex: 30, 180, 365)")
    limite_fotos = models.IntegerField(
        default=5,
        verbose_name="Limite de Fotos",
        help_text="Número máximo de fotos permitidas por anúncio (ex: 5, 15, 32)"
    )
    limite_anuncios = models.IntegerField(
        default=1,
        verbose_name="Limite de Anúncios",
        help_text="Número máximo de anúncios ATIVOS que o usuário pode ter com este plano (ex: 1, 5)"
    )
    is_ativo = models.BooleanField(
        default=True,
        verbose_name="Plano Ativo?",
        help_text="Se marcado, o plano aparecerá na página 'Planos e Preços' para contratação."
    )

    def __str__(self):
        return f"{self.nome} (R$ {self.preco} / {self.duracao_dias} dias)"
    
    class Meta:
        verbose_name = "Plano"
        verbose_name_plural = "Planos"

# -----------------------------------------------------------------
# MODELO: ASSINATURA (Sem mudanças)
# -----------------------------------------------------------------
class Assinatura(models.Model):
    class StatusAssinatura(models.TextChoices):
        PENDENTE = 'PENDENTE', 'Pendente de Pagamento'
        ATIVA = 'ATIVA', 'Ativa'
        EXPIRADA = 'EXPIRADA', 'Expirada'
        CANCELADA = 'CANCELADA', 'Cancelada'

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="assinatura",
        null=True 
    )
    plano = models.ForeignKey(Plano, on_delete=models.SET_NULL, null=True, verbose_name="Plano")
    status = models.CharField(
        max_length=20, 
        choices=StatusAssinatura.choices, 
        default=StatusAssinatura.PENDENTE
    )
    data_inicio = models.DateTimeField(verbose_name="Data de Início", null=True, blank=True)
    data_expiracao = models.DateTimeField(verbose_name="Data de Expiração", null=True, blank=True)
    
    def __str__(self):
        return f"{self.usuario.username if self.usuario else 'Sem Usuário'} - Plano {self.plano.nome if self.plano else 'N/A'}"

    class Meta:
        verbose_name = "Assinatura de Usuário"
        verbose_name_plural = "Assinaturas de Usuários"

# -----------------------------------------------------------------
# MODELO 'Imovel' (Sem mudanças)
# -----------------------------------------------------------------
class Imovel(models.Model):
    
    class Finalidade(models.TextChoices):
        VENDA = 'VENDA', 'Venda'
        ALUGUEL = 'ALUGUEL', 'Aluguel'
    
    class StatusPublicacao(models.TextChoices):
        PENDENTE_APROVACAO = 'PEND_APROV', 'Pendente de Aprovação'
        ATIVO = 'ATIVO', 'Ativo'
        EXPIRADO = 'EXPIRADO', 'Expirado'
        REJEITADO = 'REJEITADO', 'Rejeitado'
        PAUSADO = 'PAUSADO', 'Pausado'

    finalidade = models.CharField(
        max_length=10, choices=Finalidade.choices, default=Finalidade.VENDA,
        verbose_name="Finalidade (Venda/Aluguel)", null=True, blank=True
    )
    destaque = models.BooleanField(default=False, verbose_name="Destaque?")
    
    proprietario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='imoveis')
    
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

    status_publicacao = models.CharField(
        max_length=20,
        choices=StatusPublicacao.choices,
        # --- [LINHA CORRIGIDA] ---
        # Troquei 'StatusPublica' por 'StatusPublicacao'
        default=StatusPublicacao.PENDENTE_APROVACAO,
        # -------------------------
        verbose_name="Status da Publicação"
    )
    data_aprovacao = models.DateTimeField(null=True, blank=True, verbose_name="Data de Aprovação")
    data_expiracao = models.DateTimeField(null=True, blank=True, verbose_name="Data de Expiração")

    def __str__(self):
        if self.titulo:
            return self.titulo
        return f"Imóvel ID {self.id}"
    
# -----------------------------------------------------------------
# MODELO 'Foto' (Sem mudanças)
# -----------------------------------------------------------------
class Foto(models.Model):
    imovel = models.ForeignKey(Imovel, related_name='fotos', on_delete=models.CASCADE)
    imagem = models.ImageField(upload_to='fotos_galeria/')
    def __str__(self): return f"Foto de {self.imovel.titulo or self.imovel.id}"