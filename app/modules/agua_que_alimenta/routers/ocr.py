import logging
import os
import shutil
import uuid
import json

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Form
import sqlite3

from app.services.ocr import processar_ocr_completo
from app.config import settings
from app.dependencies import get_db_connection
from app.services.conferencia import processar_conferencia_excel
from app.services import store # Import JSON store service

# Router configuration
# Using a single Prefix for OCR related tasks
router = APIRouter(prefix="/api/ocr", tags=["OCR e Validação"])

@router.post("/upload", summary="Recebe um arquivo, executa OCR com Gemini e retorna os dados")
async def upload_e_processar_ocr(
    file: UploadFile = File(...),
    # db: sqlite3.Connection = Depends(get_db_connection), # Removed DB dependency for this route
):
    """
    Endpoint para processamento de OCR via Gemini Flash.
    
    Etapas:
    1. Salva o arquivo temporariamente.
    2. Envia para o serviço de AI Vision (via wrapper de OCR).
    3. Retorna os dados estruturados e salva na fila de validação (JSON/Store).
    
    Returns:
        JSON com status, dados extraídos e ID da fila.
    """
    try:
        # 1. Validar e Salvar Arquivo
        ext = os.path.splitext(file.filename)[1]
        if not ext:
            ext = ".pdf" # Default fallback
            
        nome_arquivo_unico = f"{uuid.uuid4().hex[:12]}{ext}"
        # Save relative path for storage
        caminho_relativo = f"uploads/{nome_arquivo_unico}"
        caminho_salvo_absoluto = str(settings.UPLOAD_FOLDER / nome_arquivo_unico)
        
        # Garantir que a pasta existe
        os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
        
        with open(caminho_salvo_absoluto, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        logging.info(f"Arquivo salvo para OCR: {caminho_salvo_absoluto}")

        # 2. Processar com Gemini
        dados_extraidos = await processar_ocr_completo(caminho_salvo_absoluto)
        
        # 3. Preparar Item da Fila
        item_fila = {
            "nome_arquivo": file.filename,
            "caminho_arquivo_local": caminho_relativo,
            "dados_extraidos": dados_extraidos,
            "status": "Aguardando Validação"
        }

        # 4. Salvar na Fila de Validação (JSON)
        item_salvo = store.add_to_queue(item_fila)
        
        logging.info(f"Item adicionado à fila JSON: {item_salvo.get('id')}")
        
        # 5. Retornar Resultado para o Frontend (Cards)
        return {
            "status": "success",
            "message": "Processamento concluído",
            "nome_completo": dados_extraidos.get("nome_completo", dados_extraidos.get("nome", "Não identificado")),
            "cpf": dados_extraidos.get("cpf", "---"),
            "id_fila": item_salvo.get('id'),
            "raw_data": dados_extraidos 
        }

    except Exception as e:
        logging.error(f"Erro no endpoint de OCR: {e}", exc_info=True)
        # Tentar limpar arquivo em caso de erro
        if 'caminho_salvo_absoluto' in locals() and os.path.exists(caminho_salvo_absoluto):
            try:
                os.remove(caminho_salvo_absoluto)
            except:  # noqa: E722
                pass
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fila-validacao")
def listar_itens_pendentes():
    """
    Retorna a lista de itens pendentes do JSON.
    """
    try:
        fila = store.load_queue()
        return fila
    except Exception as e:
        logging.error(f"Erro ao listar fila: {e}")
        raise HTTPException(status_code=500, detail="Erro ao carregar fila de validação")


@router.get("/fila-validacao/{item_id}")
def get_item_pendente_por_id(item_id: str):
    """
    Retorna um item específico da fila JSON.
    """
    item = store.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado na fila de validação")
    return item


@router.delete("/fila-validacao/{item_id}")
def delete_item_pendente(item_id: str):
    """
    Remove um item da fila de validação.
    """
    sucesso = store.delete_item(item_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Item não encontrado para exclusão")
    return {"status": "success", "message": "Item removido com sucesso"}


# --- Outros Endpoints Relacionados (Mantidos com SQL por enquanto se não forem de validação OCR) ---

@router.post("/conferencia/verificar")
async def verificar_conferencia_excel(
    municipio_id: str = Form(...),
    arquivo_excel: UploadFile = File(...),
    db: sqlite3.Connection = Depends(get_db_connection)
):
    """
    Processa planilha Excel de Conferência (Caixa Econômica).
    
    1. Valida município.
    2. Lê o Excel e cruza com dados do banco.
    3. Gera estatísticas de divergência.
    """
    logging.info(f"DEBUG: Recebido municipio={municipio_id}, arquivo={arquivo_excel.filename}")

    municipios_validos = ["ABARE", "CHORROCHO", "GLORIA", "MACURURE", "PAULO_AFONSO", "RODELAS"]
    if municipio_id not in municipios_validos:
        raise HTTPException(status_code=400, detail=f"Município inválido: {municipio_id}")

    return await processar_conferencia_excel(arquivo_excel, municipio_id, db)


@router.get("/conferencia/historico")
def listar_historico_conferencias(db: sqlite3.Connection = Depends(get_db_connection)):
    cursor = db.cursor()
    try:
        cursor.execute("SELECT id, municipio, data_criacao, resumo_json FROM historico_conferencias ORDER BY id DESC LIMIT 10")
        registros = cursor.fetchall()
        resultado = []
        for r in registros:
            row = dict(r)
            try:
                full_json = json.loads(row['resumo_json'])
                row['resumo_metas'] = full_json.get('stats', {}) 
                # Importante: Removemos a lista mestra (pesada) da resposta de listagem
                del row['resumo_json'] 
            except:  # noqa: E722
                row['resumo_metas'] = {}
            resultado.append(row)
        return resultado
    except sqlite3.OperationalError:
        return [] 


@router.get("/conferencia/historico/{item_id}")
def get_historico_detalhe(item_id: int, db: sqlite3.Connection = Depends(get_db_connection)):
    cursor = db.cursor()
    cursor.execute("SELECT resumo_json FROM historico_conferencias WHERE id = ?", (item_id,))
    registro = cursor.fetchone()
    if not registro:
        raise HTTPException(status_code=404, detail="Histórico não encontrado")
    
    return json.loads(registro['resumo_json'])


@router.delete("/conferencia/historico/{item_id}")
async def excluir_historico(item_id: int, db: sqlite3.Connection = Depends(get_db_connection)):
    cursor = db.cursor()
    cursor.execute("DELETE FROM historico_conferencias WHERE id = ?", (item_id,))
    db.commit()
    return {"message": "Histórico removido com sucesso"}
