import os
import time
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse, RedirectResponse
from app.core.database import get_supabase, fetch_all, db_insert, db_delete

router = APIRouter(prefix="/api/p1-2/documentos", tags=["P1+2 - Documentos"])
logger = logging.getLogger(__name__)

UPLOAD_DIR = os.path.join(os.getcwd(), "app", "static", "uploads", "p12")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("")
async def listar_documentos(categoria: Optional[str] = None):
    try:
        docs = fetch_all("p12_documentos")
        if categoria and categoria != "TODOS":
            docs = [d for d in docs if str(d.get("categoria") or "").lower() == categoria.lower()]
        docs.sort(key=lambda x: x.get("id", 0), reverse=True)
        return {"total": len(docs), "dados": docs}
    except Exception as e:
        logger.error(f"Erro ao listar documentos P1+2: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")

@router.get("/download/{id}")
async def baixar_documento(id: int):
    try:
        docs = fetch_all("p12_documentos")
        doc = next((d for d in docs if d.get("id") == id), None)
        if not doc:
            raise HTTPException(status_code=404, detail="Documento não encontrado.")
        
        caminho = doc.get("caminho_arquivo") or ""
        nome_arquivo = doc.get("nome_arquivo") or "documento.pdf"
        
        # Se for arquivo local
        if caminho.startswith("/static/"):
            rel_path = caminho.lstrip("/")
            full_path = os.path.join(os.getcwd(), "app", rel_path.replace("static/", "static" + os.sep))
            if os.path.exists(full_path):
                return FileResponse(full_path, filename=nome_arquivo)
        
        # Se arquivo salvo na pasta UPLOAD_DIR
        local_direct = os.path.join(UPLOAD_DIR, os.path.basename(caminho))
        if os.path.exists(local_direct):
            return FileResponse(local_direct, filename=nome_arquivo)
            
        # Se for URL externa válida (Supabase/S3)
        if caminho.startswith("http://") or caminho.startswith("https://"):
            return RedirectResponse(url=caminho)
            
        raise HTTPException(status_code=404, detail="Arquivo físico não encontrado no servidor.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao baixar documento: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao baixar: {e}")

@router.post("", status_code=201)
async def upload_documento(
    nome_documento: str = Form(...),
    categoria: str = Form("Geral"),
    file: UploadFile = File(...)
):
    try:
        content = await file.read()
        safe_name = "".join(c for c in file.filename if c.isalnum() or c in "._- ")
        filename = f"p12_{int(time.time())}_{safe_name}"
        
        # 1. Salva localmente em disco garantindo persistência imediata
        local_file_path = os.path.join(UPLOAD_DIR, filename)
        with open(local_file_path, "wb") as f:
            f.write(content)
            
        # URL de acesso direto e estável
        file_path = f"/static/uploads/p12/{filename}"
        
        # 2. Tenta espelhar no Supabase Storage se disponível
        try:
            supabase = get_supabase()
            supabase.storage.from_("agendha-uploads").upload(f"uploads/p12/{filename}", content)
            file_path = supabase.storage.from_("agendha-uploads").get_public_url(f"uploads/p12/{filename}")
        except Exception:
            # Fallback seguro para o arquivo local
            file_path = f"/static/uploads/p12/{filename}"
            
        doc_data = {
            "nome_documento": nome_documento,
            "categoria": categoria,
            "nome_arquivo": file.filename,
            "caminho_arquivo": file_path,
            "tamanho_bytes": len(content)
        }
        novo = db_insert("p12_documentos", doc_data)
        return {"message": "Documento enviado com sucesso!", "dados": novo}
    except Exception as e:
        logger.error(f"Erro ao enviar documento P1+2: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no upload: {e}")

@router.delete("/{id}")
async def excluir_documento(id: int):
    try:
        db_delete("p12_documentos", id)
        return {"message": "Documento excluído com sucesso!"}
    except Exception as e:
        logger.error(f"Erro ao excluir documento: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao excluir: {e}")