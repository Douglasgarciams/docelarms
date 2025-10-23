# imoveis/management/commands/load_bairros_novaandradina.py
from django.core.management.base import BaseCommand
from imoveis.models import Cidade, Bairro

class Command(BaseCommand):
    help = 'Cadastra a lista de bairros de Nova Andradina no banco de dados'

    def handle(self, *args, **options):
        try:
            cidade_nova_andradina = Cidade.objects.get(nome="Nova Andradina", estado="MS")
            self.stdout.write(self.style.SUCCESS(f"Cidade '{cidade_nova_andradina.nome}' encontrada. Iniciando cadastro de bairros..."))

            lista_de_bairros_nova_andradina = [
                'Centro',
                'Centro Educacional',
                'Cristo',
                'Torre',
                'Morada do Sol',
                'Francisco Alves',
                'Argemiro Ortega',
                'Paris',
                'Guiomar Soares Andrade',
                'Horto Florestal',
                'Campo Verde',
                'Vila Beatriz',
                'Pedro Pedrossian',
                'Exposição',
                'Universitário'
            ]
            
            bairros_criados = 0
            for nome_bairro in lista_de_bairros_nova_andradina:
                obj, created = Bairro.objects.get_or_create(nome=nome_bairro, cidade=cidade_nova_andradina)
                if created:
                    bairros_criados += 1

            self.stdout.write(self.style.SUCCESS(f"Processo finalizado! {bairros_criados} novos bairros foram cadastrados para Nova Andradina."))

        except Cidade.DoesNotExist:
            self.stdout.write(self.style.ERROR("ERRO: A cidade 'Nova Andradina' não foi encontrada. Por favor, cadastre-a primeiro no painel de administração com o estado 'MS'."))