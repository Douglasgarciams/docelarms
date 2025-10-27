# imoveis/management/commands/load_cidades.py
from django.core.management.base import BaseCommand
from imoveis.models import Cidade

class Command(BaseCommand):
    help = 'Cadastra a lista de cidades do MS no banco de dados'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Iniciando cadastro de cidades do MS..."))

        lista_cidades_ms = [
            'Água Clara', 'Alcinópolis', 'Amambai', 'Anastácio', 'Anaurilândia', 'Angélica', 
            'Antônio João', 'Aparecida do Taboado', 'Aquidauana', 'Aral Moreira', 
            'Bandeirantes', 'Bataguassu', 'Batayporã', 'Bela Vista', 'Bodoquena', 
            'Bonito', 'Brasilândia', 'Caarapó', 'Camapuã', 'Campo Grande', 'Caracol', 
            'Cassilândia', 'Chapadão do Sul', 'Corguinho', 'Coronel Sapucaia', 'Corumbá', 
            'Costa Rica', 'Coxim', 'Deodápolis', 'Dois Irmãos do Buriti', 'Douradina', 
            'Dourados', 'Eldorado', 'Fátima do Sul', 'Figueirão', 'Glória de Dourados', 
            'Guia Lopes da Laguna', 'Iguatemi', 'Inocência', 'Itaporã', 'Itaquiraí', 
            'Ivinhema', 'Japorã', 'Jaraguari', 'Jardim', 'Jateí', 'Juti', 'Ladário', 
            'Laguna Carapã', 'Maracaju', 'Miranda', 'Mundo Novo', 'Naviraí', 'Nioaque', 
            'Nova Alvorada do Sul', 'Nova Andradina', 'Novo Horizonte do Sul', 
            'Paraíso das Águas', # Corrigido para Paraíso das Águas se necessário
            'Paranaíba', 'Paranhos', 'Pedro Gomes', 'Ponta Porã', 
            'Porto Murtinho', 'Ribas do Rio Pardo', 'Rio Brilhante', 'Rio Negro', 
            'Rio Verde de Mato Grosso', 'Rochedo', 'Santa Rita do Pardo', 
            'São Gabriel do Oeste', 'Selvíria', 'Sete Quedas', 'Sidrolândia', 'Sonora', 
            'Tacuru', 'Taquarussu', 'Terenos', 'Três Lagoas', 'Vicentina'
        ]
        
        cidades_criadas = 0
        for nome_cidade in lista_cidades_ms:
            # Assume 'MS' como estado padrão para todas
            obj, created = Cidade.objects.get_or_create(nome=nome_cidade, defaults={'estado': 'MS'})
            if created:
                cidades_criadas += 1

        self.stdout.write(self.style.SUCCESS(f"Processo finalizado! {cidades_criadas} novas cidades foram cadastradas."))

        # Verifica se alguma cidade da lista já existia e não foi criada agora
        cidades_ja_existiam = len(lista_cidades_ms) - cidades_criadas
        if cidades_ja_existiam > 0:
             self.stdout.write(self.style.WARNING(f"{cidades_ja_existiam} cidades já existiam no banco de dados."))