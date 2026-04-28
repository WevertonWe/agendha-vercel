from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.config import settings
from app.core.database import get_db_connection as get_db
from datetime import datetime
import logging

router = APIRouter(prefix="/projetos", tags=["Projetos"])
from jinja2 import Environment, FileSystemLoader
_env = Environment(loader=FileSystemLoader("app/templates"), cache_size=0)
templates = Jinja2Templates(env=_env)

# Mapping slugs to display names
PROJECTS_INFO = {
    "ater-biomas-ca-13": "ATER BIOMAS CA 13 (Itaparica)",
    "ater-biomas-ca-24": "ATER BIOMAS CA 24 (Semiárido NII)",
    "ap1mc": "AP1MC (Tecnologia de Acesso à Água)",
    "pnud": "PNUD (Plantas Medicinais)",
    "ater-bahia-sem-fome": "ATER BAHIA SEM FOME",
    "seades": "SEADES (Cisternas)"
}

@router.get("/{projeto_slug}", response_class=HTMLResponse)
async def get_projeto_page(request: Request, projeto_slug: str):
    username = "Anônimo"
    token = request.cookies.get("access_token")
    if token:
        try:
            if token.startswith("Bearer "):
                token = token.split(" ")[1]
            from app.core.auth.utils import SECRET_KEY, ALGORITHM
            from jose import jwt
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub", "Anônimo")
        except:  # noqa: E722
            pass

    project_name = PROJECTS_INFO.get(projeto_slug, "Projeto Desconhecido")
    
    return templates.TemplateResponse("projetos/projeto_base.html", {
        "request": request,
        "projeto_slug": projeto_slug,
        "projeto_name": project_name,
        "user_username": username
    })

@router.get("/admin/sugestoes", response_class=HTMLResponse)
async def ver_sugestoes(request: Request, db = Depends(get_db)):
    # Add proper auth check here (Admin only ideally)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM sugestoes_projetos ORDER BY data_criacao DESC")
    rows = cursor.fetchall()
    
    return templates.TemplateResponse("projetos/lista_sugestoes.html", {
        "request": request,
        "sugestoes": rows
    })

@router.post("/api/sugestao")
async def salvar_sugestao(
    projeto_id: str = Form(...),
    usuario_id: str = Form(...),
    sugestao: str = Form(...),
    db = Depends(get_db)
):
    try:
        cursor = db.cursor()
        data_criacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            INSERT INTO sugestoes_projetos (projeto_id, usuario_id, sugestao, data_criacao)
            VALUES (?, ?, ?, ?)
        """, (projeto_id, usuario_id, sugestao, data_criacao))
        
        db.commit()
        
        return JSONResponse(content={"message": "Sugestão enviada com sucesso!", "id": cursor.lastrowid})
    except Exception as e:
        logging.error(f"Erro ao salvar sugestão: {e}")
        return JSONResponse(content={"error": "Erro ao processar sugestão."}, status_code=500)

@router.delete("/api/sugestao/{id}")
async def deletar_sugestao(id: int, db = Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("DELETE FROM sugestoes_projetos WHERE id = ?", (id,))
        db.commit()
        return JSONResponse(content={"message": "Sugestão excluída."})
    except Exception as e:
        logging.error(f"Erro ao excluir sugestão: {e}")
        return JSONResponse(content={"error": "Erro ao excluir."}, status_code=500)

@router.put("/api/sugestao/{id}")
async def atualizar_sugestao(id: int, request: Request, db = Depends(get_db)):
    try:
        data = await request.json()
        novo_texto = data.get("sugestao")
        
        if not novo_texto:
            return JSONResponse(content={"error": "Texto inválido"}, status_code=400)
            
        cursor = db.cursor()
        cursor.execute("UPDATE sugestoes_projetos SET sugestao = ? WHERE id = ?", (novo_texto, id))
        db.commit()
        return JSONResponse(content={"message": "Sugestão atualizada."})
    except Exception as e:
        logging.error(f"Erro ao atualizar sugestão: {e}")
        return JSONResponse(content={"error": "Erro ao atualizar."}, status_code=500)
