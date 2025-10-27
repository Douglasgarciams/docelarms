# imoveis/management/commands/load_bairros_paranaiba.py
from django.core.management.base import BaseCommand
from imoveis.models import Cidade, Bairro

class Command(BaseCommand):
    help = 'Cadastra a lista de bairros de Paranaíba no banco de dados'

    def handle(self, *args, **options):
        try:
            cidade_paranaiba = Cidade.objects.get(nome="Paranaíba", estado="MS")
            self.stdout.write(self.style.SUCCESS(f"Cidade '{cidade_paranaiba.nome}' encontrada. Iniciando cadastro de bairros..."))

            lista_de_bairros_paranaiba = [
                'Árvore Grande',
                'Cachoeira',
                'Centro',
                'Indaiá Grande',
                'Nova Jales',
                'São João do Apore',
                'Tamandaré',
                'Velhacaria',
                'Vila Santo Antonio'
            ]
            
            bairros_criados = 0
            for nome_bairro in lista_de_bairros_paranaiba:
                obj, created = Bairro.objects.get_or_create(nome=nome_bairro, cidade=cidade_paranaiba)
                if created:
                    bairros_criados += 1

            self.stdout.write(self.style.SUCCESS(f"Processo finalizado! {bairros_criados} novos bairros foram cadastrados para Paranaíba."))

        except Cidade.DoesNotExist:
            self.stdout.write(self.style.ERROR("ERRO: A cidade 'Paranaíba' não foi encontrada. Por favor, cadastre-a primeiro (ou verifique o nome exato) no comando 'load_cidades' ou no painel de administração com o estado 'MS'."))