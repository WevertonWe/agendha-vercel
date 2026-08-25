import os
import sys
import asyncio
import logging
from pathlib import Path

# Add project root to path so we can import from app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_vision import identificar_tipo_atividade_gemini
from app.services.scanner_service import normalizar_texto

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Diretório base dos técnicos
BASE_DIR = Path(r"C:\Users\CLIENTE\Desktop\BAHIA_SEM_FOME\weverton\técnicos")

async def processar_pastas_em_lote():
    if not BASE_DIR.exists():
        logger.error(f"O diretório base não existe: {BASE_DIR}")
        return

    logger.info("Iniciando varredura das pastas de datas...")
    count_sucesso = 0
    count_erro = 0
    
    # Busca todas as subpastas que pareçam ser datas (ex: DD.MM.YYYY) 
    # e que NÃO tenham a atividade no nome ainda.
    # Exemplo: 05.11.2025 (10 caracteres)
    
    pastas_para_processar = []
    
    for item in BASE_DIR.rglob("*"):
        if item.is_dir() and len(item.name) == 10:
            partes = item.name.split('.')
            if len(partes) == 3 and partes[0].isdigit() and partes[1].isdigit() and partes[2].isdigit():
                pastas_para_processar.append(item)

    logger.info(f"Foram encontradas {len(pastas_para_processar)} pastas de datas para processar.")
    
    for idx, pasta in enumerate(pastas_para_processar, 1):
        logger.info(f"[{idx}/{len(pastas_para_processar)}] Analisando pasta: {pasta}")
        
        # Encontra o primeiro PDF ou imagem na pasta
        arquivos = [f for f in pasta.iterdir() if f.is_file() and f.suffix.lower() in ('.pdf', '.jpg', '.jpeg', '.png')]
        if not arquivos:
            logger.warning(f"Sem arquivos PDF/Imagem na pasta {pasta.name}, ignorando...")
            continue
            
        arquivo = arquivos[0]
        
        try:
            with open(arquivo, "rb") as f:
                file_bytes = f.read()
                
            atividade = await identificar_tipo_atividade_gemini(file_bytes, arquivo.name)
            
            if atividade and atividade != "DOCUMENTO" and atividade != "DOCUMENTO_SEM_IA":
                novo_nome = f"{pasta.name} - {atividade}"
                nova_pasta_path = pasta.parent / novo_nome
                
                try:
                    pasta.rename(nova_pasta_path)
                    logger.info(f"✅ Renomeado: {pasta.name} -> {novo_nome}")
                    count_sucesso += 1
                except Exception as e_ren:
                    logger.error(f"Erro ao renomear {pasta} para {novo_nome}: {e_ren}")
                    count_erro += 1
            else:
                logger.warning(f"A IA não encontrou atividade conclusiva para {pasta.name}.")
                count_erro += 1
                
        except Exception as e:
            logger.error(f"Erro ao processar o arquivo {arquivo.name} na pasta {pasta.name}: {e}")
            count_erro += 1
            
        # Pausa de 5 segundos para respeitar o limite de 15 RPM da camada gratuita do Google AI Studio
        await asyncio.sleep(5)
        
    logger.info(f"Processamento concluído. Sucessos: {count_sucesso} | Erros ou não identificados: {count_erro}")

if __name__ == "__main__":
    asyncio.run(processar_pastas_em_lote())
