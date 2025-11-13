# imoveis/admin.py
from django.contrib import admin
# 1. Importamos os novos modelos, incluindo 'Assinatura'
from .models import Imovel, Foto, Cidade, Imobiliaria, Bairro, Plano, Assinatura, NichoParceiro, Parceiro
from django.utils import timezone
from datetime import timedelta

class FotoInline(admin.TabularInline):
    model = Foto
    extra = 1

@admin.register(Imovel)
class ImovelAdmin(admin.ModelAdmin):
    inlines = [ FotoInline ]
    
    # 2. 'plano' foi REMOVIDO daqui (pois não existe mais no Imovel)
    list_display = (
        'titulo', 
        'proprietario', # Adicionei para você saber quem é o dono
        'imobiliaria', 
        'cidade', 
        'bairro', 
        'preco', 
        # 'plano',              # <-- REMOVIDO (Estava causando o erro)
        'status_publicacao', 
        'destaque'
    )
    
    # 3. 'plano' foi REMOVIDO daqui (pois não existe mais no Imovel)
    list_filter = (
        'status_publicacao',
        # 'plano',              # <-- REMOVIDO (Estava causando o erro)
        'cidade', 
        'bairro', 
        'imobiliaria', 
        'finalidade', 
        'destaque'
    )
    
    search_fields = ('titulo', 'descricao', 'endereco')
    
    actions = ['aprovar_anuncios', 'marcar_como_destaque']

    # 4. Ação 'aprovar_anuncios' ATUALIZADA para usar a Assinatura do usuário
    @admin.action(description="Aprovar anúncios (mudar status para Ativo)")
    def aprovar_anuncios(self, request, queryset):
        """
        Muda o status de 'Pendente de Aprovação' para 'Ativo' 
        e calcula a data de expiração baseado na ASSINATURA do proprietário.
        """
        for imovel in queryset:
            # Só aprova se já estiver Pendente de Aprovação
            if imovel.status_publicacao == Imovel.StatusPublicacao.PENDENTE_APROVACAO:
                
                try:
                    # Busca a assinatura do dono do imóvel
                    assinatura_usuario = imovel.proprietario.assinatura
                    
                    # Verifica se a assinatura está ATIVA e tem um plano
                    if assinatura_usuario and assinatura_usuario.status == 'ATIVA' and assinatura_usuario.plano:
                        
                        duracao_dias = assinatura_usuario.plano.duracao_dias
                        
                        # Atualiza o imóvel
                        imovel.status_publicacao = Imovel.StatusPublicacao.ATIVO
                        imovel.data_aprovacao = timezone.now()
                        imovel.data_expiracao = timezone.now() + timedelta(days=duracao_dias)
                        
                        imovel.save(update_fields=['status_publicacao', 'data_aprovacao', 'data_expiracao'])
                    
                    else:
                        # Se a assinatura não estiver ativa, avisa o admin
                        self.message_user(request, f"Não foi possível aprovar '{imovel.titulo}'. A assinatura do usuário '{imovel.proprietario.username}' não está ATIVA.", level='WARNING')
                
                except Assinatura.DoesNotExist:
                    self.message_user(request, f"Não foi possível aprovar '{imovel.titulo}'. O usuário '{imovel.proprietario.username}' não possui uma assinatura.", level='ERROR')
                except Exception as e:
                     self.message_user(request, f"Erro ao aprovar '{imovel.titulo}': {e}", level='ERROR')


    # Ação 'marcar_como_destaque' (Sem mudanças)
    @admin.action(description="Marcar como destaque os anúncios selecionados")
    def marcar_como_destaque(self, request, queryset):
        queryset.update(destaque=True)

# --- Classe Admin para BAIRROS (Sem mudanças) ---
@admin.register(Bairro)
class BairroAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cidade')
    list_filter = ('cidade',)
    search_fields = ('nome',)

# --- Classe Admin para IMOBILIARIA (ATUALIZADA) ---
@admin.register(Imobiliaria)
class ImobiliariaAdmin(admin.ModelAdmin):
    # Adicionado 'usuario' e 'creci' na lista
    list_display = ('nome', 'creci', 'usuario', 'cidade', 'telefone')
    
    # Adicionado 'creci' e 'usuario__username' na busca
    search_fields = ('nome', 'creci', 'usuario__username')
    
    list_filter = ('cidade',) # Adicionado filtro de cidade
    
    # Adicionado 'usuario' e 'creci' no formulário de edição
    fields = (
        'usuario', 
        'nome', 
        'creci', # <-- CAMPO ADICIONADO
        'cidade', 
        'endereco',
        'telefone',
        'telefone_secundario',
        'site',
        'rede_social'
    )
    # Adicionado autocomplete para facilitar a busca de usuário e cidade
    autocomplete_fields = ['usuario', 'cidade']

# --- 5. PlanoAdmin ATUALIZADO (com is_ativo e Ações) ---
@admin.register(Plano)
class PlanoAdmin(admin.ModelAdmin):
    # Adicionamos 'is_ativo'
    list_display = ('nome', 'preco', 'duracao_dias', 'limite_fotos', 'limite_anuncios', 'is_ativo')
    list_filter = ('is_ativo',) # Adicionamos filtro para 'is_ativo'
    search_fields = ('nome',)
    
    # Adicionamos 'is_ativo'
    fields = ('nome', 'descricao', 'preco', 'duracao_dias', 'limite_fotos', 'limite_anuncios', 'is_ativo')
    
    # --- [AÇÕES ADICIONADAS (Seus "Botões")] ---
    actions = ['ativar_planos', 'desativar_planos']

    @admin.action(description="Ativar planos (mostrar no site)")
    def ativar_planos(self, request, queryset):
        queryset.update(is_ativo=True)
        self.message_user(request, "Planos selecionados foram ATIVADOS e agora aparecem no site.", level='SUCCESS')

    @admin.action(description="Desativar planos (esconder do site)")
    def desativar_planos(self, request, queryset):
        queryset.update(is_ativo=False)
        self.message_user(request, "Planos selecionados foram DESATIVADOS e não aparecem mais no site.", level='WARNING')
# --------------------------------------------------

# --- 6. NOVO E IMPORTANTE: Registra o modelo Assinatura ---
@admin.register(Assinatura)
class AssinaturaAdmin(admin.ModelAdmin):
    """
    Este é o seu novo painel principal para aprovar pagamentos!
    """
    list_display = ('usuario', 'plano', 'status', 'data_inicio', 'data_expiracao')
    list_filter = ('status', 'plano')
    search_fields = ('usuario__username', 'usuario__email')
    
    # Campos que o admin pode editar
    fields = ('usuario', 'plano', 'status', 'data_inicio', 'data_expiracao')
    
    # Adiciona autocomplete para facilitar a busca de usuário e plano
    autocomplete_fields = ['usuario', 'plano']
    
    # Ação para facilitar sua vida
    actions = ['ativar_assinaturas']

    @admin.action(description="Ativar assinaturas selecionadas (Ex: Pagamento confirmado)")
    def ativar_assinaturas(self, request, queryset):
        """
        Quando você confirmar o pagamento (ex: no Mercado Pago), 
        venha aqui, selecione a assinatura 'Pendente' e rode esta ação.
        """
        for assinatura in queryset:
            if assinatura.plano and assinatura.status != 'ATIVA':
                assinatura.status = Assinatura.StatusAssinatura.ATIVA
                assinatura.data_inicio = timezone.now()
                assinatura.data_expiracao = timezone.now() + timedelta(days=assinatura.plano.duracao_dias)
                assinatura.save(update_fields=['status', 'data_inicio', 'data_expiracao'])
        
        self.message_user(request, "Assinaturas selecionadas foram ativadas com sucesso.", level='SUCCESS')

# --------------------------------------------------

# --- [INÍCIO DA CORREÇÃO] ---
# Registra 'Cidade' com 'search_fields' para corrigir o erro 'autocomplete_fields'
@admin.register(Cidade)
class CidadeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'estado')
    search_fields = ('nome', 'estado') # <-- Linha obrigatória para o autocomplete funcionar

# Registra 'Foto' (boa prática, mas não obrigatório para o bug)
@admin.register(Foto)
class FotoAdmin(admin.ModelAdmin):
    list_display = ('imovel', 'imagem')
    search_fields = ('imovel__titulo',)
    autocomplete_fields = ['imovel']
# --- [FIM DA CORREÇÃO] ---

# admin.site.register(Cidade) # <-- Linha antiga removida
# admin.site.register(Foto) # <-- Linha antiga removida

# ✅ 2. Crie uma ação de "Aprovar"
@admin.action(description='Aprovar parceiros selecionados')
def aprovar_parceiros(modeladmin, request, queryset):
    queryset.update(status=Parceiro.Status.APROVADO)

# ✅ 3. Configure a listagem dos Parceiros
class ParceiroAdmin(admin.ModelAdmin):
    list_display = ('nome', 'nicho', 'telefone', 'status', 'data_cadastro')
    list_filter = ('status', 'nicho')
    search_fields = ('nome', 'email', 'telefone')
    actions = [aprovar_parceiros] # Adiciona o botão de ação

# ✅ 4. Registre os novos modelos
admin.site.register(NichoParceiro)
admin.site.register(Parceiro, ParceiroAdmin)