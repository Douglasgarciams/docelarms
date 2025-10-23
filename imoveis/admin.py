# imoveis/admin.py
from django.contrib import admin
from .models import Imovel, Foto, Cidade, Imobiliaria, Bairro # 1. Importamos o novo modelo Bairro

class FotoInline(admin.TabularInline):
    model = Foto
    extra = 1

@admin.register(Imovel)
class ImovelAdmin(admin.ModelAdmin):
    inlines = [ FotoInline ]
    # 2. Adicionamos 'bairro' para fácil visualização e filtragem
    list_display = ('titulo', 'imobiliaria', 'cidade', 'bairro', 'preco', 'aprovado', 'destaque')
    list_filter = ('cidade', 'bairro', 'imobiliaria', 'finalidade', 'aprovado', 'destaque')
    search_fields = ('titulo', 'descricao', 'endereco')
    actions = ['aprovar_anuncios', 'marcar_como_destaque']

    @admin.action(description="Aprovar anúncios selecionados")
    def aprovar_anuncios(self, request, queryset):
        queryset.update(aprovado=True)

    @admin.action(description="Marcar como destaque os anúncios selecionados")
    def marcar_como_destaque(self, request, queryset):
        queryset.update(destaque=True)

# --- 3. NOVA CLASSE ADMIN PARA GERENCIAR BAIRROS ---
@admin.register(Bairro)
class BairroAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cidade')
    list_filter = ('cidade',)
    search_fields = ('nome',)
# --------------------------------------------------

@admin.register(Imobiliaria)
class ImobiliariaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cidade', 'telefone', 'telefone_secundario')
    search_fields = ('nome',)

# Registra os outros modelos
admin.site.register(Cidade)
admin.site.register(Foto)