
import json
import logging
import sqlite3
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from app.dependencies import get_db_connection
from app.modules.agua_que_alimenta.services.ai_scanner import extrair_lista_presenca
from app.config import settings

router = APIRouter(prefix="/api/grh", tags=["GRH Scanner"])
logger = logging.getLogger(__name__)

@router.post("/scan-lista")
async def scan_lista_grh(
    file: UploadFile = File(...),
    db: sqlite3.Connection = Depends(get_db_connection)
):
    """
    Scanner de Listas de Presença (GRH) com IA.
    
    1. Envia imagem/PDF para o Gemini (via ai_scanner).
    2. Recebe lista de Nomes/CPFs detectados.
    3. Tenta encontrar 'match' no banco de dados local:
       - Primeiro por CPF (limpo).
       - Depois por Nome (LIKE/Fuzzy).
       
    Retorna JSON enriquecido com flags 'encontrado' e 'id_beneficiario'.
    """
    if not file:
         raise HTTPException(status_code=400, detail="Arquivo obrigatório")
    
    try:
        content = await file.read()
        mime_type = file.content_type or "application/pdf"
        
        # Fallback de mime-type
        if mime_type == "application/octet-stream":
            if file.filename.lower().endswith(".pdf"):
                mime_type = "application/pdf"
            elif file.filename.lower().endswith((".jpg", ".jpeg")):
                mime_type = "image/jpeg"
            elif file.filename.lower().endswith(".png"):
                mime_type = "image/png"

        # 1. Extração IA
        resultado_json_str = await extrair_lista_presenca(content, mime_type)
        
        try:
             dados = json.loads(resultado_json_str)
             if "erro" in dados:
                 raise HTTPException(status_code=500, detail=dados.get("erro"))

             beneficiarios_detectados = dados.get("beneficiarios_detectados", [])
             
             # 2. Lógica de Match (Detetive)
             cursor = db.cursor()
             
             for item in beneficiarios_detectados:
                 item['encontrado'] = False
                 item['id_beneficiario'] = None
                 item['match_type'] = None
                 
                 nome_busca = item.get('nome_extraido')
                 cpf_busca = item.get('cpf_extraido')
                 
                 # A. Tentativa por CPF
                 if cpf_busca:
                     cpf_limpo = "".join(filter(str.isdigit, cpf_busca))
                     if len(cpf_limpo) > 5: # Mínimo para ser válido tentar
                         # Tenta nas colunas cpf_familiar e cpf_tecnico
                         # LIKE para suportar se no banco estiver com/sem pontuação diferente
                         cursor.execute("""
                            SELECT id, nome_familiar, nome_tecnico, cpf_familiar, cpf_tecnico 
                            FROM beneficiarios 
                            WHERE REPLACE(REPLACE(REPLACE(cpf_familiar, '.', ''), '-', ''), ' ', '') = ?
                            OR REPLACE(REPLACE(REPLACE(cpf_tecnico, '.', ''), '-', ''), ' ', '') = ?
                         """, (cpf_limpo, cpf_limpo))
                         found = cursor.fetchone()
                         if found:
                             item['encontrado'] = True
                             item['id_beneficiario'] = found['id']
                             item['match_type'] = 'CPF'
                             item['nome_banco'] = found['nome_familiar'] or found['nome_tecnico']
                             continue # Achou, pula pro próximo

                 # B. Tentativa por Nome (LIKE)
                 if nome_busca and len(nome_busca) > 4:
                     # Busca simples por contem
                     cursor.execute("""
                        SELECT id, nome_familiar, nome_tecnico 
                        FROM beneficiarios 
                        WHERE nome_familiar LIKE ? OR nome_tecnico LIKE ?
                     """, (f"%{nome_busca}%", f"%{nome_busca}%"))
                     found = cursor.fetchone()
                     
                     if found:
                         item['encontrado'] = True
                         item['id_beneficiario'] = found['id']
                         item['match_type'] = 'NOME'
                         item['nome_banco'] = found['nome_familiar'] or found['nome_tecnico']
             
             return dados

        except json.JSONDecodeError:
             return {"erro": "Falha ao decodificar resposta da IA", "raw": resultado_json_str}

    except Exception as e:
        logger.error(f"Erro no scan GRH: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro no processamento: {str(e)}")

# --- Schema Interno para Vinculação ---
from pydantic import BaseModel  # noqa: E402
from typing import List  # noqa: E402

class VinculoGRH(BaseModel):
    termo_grh: str
    ids_beneficiarios: List[int]

from app.services.backup_service import create_snapshot  # noqa: E402
from app.services.audit_service import log_change  # noqa: E402

@router.post("/vincular")
def vincular_grh_lote(
    dados: VinculoGRH,
    db: sqlite3.Connection = Depends(get_db_connection)
):
    """
    Vincula um termo GRH (ex: 'GRH 01') a múltiplos beneficiários.
    
    - Cria Snapshot de Backup antes da alteração.
    - Atualiza campo 'grh' para cada ID fornecido.
    - Registra Log de Auditoria para cada update.
    """
    if not dados.ids_beneficiarios:
         return {"mensagem": "Nenhum beneficiário para vincular."}

    try:
        # 1. Create System Snapshot
        try:
            create_snapshot(reason=f"grh_lote_{dados.termo_grh}")
        except Exception as e:
            logger.warning(f"Failed to create snapshot, but proceeding: {e}")

        cursor = db.cursor()
        
        # 2. Update with Audit Logging
        updates_count = 0
        
        for p_id in dados.ids_beneficiarios:
            # Fetch old value
            cursor.execute("SELECT id, grh FROM beneficiarios WHERE id = ?", (p_id,))
            row = cursor.fetchone()
            
            if row:
                old_val = {"grh": row['grh']}
                
                # Update
                cursor.execute("UPDATE beneficiarios SET grh = ? WHERE id = ?", (dados.termo_grh, p_id))
                
                # Log Change
                new_val = {"grh": dados.termo_grh}
                log_change(
                    db=db,
                    tabela="beneficiarios",
                    registro_id=p_id,
                    operacao="UPDATE",
                    valor_antigo=old_val,
                    valor_novo=new_val,
                    detalhes=f"Vinculação em lote GRH: {dados.termo_grh}"
                )
                updates_count += 1

        db.commit()
        
        return {
            "mensagem": "Vinculação realizada com sucesso!",
            "afetados": updates_count
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao vincular GRH: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao salvar vínculo: {e}")

# --- Schema para Busca Manual ---

class BuscaManual(BaseModel):
    nome: str
    cpf: str = None

@router.post("/match-manual")
def buscar_beneficiario_manual(
    dados: BuscaManual,
    db: sqlite3.Connection = Depends(get_db_connection)
):
    """
    Busca um beneficiário manualmente por Nome (Fuzzy) ou CPF (Exato).
    Retorna o melhor candidato ou 404.
    """
    try:
        cursor = db.cursor()
        
        # 1. Prioridade: CPF Exato
        if dados.cpf:
            cpf_limpo = "".join(filter(str.isdigit, dados.cpf))
            if len(cpf_limpo) > 5:
                 cursor.execute("""
                    SELECT id, nome_familiar, nome_tecnico, cpf_familiar, cpf_tecnico 
                    FROM beneficiarios 
                    WHERE REPLACE(REPLACE(REPLACE(cpf_familiar, '.', ''), '-', ''), ' ', '') = ?
                    OR REPLACE(REPLACE(REPLACE(cpf_tecnico, '.', ''), '-', ''), ' ', '') = ?
                 """, (cpf_limpo, cpf_limpo))
                 found = cursor.fetchone()
                 if found:
                     return {
                         "encontrado": True,
                         "id": found['id'],
                         "nome": found['nome_familiar'] or found['nome_tecnico'],
                         "cpf": found['cpf_familiar'] or found['cpf_tecnico'],
                         "match_type": "CPF_MANUAL"
                     }

        # 2. Prioridade: Nome (Fuzzy / Like)
        if dados.nome and len(dados.nome) > 2:
            # Normalização simples: Remove acentos e upper case
            # SQLite padrão não tem 'unaccent', então fazemos LIKE com %.
            # Idealmente, a aplicação deve salvar uma coluna 'nome_normalizado' no banco.
            # Como fallback, vamos tentar LIKE direto.
            
            nome_busca = dados.nome.strip()
            
            # Tenta busca exata (LIKE) primeiro
            cursor.execute("""
                SELECT id, nome_familiar, nome_tecnico, cpf_familiar 
                FROM beneficiarios 
                WHERE nome_familiar LIKE ? OR nome_tecnico LIKE ?
            """, (f"%{nome_busca}%", f"%{nome_busca}%"))
            found = cursor.fetchone()
            
            if not found:
                # Tenta busca parcial (primeiro nome) se falhou
                primeiro_nome = nome_busca.split()[0]
                if len(primeiro_nome) > 3:
                     cursor.execute("""
                        SELECT id, nome_familiar, nome_tecnico, cpf_familiar 
                        FROM beneficiarios 
                        WHERE nome_familiar LIKE ? OR nome_tecnico LIKE ?
                    """, (f"%{primeiro_nome}%", f"%{primeiro_nome}%"))
                     found = cursor.fetchone()

            if found:
                 return {
                     "encontrado": True,
                     "id": found['id'],
                     "nome": found['nome_familiar'] or found['nome_tecnico'],
                     "cpf": found['cpf_familiar'],
                     "match_type": "NOME_MANUAL"
                 }

        return {"encontrado": False, "mensagem": "Nenhum beneficiário encontrado."}

    except Exception as e:
        logger.error(f"Erro na busca manual: {e}")
        raise HTTPException(status_code=500, detail="Erro interno na busca.")

@router.get("/documento/{filename}")
def download_grh_documento(filename: str):
    """
    Retorna o arquivo físico da pasta GRH para download/visualização.
    """
    file_path = settings.GRH_FOLDER / filename
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    return FileResponse(file_path)
