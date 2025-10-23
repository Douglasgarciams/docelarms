# imoveis/management/commands/load_bairros_dourados.py
from django.core.management.base import BaseCommand
from imoveis.models import Cidade, Bairro

class Command(BaseCommand):
    help = 'Cadastra a lista de bairros de Dourados no banco de dados'

    def handle(self, *args, **options):
        try:
            cidade_dourados = Cidade.objects.get(nome="Dourados", estado="MS")
            self.stdout.write(self.style.SUCCESS(f"Cidade '{cidade_dourados.nome}' encontrada. Iniciando cadastro de bairros..."))

            lista_de_bairros_dourados = [
                'Aldeia Bororó', 'Aldeia Jaguapiru', 'Alto da Boa Vista', 'Alto das Paineiras', 
                'Altos do Indaiá', 'Área Rural de Dourados', 'BNH I Plano', 
                'Bourbon Premiun Residence', 'Caiman', 'Campo Belo', 'Campo Belo III', 
                'Campo Dourado', 'Canaã I', 'Canaã II', 'Canaã III', 'Centro', 
                'Chácara Califórnia', 'Chácara Castelo I', 'Chácara Castelo II', 
                'Chácara Cidélis', 'Cohafaba III Plano', 'Ecoville', 'Esplanada', 
                'Jardim Água Boa', 'Jardim Alhambra', 'Jardim Aline', 'Jardim América', 
                'Jardim Ayde', 'Jardim Caramuru', 'Jardim Carisma', 'Jardim Central', 
                'Jardim Clímax', 'Jardim Colibri', 'Jardim Cristhais', 
                'Jardim das Palmeiras', 'Jardim das Primaveras', 'Jardim Deoclécio Artuzzi', 
                'Jardim Deoclécio Artuzzi II', 'Jardim do Bosque', 'Jardim dos Estados', 
                'Jardim dos Eucaliptos', 'Jardim Dubai', 'Jardim Europa', 
                'Jardim Flamboyant', 'Jardim Flórida', 'Jardim Guaicurus', 
                'Jardim Guanabara', 'Jardim Harrisom de Figueiredo', 'Jardim Hilda', 
                'Jardim Independência', 'Jardim Itaipú', 'Jardim Itapiri', 
                'Jardim João Paulo II', 'Jardim Jóquei Clube', 'Jardim Londrina', 
                'Jardim Maracanã', 'Jardim Márcia', 'Jardim Marília', 'Jardim Maringá', 
                'Jardim Mônaco', 'Jardim Monte Alegre', 'Jardim Monte Líbano', 
                'Jardim Novo Horizonte', 'Jardim Paulista', 'Jardim Piratininga', 
                'Jardim Rasslem', 'Jardim Santa Hermínia', 'Jardim Santa Maria', 
                'Jardim São Cristóvão', 'Jardim São Pedro', 'Jardim Shekiná', 
                'Jardim Syria Rasselen', 'Jardim Tropical', 'Jardim Universitário', 
                'Jardim Vitória', 'Laranja Doce', 'Loteamento Flor de Lis', 
                'Loteamento Pousada dos Pássaros', 'Panambi Vera', 'Parque Alvorada', 
                'Parque das Nações', 'Parque das Nações II', 'Parque do Lago', 
                'Parque do Lago II', 'Parque dos Beija-flores', 'Parque dos Bem-te-vis', 
                'Parque dos Coqueiros', 'Parque dos Jequitibás', 'Parque Nova Dourados', 
                'Parque Residencial Pelicano', 'Parque Rincão I', 'Parque Rincão II', 
                'Portal de Dourados', 'Porto Madero', 'Porto Seguro', 'Residencial Bonanza', 
                'Residencial Cidade Jardim I', 'Residencial Greenville', 'Residencial Kairós', 
                'Residencial Monte Sião I', 'Residencial Pantanal', 'Vila Alba', 
                'Vila Almeida', 'Vila Amaral', 'Vila Aurora', 'Vila Cachoeirinha', 
                'Vila Cuiabá', 'Vila Erondina', 'Vila Esperança', 'Vila Industrial', 
                'Vila Mariana', 'Vila Martins', 'Vila Nova Esperança', 'Vila Planalto', 
                'Vila Popular', 'Vila Progresso', 'Vila Rosa', 'Vila Rubi', 
                'Vila Santa Catarina', 'Vila Santo André', 'Vila São Braz', 
                'Vila São Francisco', 'Vila São João', 'Vila São Luiz', 'Vila Toscana', 
                'Vila Toscana II', 'Vila Ubiratan', 'Vival Castelo', 'Vival dos Ipês', 
                'Walter Brandão da Silva', 'Ypê Roxo'
            ]
            
            bairros_criados = 0
            for nome_bairro in lista_de_bairros_dourados:
                obj, created = Bairro.objects.get_or_create(nome=nome_bairro, cidade=cidade_dourados)
                if created:
                    bairros_criados += 1

            self.stdout.write(self.style.SUCCESS(f"Processo finalizado! {bairros_criados} novos bairros foram cadastrados para Dourados."))

        except Cidade.DoesNotExist:
            self.stdout.write(self.style.ERROR("ERRO: A cidade 'Dourados' não foi encontrada. Por favor, cadastre-a primeiro no painel de administração com o estado 'MS'."))