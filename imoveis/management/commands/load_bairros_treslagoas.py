# imoveis/management/commands/load_bairros_treslagoas.py
from django.core.management.base import BaseCommand
from imoveis.models import Cidade, Bairro

class Command(BaseCommand):
    help = 'Cadastra a lista de bairros de Três Lagoas no banco de dados'

    def handle(self, *args, **options):
        try:
            cidade_tres_lagoas = Cidade.objects.get(nome="Três Lagoas", estado="MS")
            self.stdout.write(self.style.SUCCESS(f"Cidade '{cidade_tres_lagoas.nome}' encontrada. Iniciando cadastro de bairros..."))

            lista_de_bairros_tres_lagoas = [
                'Alto da Boa Vista', 'Área Rural de Três Lagoas', 'Bairro Santos Dumont', 'Carioca', 
                'Centro', 'Chácara Imperial', 'COHAB Jardim Caçula', 'Colinos', 
                'Conjunto Habitacional Imperial', 'Distrito Industrial II', 'Distrito Industrial Varginha', 
                'Dourado', 'Interlagos', 'Ipê', 'Jardim Aeroporto', 'Jardim Alvorada', 'Jardim Angélica', 
                'Jardim Bela Vista', 'Jardim Brasília', 'Jardim Cangalha', 'Jardim Capilé', 
                'Jardim Carandá', 'Jardim das Acácias', 'Jardim das Américas', 'Jardim das Oliveiras', 
                'Jardim das Orquídeas', 'Jardim das Ortências', 'Jardim das Paineiras', 
                'Jardim das Violetas', 'Jardim Dourados', 'Jardim Esperança', 'Jardim Flamboyant', 
                'Jardim Guaporé', 'Jardim Guaporé II', 'Jardim Independência II', 'Jardim Itamarati', 
                'Jardim JK', 'Jardim Maristela', 'Jardim Moçambique', 'Jardim Morumbi', 'Jardim Noroeste', 
                'Jardim Nova Americana', 'Jardim Nova Ipanema', 'Jardim Novo Aeroporto', 'Jardim Oiti', 
                'Jardim Paranapunga', 'Jardim Planalto', 'Jardim Primavera', 'Jardim Primaveril', 
                'Jardim Progresso', 'Jardim Residencial Atenas', 'Jardim Rodrigues', 'Jardim Roriz', 
                'Jardim Santa Aurélia', 'Jardim Santa Júlia', 'Jardim Santa Lourdes', 'Jardim Santo André', 
                'Jardim Vila Verde', 'Jupiá', 'Lapa', 'Loteamento Montanini', 'Nossa Senhora Aparecida', 
                'Nossa Senhora das Graças', 'Nova Europa', 'Nova Três Lagoas', 'Novo Oeste', 
                'Novo Oeste II', 'Parque das Mangueiras', 'Parque Residencial Jamel Ville', 
                'Parque Residencial Jamel Ville II', 'Parque Residencial Orestes Prata Tibery Junior', 
                'Parque Residencial Osmar F Dutra', 'Parque Residencial Quinta da Lagoa', 
                'Parque São Carlos', 'Portal das Águas', 'Recanto das Palmeiras', 'Residencial Costa Leste', 
                'Residencial Villa Dumont', 'Santa Luzia', 'Santa Rita', 'Santos Dumont', 'São Jorge', 
                'SETSUL', 'Vila Clementina', 'Vila Coimbra', 'Vila dos Ferroviários', 'Vila Guanabara', 
                'Vila Haro', 'Vila Maria', 'Vila Nova', 'Vila Piloto', 'Vila Popular', 'Vila Santana', 
                'Vila São João', 'Vila São José', 'Vila Terezinha', 'Village do Lago'
            ]
            
            bairros_criados = 0
            for nome_bairro in lista_de_bairros_tres_lagoas:
                obj, created = Bairro.objects.get_or_create(nome=nome_bairro, cidade=cidade_tres_lagoas)
                if created:
                    bairros_criados += 1

            self.stdout.write(self.style.SUCCESS(f"Processo finalizado! {bairros_criados} novos bairros foram cadastrados para Três Lagoas."))

        except Cidade.DoesNotExist:
            self.stdout.write(self.style.ERROR("ERRO: A cidade 'Três Lagoas' não foi encontrada. Por favor, cadastre-a primeiro no painel de administração com o estado 'MS'."))