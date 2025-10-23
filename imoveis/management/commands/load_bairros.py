# imoveis/management/commands/load_bairros.py
from django.core.management.base import BaseCommand
from imoveis.models import Cidade, Bairro

class Command(BaseCommand):
    help = 'Cadastra a lista de bairros de Campo Grande no banco de dados'

    def handle(self, *args, **options):
        try:
            cidade_cg = Cidade.objects.get(nome="Campo Grande", estado="MS")
            self.stdout.write(self.style.SUCCESS(f"Cidade '{cidade_cg.nome}' encontrada. Iniciando cadastro de bairros..."))

            lista_de_bairros_cg = [
                'Água Limpa Park', 'Aguadinha', 'Alameda dos Castelos', 'Alphaville Campo Grande', 
                'Alphaville Campo Grande 3', 'Alphaville Campo Grande 4', 'Altos da Mata', 
                'Altos do Panamá', 'Alves Pereira', 'Amambaí', 'Amantini Residence', 
                'Área Rural de Campo Grande', 'Arnaldino da Silva', 'Arnaldo Estevão Figueiredo', 
                'Ary Abussafi de Lima', 'Autonomista', 'Bairro Industrial', 'Bairro São Pedro', 
                'Bairro Seminário', 'Barra da Tijuca II', 'Bela Vista', 'Bosque Santa Mônica', 
                'Caiobá', 'Carandá Bosque I', 'Carandá Bosque II', 'Centro', 'Cidade Jardim', 
                'Cidade Morena', 'Cruzeiro', 'Glória', 'Guanandi', 'Itanhangá Park', 
                'Jardim Aclimação', 'Jardim Alto São Francisco', 'Jardim Antares', 
                'Jardim Aquarela', 'Jardim Bela Vista', 'Jardim Bonança', 'Jardim Brasil', 
                'Jardim Carioca', 'Jardim Centro Oeste', 'Jardim Colibri II', 'Jardim Colônia', 
                'Jardim dos Estados', 'Jardim Enseada dos Pássaros', 'Jardim Fluminense', 
                'Jardim Itaíia', 'Jardim Itatibaia', 'Jardim Itatiaia', 'Jardim Itapuã', 
                'Jardim Jatobá', 'Jardim Mansur', 'Jardim Monte Alegre', 'Jardim Monte Líbano', 
                'Jardim Nashville', 'Jardim Nova Capital', 'Jardim Nova Era', 
                'Jardim Novo Seminário', 'Jardim Panamá', 'Jardim Piratininga', 
                'Jardim São Bento', 'Jardim Seminário', 'Jardim Sumatra', 'Jardim Tijuca', 
                'Jardim Tropical', 'Jardim Veraneio', 'Jardim Vida Nova', 'Lageado', 
                'Los Angeles', 'Monte Castelo', 'Moreninha', 'Moreninha I', 'Moreninha II', 
                'Moreninha III', 'Moreninha IV', 'Nasser', 'Noroeste', 'Nova Campo Grande', 
                'Nova Lima', 'Ouro Preto', 'Parque do Sol', 'Parque Residencial dos Girassóis', 
                'Porto Galo', 'Residencial Alto Tamandaré', 'Residencial Áqua­rius I', 
                'Residencial Betaville', 'Residencial Damha', 'Residencial Damha II', 
                'Residencial Estrela Park', 'Residencial Gama', 'Residencial Mario Covas', 
                'Residencial Oliveira III', 'Residencial Ramez Tebet', 'Santa Fé', 
                'Santa Luzia', 'São Conrado', 'São Francisco', 'Tiradentes', 'Universitário', 
                'Vila Albuquerque', 'Vila Antônio Vendas', 'Vila Bandeirantes', 
                'Vila Belo Horizonte', 'Vila Carlota', 'Vila Duque de Caxias', 'Vila Eliane', 
                'Vila Fernanda', 'Vila Gomes', 'Vila Ieda', 'Vila Jardim Botafogo', 
                'Vila Jardim Paulista', 'Vila Lucinda', 'Vila Miguel Couto', 'Vila Nogueira', 
                'Vila Palmira', 'Vila Popular', 'Vila Rosa Pires', 'Vila Santa Dorotéia', 
                'Vila Serradinho', 'Zé Pereira', 'outros'
            ]
            
            bairros_criados = 0
            for nome_bairro in lista_de_bairros_cg:
                obj, created = Bairro.objects.get_or_create(nome=nome_bairro, cidade=cidade_cg)
                if created:
                    bairros_criados += 1

            self.stdout.write(self.style.SUCCESS(f"Processo finalizado! {bairros_criados} novos bairros foram cadastrados para Campo Grande."))

        except Cidade.DoesNotExist:
            self.stdout.write(self.style.ERROR("ERRO: A cidade 'Campo Grande' não foi encontrada. Por favor, cadastre-a primeiro no painel de administração com o estado 'MS'."))