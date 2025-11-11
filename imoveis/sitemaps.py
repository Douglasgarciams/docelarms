from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone
from .models import Imovel

class ImovelSitemap(Sitemap):
    """
    Sitemap para os imóveis dinâmicos.
    """
    changefreq = "weekly"  # Com que frequência os imóveis mudam? (weekly/daily)
    priority = 0.9         # Prioridade alta (max é 1.0)

    def items(self):
        # Retorna todos os imóveis que estão publicados e não expirados
        agora = timezone.now()
        return Imovel.objects.filter(
            status_publicacao='ATIVO',
            data_expiracao__gt=agora
        ).order_by('-data_cadastro')

    def lastmod(self, obj):
        # Retorna a data da última modificação (ou cadastro)
        return obj.data_cadastro

    def location(self, obj):
        # Retorna a URL para um imóvel específico
        return reverse('detalhe_imovel', args=[obj.id])


class StaticViewSitemap(Sitemap):
    """
    Sitemap para as páginas estáticas (Home, políticas, contato, etc.)
    """
    priority = 0.5
    changefreq = "monthly" # Essas páginas não mudam com frequência

    def items(self):
        # Retorna os NOMES das URLs estáticas (dos seus urls.py)
        return [
            'lista_imoveis',
            'listar_planos',
            'politica_de_uso',
            'politica_de_qualidade',
            'dicas_de_seguranca',
            'fale_conosco',
            'login',
            'cadastro'
        ]

    def location(self, item):
        # Retorna a URL para cada nome da lista acima
        return reverse(item)