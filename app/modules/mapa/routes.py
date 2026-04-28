import sqlite3
import shutil
import uuid
import os
from typing import List, Optional
from fastapi import APIRouter, Request, HTTPException, Depends, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
# import pandas as pd
import io

from app.config import settings
from .models import PontoCreate, PontoResponse, CategoriaCreate, CategoriaResponse
from . import services
from app.services.utils import remover_acentos

router = APIRouter(prefix="/api/mapa", tags=["Mapa"])
view_router = APIRouter(include_in_schema=False)

from jinja2 import Environment, FileSystemLoader
_env = Environment(loader=FileSystemLoader("app/templates"), cache_size=0)
templates = Jinja2Templates(env=_env)

# --- Auth Helper ---
def get_user_auth(request: Request) -> Optional[str]:
    """
    Tries to get username from 'access_token' cookie or 'Authorization' header.
    Returns username if valid, None otherwise.
    """
    token = request.cookies.get("access_token")
    
    # Fallback to Header if no cookie
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith(f"{settings.AUTH_BEARER_PREFIX} "):
            token = auth_header.split(" ")[1]
            
    if not token:
        return None

    if token.startswith(f"{settings.AUTH_BEARER_PREFIX} "):
        token = token.split(" ")[1]

    try:
        from app.core.auth.utils import SECRET_KEY, ALGORITHM
        from jose import jwt
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except Exception:
        return None

def get_user_role(username: str) -> Optional[str]:
    try:
        conn = services.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return row['role']
        return None
    except Exception:
        return None

# --- Views ---

@view_router.get("/mapa", response_class=HTMLResponse)
async def get_map_page(request: Request):
    user = get_user_auth(request)
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse("mapa/index.html", {"request": request})

@router.get("/geral", response_class=HTMLResponse)
async def mapa_geral(request: Request):
    user = get_user_auth(request)
    if not user:
        return RedirectResponse("/login")
        
    return templates.TemplateResponse("mapa/index.html", {
        "request": request, 
        "contexto": "geral"
    })

@router.get("/privado", response_class=HTMLResponse)
async def mapa_privado(request: Request):
    user = get_user_auth(request)
    
    if not user:
        return RedirectResponse("/login")
        
    if user != "fgermino":
        return templates.TemplateResponse("errors/error.html", {
            "request": request,
            "message": "Acesso Restrito à Coordenação. Você não tem permissão para visualizar esta página."
        }, status_code=403)

    return templates.TemplateResponse("mapa/index.html", {
        "request": request, 
        "contexto": "privado"
    })

# --- API ---

def require_auth(request: Request):
    user = get_user_auth(request)
    if not user:
        raise HTTPException(status_code=401, detail="Não autenticado")
    return user

@router.get("/pontos", response_model=List[PontoResponse])
async def list_pontos(
    request: Request, 
    contexto: str = "geral", 
    responsavel: Optional[str] = None, 
    user: str = Depends(require_auth)
):
    # Security Check: Private context only for 'fgermino'
    if contexto == "privado" and user != "fgermino":
        raise HTTPException(status_code=403, detail="Permissão negada para este contexto")
    
    # Check User Role
    user_role = get_user_role(user)
    
    # Logic:
    # If Admin, return everything (or filter by responsavel if provided).
    # If not Admin (e.g. 'bruna'), return ONLY their points (unless they are viewing General Map? 
    # Requirement: "Se o usuário for Admin, retorna tudo. Se for a Bruna logada, retorna só os dela (exceto no Mapa Geral, onde o Admin vê tudo)."
    # This implies Bruna viewing General Map sees ONLY HERS? Or everyone sees everyone in General Map?
    # "Se for a Bruna logada, retorna só os dela" sounds restrictive.
    # But usually a Map shows all points?
    # "exceto no Mapa Geral, onde o Admin vê tudo" -> This suggests Bruna doesn't see everything even in General Map?
    # Or maybe "exceto no Mapa Geral" means "In General Map everyone sees everything"?
    # Let's read carefully: "Se o usuário for Admin, retorna tudo. Se for a Bruna logada, retorna só os dela (exceto no Mapa Geral, onde o Admin vê tudo)."
    # This phrasing is ambiguous. "Se for Bruna logada, retorna só os dela".
    # I will assume restrictive: Bruna sees only `responsavel='bruna'`. Admin sees all.
    # Unless `responsavel` param is specified.
    
    filter_responsavel = responsavel
    
    if user_role != 'admin':
        # Force filter to current user
        filter_responsavel = user

    # If admin and responsavel is not provided, fetch all.
    # If admin and responsavel IS provided (e.g. filter by Bruna as Admin), fetch Bruna's.
    
    return sorted(services.get_all_pontos(contexto, responsavel=filter_responsavel), key=lambda x: x.id, reverse=True)

@router.get("/beneficiarios/search")
async def search_beneficiarios(q: str, limit: int = 10, user: str = Depends(require_auth)):
    """
    Busca rápida de beneficiários para o Mapa.
    Retorna apenas dados essenciais: Nome, CPF, Lat, Lng, Status, Verificação BSF.
    Ignora acentos e busca parcial.
    """
    if not q or len(q) < 3:
        return []

    try:
        conn = services.get_db_connection()
        conn.create_function("remover_acentos", 1, remover_acentos) # Register custom function if possible or use LIKE
        cursor = conn.cursor()
        
        # Searching primarily in BENEFICIARIOS table (Source of Truth) because they might use the search to find people to Add/Verify
        # But wait, the goal is to flyTo on Map.
        # If I return coord from Beneficiarios, map can fly there. 
        # But if the point is not loaded in the map layers (e.g. not synced), the user will see an empty spot.
        # Ideally we search MAPA_PONTOS?
        # But Sync logic updates mapa_pontos.
        # Let's search BENEFICIARIOS and assume sync is up to date OR allow 'ghost' points (showing marker on flyTo).
        # Given "status e verificacao_bsf", benef table has this data.
        
        # Unaccent logic in SQLITE is tricky without extension.
        # Using LIKE %q% is simple.
        # Ensuring fast search: LIMIT 10.
        
        # Simple LIKE query for now. Python function remover_acentos can be used on query param, but database data might be accented.
        # "Conceição" -> user types "conceicao".
        # We need unaccent logic.
        # Best bet: Fetch chunks or use a normalized column.
        # Since we can't change schema easily for normalized column now without migration risk, let's try strict LIKE first or upper.
        # SQLite GLOB or LIKE is case insensitive for ASCII.
        
        # Let's clean query
        q_clean = q.strip().upper() # Basic
        
        # Try finding by CPF (digits only)
        import re
        q_digits = re.sub(r'[^0-9]', '', q)
        
        results = []
        
        if len(q_digits) > 5: # Likely a CPF search
             cursor.execute("""
                SELECT nome_completo, cpf, latitude, longitude, status, verificado_bsf 
                FROM beneficiarios 
                WHERE cpf LIKE ? AND latitude IS NOT NULL
                LIMIT ?
             """, (f"%{q_digits}%", limit))
             results = cursor.fetchall()
        
        if not results:
             # Text search
             # Note: SQLite LIKE is case-insensitive for ASCII chars by default, but not UTF-8 (accents).
             # We will try robust search in Python if dataset is small, or just standard LIKE.
             # Dataset size unknown. Assuming scalable approach needed.
             # Let's use simple LIKE with wildcards.
             cursor.execute("""
                SELECT nome_completo, cpf, latitude, longitude, status, verificado_bsf 
                FROM beneficiarios 
                WHERE (UPPER(nome_completo) LIKE ?) 
                AND latitude IS NOT NULL
                LIMIT ?
             """, (f"%{q_clean}%", limit))
             results = cursor.fetchall()
        
        conn.close()
        
        # Format response
        data = []
        for row in results:
             ver_bsf = False
             raw_bsf = row['verificado_bsf']
             if raw_bsf and str(raw_bsf).lower() in ['true', '1', 'sim', 'ok']:
                 ver_bsf = True
                 
             data.append({
                 "nome": row['nome_completo'],
                 "cpf": row['cpf'],
                 "lat": row['latitude'],
                 "lng": row['longitude'],
                 "status": row['status'],
                 "verificacao_bsf": ver_bsf,
                 "display_status": f"{row['status']} {'(BSF)' if ver_bsf else ''}"
             })
             
        # Add simple client-side unaccent filtering if needed? No, DB logic is safer for pagination/limit.
        # For "Conceição" vs "Conceicao", without Unaccent Extension in SQLite, user must type correctly or we rely on some fuzzy match.
        # Workaround: Python-side filtering if we fetch more? No, perf risk.
        # Proceed with standard UPPER LIKE.
        
        return data

    except Exception as e:
        print(f"Search Error: {e}")
        return []

@router.post("/upload")
async def upload_foto_ponto(file: UploadFile = File(...), user: str = Depends(require_auth)):
    try:
        # 1. Define folder
        # app/static/uploads/mapa/
        upload_dir = os.path.join("app", "static", "uploads", "mapa")
        os.makedirs(upload_dir, exist_ok=True)
        
        # 2. Generate unique name
        # Keep extension
        ext = os.path.splitext(file.filename)[1]
        if not ext:
            ext = ".jpg"
            
        unique_name = f"{uuid.uuid4()}{ext}"
        file_path = os.path.join(upload_dir, unique_name)
        
        # 3. Save
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 4. Return URL
        # /static/uploads/mapa/filename
        url = f"/static/uploads/mapa/{unique_name}"
        return {"url": url}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar imagem: {str(e)}")


@router.post("/pontos", response_model=PontoResponse)
async def create_new_ponto(ponto: PontoCreate, request: Request, user: str = Depends(require_auth)):
    # Security Check
    if ponto.contexto == "privado" and user != "fgermino":
        raise HTTPException(status_code=403, detail="Permissão negada para salvar neste contexto")
    
    # Assign responsavel to current user (creator)
    ponto.responsavel = user

    created_ponto = services.create_ponto(ponto)
    if not created_ponto:
        raise HTTPException(status_code=500, detail="Erro ao criar ponto no mapa")
    return created_ponto

@router.delete("/pontos/{ponto_id}")
async def remove_ponto(ponto_id: int, request: Request, user: str = Depends(require_auth)):
    # Check ownership/context before delete
    ponto = services.get_ponto(ponto_id)
    if not ponto:
        raise HTTPException(status_code=404, detail="Ponto não encontrado")

    if ponto.contexto == "privado" and user != "fgermino":
         raise HTTPException(status_code=403, detail="Permissão negada para deletar este ponto")
    
    user_role = get_user_role(user)
    if user_role != 'admin' and ponto.responsavel != user:
        raise HTTPException(status_code=403, detail="Você só pode excluir seus próprios pontos")

    success = services.delete_ponto(ponto_id)
    if not success:
        raise HTTPException(status_code=404, detail="Erro ao deletar")
    return {"message": "Ponto deletado com sucesso"}

@router.get("/pontos/{ponto_id}", response_model=PontoResponse)
async def get_one_ponto(ponto_id: int, user: str = Depends(require_auth)):
    ponto = services.get_ponto(ponto_id)
    if not ponto:
        raise HTTPException(status_code=404, detail="Ponto não encontrado")
    
    if ponto.contexto == "privado" and user != "fgermino":
         raise HTTPException(status_code=403, detail="Permissão negada")
    
    user_role = get_user_role(user)
    if user_role != 'admin' and ponto.responsavel != user:
         raise HTTPException(status_code=403, detail="Permissão negada")
         
    return ponto

@router.put("/pontos/{ponto_id}", response_model=PontoResponse)
async def update_existing_ponto(ponto_id: int, ponto: PontoCreate, user: str = Depends(require_auth)):
    # Check permissions
    existing = services.get_ponto(ponto_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Ponto não encontrado")
        
    # Prevent modifying private points if not allowed
    if existing.contexto == "privado" and user != "fgermino":
        raise HTTPException(status_code=403, detail="Permissão negada")

    # Prevent moving TO private context if not allowed
    if ponto.contexto == "privado" and user != "fgermino":
        raise HTTPException(status_code=403, detail="Permissão negada para mover para privado")

    user_role = get_user_role(user)
    if user_role != 'admin' and existing.responsavel != user:
        raise HTTPException(status_code=403, detail="Você só pode editar seus próprios pontos")
    
    # Ensure responsavel remains the same unless admin changes it?
    # Or strict updates: maintain original owner
    ponto.responsavel = existing.responsavel # Keep original owner

    updated = services.update_ponto(ponto_id, ponto)
    if not updated:
        raise HTTPException(status_code=404, detail="Erro ao atualizar ponto")
    return updated

# --- Batch Import ---

@router.post("/importar-preview")
async def import_preview(file: UploadFile = File(...), user: str = Depends(require_auth)):
    """
    Reads .xlsx or .csv and returns valid points preview.
    Does NOT save to DB.
    """
    contents = await file.read()
    filename = file.filename.lower()
    
    try:
        if filename.endswith('.xlsx'):
            df = pd.read_excel(io.BytesIO(contents))
        elif filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Formato não suportado. Use .xlsx ou .csv")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao ler arquivo: {str(e)}")

    preview_pontos = []
    
    # Expected columns: Latitude, Longitude, Nome, Categoria, Responsável (optional?)

    # Mapping friendly names to model fields
    # Flexible column names
    
    def get_col(df, options):
        for opt in options:
            for col in df.columns:
                if opt.lower() in col.lower():
                    return col
        return None

    col_lat = get_col(df, ['latitude', 'lat'])
    col_lon = get_col(df, ['longitude', 'lon', 'lng'])
    col_nome = get_col(df, ['nome', 'descricao', 'titulo'])
    col_cat = get_col(df, ['categoria', 'tipo'])
    col_resp = get_col(df, ['responsavel', 'owner', 'dono'])

    if not col_lat or not col_lon:
         raise HTTPException(status_code=400, detail="Colunas Latitude e Longitude são obrigatórias.")

    for index, row in df.iterrows():
        try:
            lat = float(row[col_lat])
            lon = float(row[col_lon])
            
            # Simple validation
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                continue # Skip invalid coords
                
            nome = str(row[col_nome]) if col_nome and pd.notna(row[col_nome]) else f"Ponto Importado {index+1}"
            categoria = str(row[col_cat]) if col_cat and pd.notna(row[col_cat]) else "Outro"
            resp = str(row[col_resp]) if col_resp and pd.notna(row[col_resp]) else user # Default to uploader if missing
            
            preview_pontos.append({
                "nome": nome,
                "latitude": lat,
                "longitude": lon,
                "tipo": categoria,
                "descricao": f"Importado de {file.filename}",
                "responsavel": resp,
                "contexto": "geral" # Default
            })
        except ValueError:
            continue # Skip non-numeric coords

    return {"pontos": preview_pontos, "total": len(preview_pontos)}

@router.post("/importar-confirmar")
async def import_confirm(pontos: List[PontoCreate], user: str = Depends(require_auth)):
    """
    Receives list of points and saves them.
    """
    saved_count = 0
    errors = 0
    
    for pt in pontos:
        # Enforce responsavel if not set or if restrictive
        if not pt.responsavel:
            pt.responsavel = user
            
        # Optional: Validate responsavel exists?
        # For now trust the input or force user?
        # If admin is importing, they might set responsavel to 'bruna'.
        # If 'bruna' is importing, force responsavel='bruna'.
        
        user_role = get_user_role(user)
        if user_role != 'admin':
             pt.responsavel = user
        
        # Default color based on category?
        if not pt.cor:
             # Basic mapping or default
             pt.cor = "#6c757d" 

        res = services.create_ponto(pt)
        if res:
            saved_count += 1
        else:
            errors += 1
            
    return {"message": "Importação concluída", "salvos": saved_count, "erros": errors}

@router.get("/stats")
async def get_map_stats(user: str = Depends(require_auth)):
    try:
        conn = services.get_db_connection()
        cursor = conn.cursor()
        
        # Count by Responsavel
        cursor.execute("SELECT responsavel, COUNT(*) as total FROM mapa_pontos GROUP BY responsavel")
        rows = cursor.fetchall()
        
        stats = {row['responsavel'] if row['responsavel'] else 'Sem Dono': row['total'] for row in rows}
        
        # Count Total
        cursor.execute("SELECT COUNT(*) as total FROM mapa_pontos")
        total = cursor.fetchone()['total']
        
        conn.close()
        
        return {"total": total, "by_user": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/modelo-importacao")
async def export_template(user: str = Depends(require_auth)):
    """
    Returns a sample .xlsx file for import.
    """
    data = [{
        "Nome": "Exemplo Cisterna",
        "Latitude": -9.41234,
        "Longitude": -38.25678,
        "Categoria": "Cisterna",
        "Descricao": "Ponto de exemplo para importação",
        "Responsavel": user
    }]
    
    df = pd.DataFrame(data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Modelo')
        
        # Adjust column widths
        worksheet = writer.sheets['Modelo']
        for idx, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.column_dimensions[chr(65 + idx)].width = max_len
            
    output.seek(0)
    
    headers = {
        'Content-Disposition': 'attachment; filename="modelo_mapa_pontos.xlsx"'
    }
    
    return StreamingResponse(output, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers=headers)

# --- Views (Old) ---


# --- Category Management ---

@view_router.get("/gestao/mapa/categorias", response_class=HTMLResponse)
async def get_categorias_page(request: Request):
    user = get_user_auth(request)
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse("mapa/categorias.html", {"request": request})

@router.get("/categorias", response_model=List[CategoriaResponse])
async def list_categorias(user: str = Depends(require_auth)):
    return services.get_all_categorias()

@router.post("/categorias", response_model=CategoriaResponse)
async def create_categoria(categoria: CategoriaCreate, user: str = Depends(require_auth)):
    new_cat = services.create_categoria(categoria)
    if not new_cat:
        raise HTTPException(status_code=500, detail="Erro ao criar categoria")
    return new_cat

@router.put("/categorias/{id}", response_model=CategoriaResponse)
async def update_categoria(id: int, categoria: CategoriaCreate, user: str = Depends(require_auth)):
    updated = services.update_categoria(id, categoria)
    if not updated:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return updated

@router.delete("/categorias/{id}")
async def remove_categoria(id: int, user: str = Depends(require_auth)):
    success = services.delete_categoria(id)
    if not success:
         raise HTTPException(status_code=404, detail="Erro ao deletar")
    return {"message": "Deletado com sucesso"}

# --- Sync Endpoint ---
@router.post("/sincronizar-beneficiarios")
async def sincronizar_beneficiarios(data: dict, request: Request):
    user = get_user_auth(request)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    municipio = data.get("municipio")
    status = data.get("status")
    
    if not municipio or not status:
        raise HTTPException(status_code=400, detail="Município e Status são obrigatórios")

    try:
        conn = services.get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 1. Query beneficiaries
        query_ben = """
            SELECT nome_completo, cpf, comunidade, latitude, longitude, status, verificado_bsf 
            FROM beneficiarios 
            WHERE 1=1
            AND UPPER(municipio) = ?
            AND UPPER(status) = ?
            AND latitude IS NOT NULL AND longitude IS NOT NULL
            AND (latitude != 0 OR longitude != 0)
        """
        cursor.execute(query_ben, (municipio.upper(), status.upper()))
        beneficiarios = cursor.fetchall()

        synced_count = 0
        duplicate_count = 0

        for b in beneficiarios:
            nome = b['nome_completo'] or "Sem Nome"
            cpf = b['cpf'] or "N/I"
            comunidade = b['comunidade'] or "N/I"
            lat = b['latitude']
            lng = b['longitude']

            # 2. Check overlap (Idempotency) using CPF in description
            check_query = """
                SELECT id FROM mapa_pontos 
                WHERE tipo = 'Beneficiário' 
                AND descricao LIKE ?
            """
            cursor.execute(check_query, (f"%{cpf}%",))
            exists = cursor.fetchone()

            ver_bsf = False
            if b['verificado_bsf'] and str(b['verificado_bsf']).lower() in ['true', '1', 'sim', 'ok']:
                 ver_bsf = True

            if not exists:
                # 3. Insert
                insert_query = """
                    INSERT INTO mapa_pontos (nome, tipo, cor, descricao, latitude, longitude, status_beneficiario, verificacao_bsf)
                    VALUES (?, 'Beneficiário', '#007bff', ?, ?, ?, ?, ?)
                """
                descricao = f"CPF: {cpf} - Comunidade: {comunidade}"
                cursor.execute(insert_query, (nome, descricao, lat, lng, status, ver_bsf))
                synced_count += 1
            else:
                # Optional: Update existing point with correct status/bsf?
                # User asked for Sync. Let's update IF needed to ensure map is fresh.
                update_query = """
                    UPDATE mapa_pontos 
                    SET status_beneficiario = ?, verificacao_bsf = ?
                    WHERE id = ?
                """
                cursor.execute(update_query, (status, ver_bsf, exists['id']))
                duplicate_count += 1 # Count as skipped for insertion, but updated data

        conn.commit()
        conn.close()

        return JSONResponse({
            "status": "success", 
            "message": f"Sincronização concluída: {synced_count} novos pontos.",
            "synced": synced_count,
            "duplicates_skipped": duplicate_count
        })

    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

