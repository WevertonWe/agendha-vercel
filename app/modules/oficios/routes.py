from fastapi import APIRouter, Request, Form, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
import shutil
from app.config import settings
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from app.modules.oficios import services

router = APIRouter(prefix="/oficios", tags=["Ofícios"])
from jinja2 import Environment, FileSystemLoader
_env = Environment(loader=FileSystemLoader("app/templates"), cache_size=0)
templates = Jinja2Templates(env=_env)

def date_br_filter(value):
    if not value:
        return ""
    try:
        if isinstance(value, str):
            date_obj = datetime.strptime(value, '%Y-%m-%d')
            return date_obj.strftime('%d/%m/%Y')
        return value.strftime('%d/%m/%Y')
    except:  # noqa: E722
        return value

templates.env.filters['date_br'] = date_br_filter

class OficioUpdate(BaseModel):
    numero_oficio: Optional[str] = None
    destinatario: Optional[str] = None
    data_envio: Optional[str] = None
    motivo_descricao: Optional[str] = None

@router.get("/", response_class=HTMLResponse)
async def list_oficios(request: Request):
    oficios = services.get_all_oficios()
    return templates.TemplateResponse("admin/oficios.html", {"request": request, "oficios": oficios})

@router.get("/download/{filename}")
async def download_file(filename: str):
    file_path = settings.UPLOAD_FOLDER / "oficios" / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    return FileResponse(file_path)

@router.post("/", response_class=HTMLResponse)
async def create_oficio(
    request: Request,
    destinatario: str = Form(...),
    data_envio: str = Form(...),
    motivo_descricao: str = Form(...),
    numero_oficio: str = Form(None),
    arquivo: UploadFile = File(None)
):
    # Tenta pegar o usuário do cookie para 'criado_por'
    criado_por = "Desconhecido"
    token = request.cookies.get("access_token")
    if token:
        try:
            if token.startswith(f"{settings.AUTH_BEARER_PREFIX} "):
                token = token.split(" ")[1]
            from jose import jwt
            from app.core.auth.utils import SECRET_KEY, ALGORITHM
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            criado_por = payload.get("sub", "Desconhecido")
        except:  # noqa: E722
            pass

    caminho_arquivo = None
    if arquivo and arquivo.filename:
        upload_dir = settings.UPLOAD_FOLDER / "oficios"
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Safe filename
        safe_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{arquivo.filename}"
        file_path = upload_dir / safe_filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(arquivo.file, buffer)
            
        caminho_arquivo = safe_filename

    dados = {
        "numero_oficio": numero_oficio,
        "destinatario": destinatario,
        "data_envio": data_envio,
        "motivo_descricao": motivo_descricao,
        "criado_por": criado_por,
        "caminho_arquivo": caminho_arquivo
    }
    
    services.create_oficio(None, dados)
    
    return RedirectResponse(url="/oficios", status_code=303)

@router.put("/{oficio_id}")
async def update_oficio_endpoint(
    oficio_id: int,
    destinatario: Optional[str] = Form(None),
    data_envio: Optional[str] = Form(None),
    motivo_descricao: Optional[str] = Form(None),
    numero_oficio: Optional[str] = Form(None),
    arquivo: UploadFile = File(None)
):
    dados = {}
    if destinatario is not None:
        dados["destinatario"] = destinatario
    if data_envio is not None:
        dados["data_envio"] = data_envio
    if motivo_descricao is not None:
        dados["motivo_descricao"] = motivo_descricao
    if numero_oficio is not None:
        dados["numero_oficio"] = numero_oficio

    if arquivo and arquivo.filename:
        upload_dir = settings.UPLOAD_FOLDER / "oficios"
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Safe filename
        safe_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{arquivo.filename}"
        file_path = upload_dir / safe_filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(arquivo.file, buffer)
            
        dados["caminho_arquivo"] = safe_filename

    sucesso = services.update_oficio(None, oficio_id, dados)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Ofício não encontrado")
    return {"message": "Ofício atualizado com sucesso"}

@router.delete("/{oficio_id}")
async def delete_oficio_endpoint(
    oficio_id: int
):
    sucesso = services.delete_oficio(None, oficio_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Ofício não encontrado")
    return {"message": "Ofício excluído com sucesso"}
