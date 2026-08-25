from fastapi import APIRouter, Request, HTTPException, Query, Body
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader
import os
import glob
import logging

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

_env = Environment(loader=FileSystemLoader("app/templates"), cache_size=0)
templates = Jinja2Templates(env=_env)
router = APIRouter(tags=["Ferramentas"])


@router.get("/ferramentas/pdf-rotator", response_class=HTMLResponse, summary="Ferramenta para Rotacionar PDFs")
async def get_pdf_rotator_page(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="ferramentas/pdf_rotator.html", 
        context={"request": request, "current_page": "pdf_rotator"}
    )


@router.get("/api/ferramentas/pdf-list", summary="Lista arquivos PDF em um diretório")
async def list_pdfs(folder_path: str = Query(..., description="Caminho absoluto da pasta")):
    if not os.path.exists(folder_path):
        return JSONResponse(status_code=400, content={"status": "error", "message": "O caminho especificado não existe."})
    if not os.path.isdir(folder_path):
        return JSONResponse(status_code=400, content={"status": "error", "message": "O caminho especificado não é uma pasta."})
    
    try:
        # Pega arquivos .pdf recursivamente
        pdf_files = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(".pdf"):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, folder_path)
                    pdf_files.append({
                        "filename": file,
                        "rel_path": rel_path,
                        "filepath": full_path,
                        "size": os.path.getsize(full_path)
                    })
        
        # Sort by relative path to keep folders grouped
        pdf_files.sort(key=lambda x: x["rel_path"].lower())
        
        return {"status": "success", "files": pdf_files}
    except Exception as e:
        logging.error(f"Erro ao listar PDFs na pasta {folder_path}: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": f"Erro ao acessar a pasta: {str(e)}"})


@router.get("/api/ferramentas/pdf-view", summary="Visualiza um arquivo PDF específico")
async def view_pdf(filepath: str = Query(..., description="Caminho absoluto do arquivo PDF")):
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.")
    if not filepath.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="O arquivo não é um PDF válido.")
    
    # We add headers to prevent caching issues if we rotate it
    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
    }
    return FileResponse(filepath, media_type="application/pdf", headers=headers)


@router.post("/api/ferramentas/pdf-rotate", summary="Rotaciona e salva um arquivo PDF")
async def rotate_pdf(payload: dict = Body(...)):
    if fitz is None:
        return JSONResponse(status_code=500, content={"status": "error", "message": "A biblioteca PyMuPDF (fitz) não está instalada no servidor."})
        
    filepath = payload.get("filepath")
    angle = payload.get("angle", 90)
    
    if not filepath or not os.path.exists(filepath):
        return JSONResponse(status_code=404, content={"status": "error", "message": "Arquivo não encontrado."})
    if not filepath.lower().endswith(".pdf"):
        return JSONResponse(status_code=400, content={"status": "error", "message": "Somente arquivos PDF podem ser rotacionados."})
    
    try:
        angle = int(angle)
        
        doc = fitz.open(filepath)
        temp_path = filepath + ".tmp"
        for page in doc:
            current_rotation = page.rotation
            new_rotation = (current_rotation + angle) % 360
            page.set_rotation(new_rotation)
            
        doc.save(temp_path)
        doc.close()
        
        os.replace(temp_path, filepath)
        
        return {"status": "success", "message": f"PDF rotacionado em {angle}° com sucesso!"}
    except Exception as e:
        logging.error(f"Erro ao rotacionar PDF {filepath}: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": f"Falha ao rotacionar PDF: {str(e)}"})
