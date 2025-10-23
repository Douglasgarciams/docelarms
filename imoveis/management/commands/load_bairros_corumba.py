# imoveis/management/commands/load_bairros_corumba.py
from django.core.management.base import BaseCommand
from imoveis.models import Cidade, Bairro

class Command(BaseCommand):
    help = 'Cadastra a lista de bairros de Corumbá no banco de dados'

    def handle(self, *args, **options):
        try:
            cidade_corumba = Cidade.objects.get(nome="Corumbá", estado="MS")
            self.stdout.write(self.style.SUCCESS(f"Cidade '{cidade_corumba.nome}' encontrada. Iniciando cadastro de bairros..."))

            # --- LISTA DE BAIRROS CORRIGIDA ---
            lista_de_bairros_corumba = [
                'Aeroporto', 'Área Rural de Corumbá', 'Centro', 'Centro América',
                'Conjunto Cadiwéus', 'Conjunto Guana', 'Conjunto Guatos',
                'Cristo Redentor', 'Dom Bosco', 'Generoso', 'Guaicurus', 'Industrial',
                'Jardim dos Estados', 'Jardim Florestal', 'Maria Leite',
                'Nossa Senhora de Fátima', 'Nova Corumbá', 'Padre Ernesto Sassida',
                'Popular Nova', 'Popular Velha', 'Porto Esperança', 'Previsul',
                'Universitário', 'Vila Guarani', 'Vila Mamona'
            ]
            
            bairros_criados = 0
            for nome_bairro in lista_de_bairros_corumba:
                obj, created = Bairro.objects.get_or_create(nome=nome_bairro, cidade=cidade_corumba)
                if created:
                    bairros_criados += 1

            self.stdout.write(self.style.SUCCESS(f"Processo finalizado! {bairros_criados} novos bairros foram cadastrados para Corumbá."))

        except Cidade.DoesNotExist:
            self.stdout.write(self.style.ERROR("ERRO: A cidade 'Corumbá' não foi encontrada. Por favor, cadastre-a primeiro no painel de administração com o estado 'MS'."))