# imoveis/migrations/0021_popular_nichos_parceiros.py

from django.db import migrations
from django.utils.text import slugify

# A LISTA COMPLETA DE NICHOS
NICHOS_LIST = [
    "Aquecedores Solar", "Ar Condicionado", "Arquitetos", 
    "Automação Predial e Residencial", "Avaliadores de Imóveis", 
    "Caçambas e Entulhos", "Calheiros", "Cerâmicas", "Chaveiros", 
    "Compensados", "Concreto Pré-Moldado", "Construtores", 
    "Corretoras de Seguro", "Decoração", "Eletricistas", 
    "Eletrodomésticos", "Encanadores", "Engenheiros", "Esquadrias", 
    "Ferramentas", "Forro", "Gesso", "Iluminação", 
    "Impermeabilizações", "Limpa Fossa", "Limpeza", "Madeireiras", 
    "Marceneiros", "Marmoaria", "Material de Construção", "Móveis", 
    "Móveis Planejados", "Paisagismo", "Pequenos Reparos", 
    "Persianas", "Pintores", "Piscinas", "Pisos", "Poços", 
    "Portões Eletrônicos", "Quadros e Molduras", "Segurança", 
    "Serralheiros", "Telefonia e Internet", "Telhas", "Tintas", 
    "Toldos", "Tv Assinatura", "Vidro e Box"
]

def popular_nichos(apps, schema_editor):
    """
    Pega cada nome da lista, cria um slug e o insere no banco.
    """
    NichoParceiro = apps.get_model('imoveis', 'NichoParceiro')
    
    for nome_nicho in NICHOS_LIST:
        nicho_slug = slugify(nome_nicho)
        
        NichoParceiro.objects.get_or_create(
            nome=nome_nicho,
            defaults={'slug': nicho_slug}
        )

class Migration(migrations.Migration):

    # ✅ --- ESTA É A CORREÇÃO ---
    # Nós dizemos ao Django que esta migração (0021) 
    # só pode rodar DEPOIS da migração 0020.
    dependencies = [
        ('imoveis', '0020_nichoparceiro_parceiro'), 
    ]
    # --- FIM DA CORREÇÃO ---

    operations = [
        migrations.RunPython(popular_nichos),
    ]