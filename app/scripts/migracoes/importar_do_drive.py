import os
import io
import sqlite3
import requests
import json
import logging
import shutil
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from app.config import settings

# ==============================================================================
# CONFIGURAÇÕES - AJUSTE AQUI
# ==============================================================================

ID_PASTA_TECNICOS_DRIVE = "1jpjYrb_WDb_LyxeQNcEOYIx_bWWiA-Ht"
CAMINHO_CREDENCIAS = "google_credentials.json"
NOME_BANCO_DE_DADOS = "app/agendha.db"
URL_UPLOAD_API = "http://127.0.0.1:8000/upload"
PASTA_DOWNLOADS_TEMP = "temp_downloads"
PASTA_UPLOADS = "app/uploads"

# ==============================================================================


def limpar_dados_antigos():
    """Apaga todos os registos da fila de validação e os ficheiros na pasta de uploads."""
    print("\n🔥 Iniciando processo de limpeza...")

    # 1. Limpar a tabela validacao_pendente
    try:
        conexao = sqlite3.connect(NOME_BANCO_DE_DADOS)
        cursor = conexao.cursor()
        print("   - A apagar registos da tabela 'validacao_pendente'...")
        cursor.execute("DELETE FROM validacao_pendente;")
        cursor.execute(
            "DELETE FROM sqlite_sequence WHERE name='validacao_pendente';")
        conexao.commit()
        conexao.close()
        print("   ✅ Tabela 'validacao_pendente' limpa com sucesso.")
    except Exception as e:
        print(f"   ❌ Erro ao limpar a tabela: {e}")

    # 2. Limpar a pasta de uploads
    try:
        if os.path.exists(PASTA_UPLOADS):
            print(f"   - A apagar ficheiros da pasta '{PASTA_UPLOADS}'...")
            for filename in os.listdir(PASTA_UPLOADS):
                file_path = os.path.join(PASTA_UPLOADS, filename)
                os.remove(file_path)
            print(f"   ✅ Pasta '{PASTA_UPLOADS}' limpa com sucesso.")
        else:
            print(
                f"   - Pasta '{PASTA_UPLOADS}' não encontrada, nada a limpar.")
    except Exception as e:
        print(f"   ❌ Erro ao limpar a pasta de uploads: {e}")

    print("🔥 Limpeza concluída.")


def autenticar_google_drive():
    """Autentica na API do Google Drive usando a conta de serviço."""
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    
    if settings.GOOGLE_APPLICATION_CREDENTIALS_JSON:
        try:
            creds_info = json.loads(settings.GOOGLE_APPLICATION_CREDENTIALS_JSON)
            creds = service_account.Credentials.from_service_account_info(
                creds_info, scopes=SCOPES
            )
        except Exception as e:
            print(f"❌ ERRO CRÍTICO: Falha ao carregar credenciais JSON: {e}")
            raise
    else:
        print("❌ ERRO CRÍTICO: GOOGLE_APPLICATION_CREDENTIALS_JSON não está definido no .env!")
        raise ValueError("Credenciais do Google ausentes no ambiente.")
        
    service = build('drive', 'v3', credentials=creds)
    print("✅ Autenticação com o Google Drive bem-sucedida.")
    return service


def get_ficheiros_ja_processados(db_path):
    """Busca no DB a lista de IDs de ficheiros do Drive que já foram processados."""
    conexao = sqlite3.connect(db_path)
    cursor = conexao.cursor()
    cursor.execute("SELECT google_drive_file_id FROM validacao_pendente")
    resultados = [row[0] for row in cursor.fetchall()]
    conexao.close()
    return set(resultados)


def importar_arquivos():
    """Função principal que orquestra a importação."""

    print("\n" + "="*50)
    resposta = input(
        "🧹 Deseja apagar TODOS os dados da fila e os ficheiros antigos antes de importar? (s/N): ")
    if resposta.lower() in ['s', 'sim']:
        limpar_dados_antigos()
    else:
        print("\nSkipping cleanup. A importar apenas ficheiros novos.")
    print("="*50 + "\n")

    drive_service = autenticar_google_drive()
    ficheiros_processados = get_ficheiros_ja_processados(NOME_BANCO_DE_DADOS)
    print(
        f"Encontrados {len(ficheiros_processados)} ficheiros já processados na base de dados.")
    os.makedirs(PASTA_DOWNLOADS_TEMP, exist_ok=True)

    try:
        query_tecnicos = f"'{ID_PASTA_TECNICOS_DRIVE}' in parents and mimeType = 'application/vnd.google-apps.folder'"
        pastas_tecnicos = drive_service.files().list(
            q=query_tecnicos, fields="files(id, name)").execute().get('files', [])

        for tecnico in pastas_tecnicos:
            print(f"\n🔎 Verificando a pasta do técnico: {tecnico['name']}")
            query_cadastros = f"'{tecnico['id']}' in parents and name = 'cadastros' and mimeType = 'application/vnd.google-apps.folder'"
            pasta_cadastro = drive_service.files().list(
                q=query_cadastros, fields="files(id, name)").execute().get('files', [])

            if not pasta_cadastro:
                print(
                    f"   -> Nenhuma subpasta 'cadastros' encontrada para {tecnico['name']}.")
                continue

            id_pasta_cadastro = pasta_cadastro[0]['id']
            query_ficheiros = f"'{id_pasta_cadastro}' in parents and (mimeType='application/pdf' or mimeType contains 'image/')"
            ficheiros = drive_service.files().list(
                q=query_ficheiros, fields="files(id, name)").execute().get('files', [])

            print(
                f"   -> Encontrados {len(ficheiros)} ficheiros na pasta 'cadastros'.")

            for ficheiro in ficheiros:
                file_id = ficheiro['id']
                file_name = ficheiro['name']

                if file_id in ficheiros_processados:
                    print(f"   - Ignorando '{file_name}' (já processado).")
                    continue

                print(f"   + NOVO FICHEIRO ENCONTRADO: '{file_name}'")

                caminho_local_temporario = os.path.join(
                    PASTA_DOWNLOADS_TEMP, file_name)
                request = drive_service.files().get_media(fileId=file_id)
                fh = io.FileIO(caminho_local_temporario, 'wb')
                downloader = MediaIoBaseDownload(fh, request)

                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    print(
                        f"     -> A descarregar... {int(status.progress() * 100)}%.")

                print("     -> Envio para a API de OCR...")
                with open(caminho_local_temporario, 'rb') as f:

                    # =========================================================
                    # == A CORREÇÃO ESTÁ AQUI: de 'files' para 'file'        ==
                    # Esta é a 'etiqueta' que o nosso servidor FastAPI espera.
                    files_to_upload = {'file': (file_name, f)}
                    # =========================================================

                    response = requests.post(
                        URL_UPLOAD_API, files=files_to_upload)

                if response.status_code == 200:
                    ocr_result = response.json()
                    print("     -> OCR concluído com sucesso.")

                    caminho_final_do_arquivo = ocr_result.get(
                        'caminho_arquivo_original', '')

                    conexao = sqlite3.connect(NOME_BANCO_DE_DADOS)
                    cursor = conexao.cursor()
                    cursor.execute(
                        """
                        INSERT INTO validacao_pendente (google_drive_file_id, nome_arquivo, caminho_arquivo_local, dados_extraidos_json)
                        VALUES (?, ?, ?, ?)
                        """,
                        (file_id, file_name, caminho_final_do_arquivo,
                         json.dumps(ocr_result))
                    )
                    conexao.commit()
                    conexao.close()
                    print("     -> Resultado guardado na fila de validação.")
                    ficheiros_processados.add(file_id)
                else:
                    print(
                        f"     -> ERRO no OCR: A API retornou o status {response.status_code}")
                    print(f"        Detalhe: {response.text}")

    except Exception as e:
        print(f"\n❌ Ocorreu um erro geral durante a importação: {e}")
        logging.exception("Erro detalhado:")
    finally:
        if os.path.exists(PASTA_DOWNLOADS_TEMP):
            shutil.rmtree(PASTA_DOWNLOADS_TEMP)
            print("\nLimpeza da pasta temporária concluída.")
        print("Script finalizado.")


if __name__ == "__main__":
    print("="*50)
    print("INICIANDO SCRIPT DE IMPORTAÇÃO DO GOOGLE DRIVE")
    importar_arquivos()
