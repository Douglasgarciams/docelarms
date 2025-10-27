# imoveis/management/commands/test_r2_upload.py
from django.core.management.base import BaseCommand
import os
import boto3
from io import BytesIO

class Command(BaseCommand):
    help = 'Testa diretamente o upload de um arquivo para o Cloudflare R2'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("--- Iniciando teste de upload para o R2 ---"))

        # 1. Ler as credenciais
        try:
            access_key_id = os.environ.get('CLOUDFLARE_R2_ACCESS_KEY_ID')
            secret_access_key = os.environ.get('CLOUDFLARE_R2_SECRET_ACCESS_KEY')
            bucket_name = os.environ.get('CLOUDFLARE_R2_BUCKET_NAME')
            account_id = os.environ.get('CLOUDFLARE_R2_ACCOUNT_ID')
            endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com"

            if not all([access_key_id, secret_access_key, bucket_name, account_id]):
                self.stdout.write(self.style.ERROR("ERRO: Variáveis de ambiente (R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET_NAME, R2_ACCOUNT_ID) não estão todas definidas no Render."))
                return

            self.stdout.write(self.style.SUCCESS("Credenciais lidas do ambiente com sucesso."))
            self.stdout.write(f"Bucket: {bucket_name}, Endpoint: {endpoint_url}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erro ao ler variáveis de ambiente: {e}"))
            return

        # 2. Configurar o cliente boto3
        try:
            s3_client = boto3.client(
                's3',
                endpoint_url=endpoint_url,
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
                region_name='auto',
                config=boto3.session.Config(signature_version='s3v4'),
            )
            self.stdout.write(self.style.SUCCESS("Cliente Boto3 (S3) configurado."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"ERRO ao configurar o cliente Boto3: {e}"))
            return

        # 3. Tentar o upload
        try:
            dummy_file_content = b"Este eh um arquivo de teste vindo do comando manage.py."
            dummy_file = BytesIO(dummy_file_content)
            file_key = 'media/test/manage_py_test.txt'

            self.stdout.write(f"Tentando enviar '{file_key}' para o bucket '{bucket_name}'...")

            s3_client.put_object(
                Bucket=bucket_name,
                Key=file_key,
                Body=dummy_file
            )
            self.stdout.write(self.style.SUCCESS("--- SUCESSO! Upload concluído. ---"))
            self.stdout.write(self.style.NOTICE("Verifique o bucket 'docelarms' no Cloudflare R2 agora. Você deve ver a pasta 'media', 'test' e o arquivo 'manage_py_test.txt'."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"--- ERRO DURANTE O UPLOAD (put_object) ---"))
            self.stdout.write(self.style.ERROR(f"Erro: {e}"))