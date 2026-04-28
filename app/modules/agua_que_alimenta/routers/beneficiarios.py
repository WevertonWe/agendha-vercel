import shutil
import uuid
import logging
import sqlite3
import datetime
# import pandas as pd
import io
import json
import asyncio
from typing import List, Union, Optional
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response, Request
from fastapi.responses import JSONResponse, HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.dependencies import get_db_connection, get_db
from app.core.auth.dependencies import get_current_user, get_admin_user
from app.modules.agua_que_alimenta.models import (
    Beneficiario, BeneficiarioUpdate, BeneficiarioParaKML, SchemaValidacao
)
from app.config import settings
from app.services.utils import remover_acentos, limpar_cpf
from app.services import ai_vision
import traceback

router = APIRouter(prefix="/api/beneficiarios", tags=["Beneficiários"])
router_root = APIRouter() # Roteador auxiliar para rotas raiz (sem prefixo acumulado)

# --- Models para Relatórios ---
class RelatorioRequest(BaseModel):
    ids: List[int]
    colunas: List[str]
    email: Optional[str] = None

from jinja2 import Environment, FileSystemLoader
_env = Environment(loader=FileSystemLoader("app/templates"), cache_size=0)
templates = Jinja2Templates(env=_env)
logger = logging.getLogger(__name__)

@router_root.get("/beneficiarios/perfil/{id}", response_class=HTMLResponse)
async def ver_perfil_beneficiario(request: Request, id: int, db: sqlite3.Connection = Depends(get_db_connection)):
    """
    Exibe a página de perfil detalhado de um beneficiário específico.
    Busta os dados pelo ID e renderiza o template 'beneficiarios/perfil.html'.
    """
    cursor = db.cursor()
    cursor.execute("SELECT * FROM beneficiarios WHERE id = ?", (id,))
    row = cursor.fetchone()
    
    if not row:
        return templates.TemplateResponse("errors/404.html", {"request": request}, status_code=404)
        
    beneficiario = dict(row)
    
    return templates.TemplateResponse("beneficiarios/perfil.html", {
        "request": request,
        "beneficiario": beneficiario
    })

@router_root.get("/planejamento/abare", response_class=HTMLResponse)
async def view_planejamento_abare(request: Request):
    return templates.TemplateResponse("agua/planejamento_abare.html", {"request": request})

@router.get("", response_class=JSONResponse)
def get_beneficiarios(
    municipio: str | None = None,
    db: sqlite3.Connection = Depends(get_db_connection)
):
    """
    Retorna a lista JSON de todos os beneficiários.
    Suporta filtragem opcional por 'municipio'.
    """
    try:
        cursor = db.cursor()
        query = "SELECT * FROM beneficiarios"
        params = []
        if municipio:
            query += " WHERE UPPER(municipio) = ?"
            params.append(municipio.upper())
        cursor.execute(query, params)
        registros = cursor.fetchall()
        return [dict(registro) for registro in registros]
    except sqlite3.Error as e:
        logging.error(f"API: Erro ao buscar beneficiários: {e}")
        raise HTTPException(
            status_code=500, detail="Erro interno ao buscar dados.")


@router.post("/import/confirmar")
async def confirmar_importacao_csv(
    dados: Union[List[dict], dict],
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_admin_user)
):
    """
    Recebe um JSON (único ou lista) de beneficiários para importar/atualizar.
    Realiza UPSERT: Se CPF existir, atualiza; senão, insere.
    Força status = 'IMPORTADO'.
    """
    cursor = db.cursor()
    count_novos = 0
    count_atualizados = 0

    # Normalizar para lista
    lista_dados = dados if isinstance(dados, list) else [dados]

    try:
        for item in lista_dados:
            # Skip invalid items if needed, or process all that have CPF/Name
            if not item.get('cpf'):
                continue
            
            nome = item.get('nome', 'Desconhecido')
            cpf = item.get('cpf')
            
            # Tentar normalizar campos (Blindagem de Município)
            c_comunidade = item.get('comunidade')
            c_municipio = remover_acentos(item.get('municipio'))
            c_nis = item.get('nis')
            c_lat = item.get('latitude')
            c_lon = item.get('longitude')
            # Force status to IMPORTADO for traceability per user request
            c_status = 'IMPORTADO'
            
            # Verificar se já existe
            cursor.execute("SELECT id FROM beneficiarios WHERE cpf = ?", (cpf,))
            row = cursor.fetchone()
            
            if row:
                # UPDATE
                try:
                    cursor.execute("""
                        UPDATE beneficiarios 
                        SET nome_completo = ?, nome_familiar = ?, comunidade = ?, municipio = ?, nis = ?, latitude = ?, longitude = ?, status = ?
                        WHERE cpf = ?
                    """, (nome, nome, c_comunidade, c_municipio, c_nis, c_lat, c_lon, c_status, cpf))
                    count_atualizados += 1
                except sqlite3.Error as e:
                    logging.error(f"Erro ao atualizar {cpf}: {e}")
            else:
                # INSERT
                try:
                    cursor.execute("""
                        INSERT INTO beneficiarios (nome_completo, nome_familiar, cpf, cpf_familiar, comunidade, municipio, nis, latitude, longitude, status, doc_status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (nome, nome, cpf, cpf, c_comunidade, c_municipio, c_nis, c_lat, c_lon, c_status, 'PENDENTE'))
                    count_novos += 1
                except sqlite3.Error as e:
                    logging.error(f"Erro ao inserir {cpf}: {e}")

        db.commit()
        return {"message": "Processamento concluído", "novos": count_novos, "atualizados": count_atualizados}

    except Exception as e:
        db.rollback()
        logging.error(f"Erro ao confirmar importação CSV: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro interno ao processar importação: {e}")


@router.delete("/{beneficiario_id}", status_code=204)
def excluir_beneficiario(
    beneficiario_id: int, 
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_admin_user)
):
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT id FROM beneficiarios WHERE id = ?", (beneficiario_id,))
        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404, detail="Beneficiário não encontrado.")
        cursor.execute("DELETE FROM beneficiarios WHERE id = ?",
                       (beneficiario_id,))
        db.commit()
        return
    except sqlite3.Error as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Erro no banco de dados ao excluir: {e}")


@router.get("/{beneficiario_id}", response_class=JSONResponse)
def get_beneficiario_por_id(beneficiario_id: int, db: sqlite3.Connection = Depends(get_db_connection)):
    try:
        cursor = db.cursor()
        cursor.execute(
            "SELECT * FROM beneficiarios WHERE id = ?", (beneficiario_id,))
        registro = cursor.fetchone()
        if registro is None:
            raise HTTPException(
                status_code=404, detail="Beneficiário não encontrado.")
        return dict(registro)
    except sqlite3.Error as e:
        raise HTTPException(
            status_code=500, detail=f"Erro no banco de dados: {e}")


@router.put("/{beneficiario_id}", response_class=JSONResponse)
def update_beneficiario(
    beneficiario_id: int, 
    dados: BeneficiarioUpdate, 
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_admin_user)
):
    try:
        campos_para_atualizar = dados.dict(exclude_unset=True)
        if not campos_para_atualizar:
            raise HTTPException(
                status_code=400, detail="Nenhum dado fornecido para atualização.")

        # --- SYNC CPF FAMILIAR (Bug Fix) ---
        # Se alterou o CPF, obrigatoriamente altera o CPF Familiar para manter consistência
        if 'cpf' in campos_para_atualizar:
            campos_para_atualizar['cpf_familiar'] = campos_para_atualizar['cpf']
        # -----------------------------------

        logging.info(
            f"Atualizando ID {beneficiario_id} com dados: {campos_para_atualizar}")

        set_clause_parts = []
        valores = []
        for campo, valor in campos_para_atualizar.items():
            if valor is not None:
                set_clause_parts.append(f"{campo} = ?")
                valores.append(valor)

        if not set_clause_parts:
            logging.warning(
                f"Nenhum campo com valor para atualizar no ID {beneficiario_id}.")
            cursor = db.cursor()
            cursor.execute(
                "SELECT * FROM beneficiarios WHERE id = ?", (beneficiario_id,))
            registro_atual = cursor.fetchone()
            if not registro_atual:
                raise HTTPException(
                    status_code=404, detail="Beneficiário não encontrado após tentativa de atualização vazia.")
            return dict(registro_atual)

        set_clause = ", ".join(set_clause_parts)
        query = f"UPDATE beneficiarios SET {set_clause} WHERE id = ?"  # nosec
        valores.append(beneficiario_id)

        cursor = db.cursor()
        cursor.execute(query, valores)
        db.commit()

        cursor.execute(
            "SELECT * FROM beneficiarios WHERE id = ?", (beneficiario_id,))
        registro_atualizado = dict(cursor.fetchone())
        return registro_atualizado

    except sqlite3.Error as e:
        db.rollback()
        logging.error(
            f"Erro SQLite ao atualizar ID {beneficiario_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Erro no banco de dados ao atualizar: {e}")

    except Exception as e:
        db.rollback()
        logging.error(
            f"Erro inesperado ao atualizar ID {beneficiario_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Erro inesperado no servidor ao atualizar: {e}")

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Erro ao atualizar o documento no banco de dados: {e}")


@router.post("/{beneficiario_id}/documento", response_model=Beneficiario)
async def upload_documento_beneficiario(
    beneficiario_id: int,
    arquivo: UploadFile = File(...),
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_current_user)
):
    """
    Upload genérico de Documento do Beneficiário. Salva em 'beneficiarios_docs' e atualiza 'doc_status'.
    """
    DEST_FOLDER = settings.UPLOAD_FOLDER / "beneficiarios_docs"
    DEST_FOLDER.mkdir(parents=True, exist_ok=True)

    nome_arquivo_unico = f"doc_{uuid.uuid4().hex[:8]}_{arquivo.filename}"
    caminho_absoluto = DEST_FOLDER / nome_arquivo_unico
    
    with open(caminho_absoluto, "wb") as buffer:
        shutil.copyfileobj(arquivo.file, buffer)

    caminho_web_relativo = f"uploads/beneficiarios_docs/{nome_arquivo_unico}"

    try:
        cursor = db.cursor()
        cursor.execute(
            "UPDATE beneficiarios SET doc_status = ? WHERE id = ?",
            (caminho_web_relativo, beneficiario_id)
        )
        db.commit()

        cursor.execute("SELECT * FROM beneficiarios WHERE id = ?", (beneficiario_id,))
        registro_atualizado = dict(cursor.fetchone())
        return Beneficiario(**registro_atualizado)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao salvar documento: {e}")


@router.patch("/{beneficiario_id}/desvincular-pedreiro", status_code=200)
def desvincular_pedreiro(
    beneficiario_id: int,
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_admin_user)
):
    """
    Remove o vínculo do pedreiro com o beneficiário (seta pedreiro_id = NULL).
    """
    try:
        cursor = db.cursor()
        
        # Verify existence
        cursor.execute("SELECT id FROM beneficiarios WHERE id = ?", (beneficiario_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Beneficiário não encontrado.")

        cursor.execute("UPDATE beneficiarios SET pedreiro_id = NULL WHERE id = ?", (beneficiario_id,))
        db.commit()
        return {"message": "Pedreiro desvinculado com sucesso."}
    
    except sqlite3.Error as e:
        db.rollback()
        logging.error(f"Erro no DB ao desvincular pedreiro: {e}")
        raise HTTPException(status_code=500, detail="Erro ao desvincular pedreiro.")


@router.post("/{beneficiario_id}/nota_fiscal", response_model=Beneficiario)
async def upload_nota_fiscal(
    beneficiario_id: int,
    arquivo: UploadFile = File(...),
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_current_user)
):
    """
    Upload específico de Nota Fiscal. Salva em 'pedreiros_docs' e atualiza 'link_nota_fiscal'.
    """
    # Pasta solicitada: app/uploads/pedreiros_docs/
    DEST_FOLDER = settings.UPLOADS_FOLDER / "pedreiros_docs"
    DEST_FOLDER.mkdir(parents=True, exist_ok=True)

    nome_arquivo_unico = f"nf_{uuid.uuid4().hex[:8]}_{arquivo.filename}"
    caminho_absoluto = DEST_FOLDER / nome_arquivo_unico
    
    with open(caminho_absoluto, "wb") as buffer:
        shutil.copyfileobj(arquivo.file, buffer)

    caminho_web_relativo = f"uploads/pedreiros_docs/{nome_arquivo_unico}"

    try:
        cursor = db.cursor()
        cursor.execute(
            "UPDATE beneficiarios SET link_nota_fiscal = ?, status_pagamento = 'PAGO' WHERE id = ?",
            (caminho_web_relativo, beneficiario_id)
        )
        db.commit()

        cursor.execute("SELECT * FROM beneficiarios WHERE id = ?", (beneficiario_id,))
        registro_atualizado = dict(cursor.fetchone())
        return Beneficiario(**registro_atualizado)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao salvar nota fiscal: {e}")


@router.post("/export/kml", response_class=Response)
async def exportar_beneficiarios_kml(beneficiarios_filtrados: List[BeneficiarioParaKML]):
    """
    Exportação KML via POST (Lista Explícita).
    
    Recebe uma lista JSON de beneficiários (filtrados no frontend) e gera o KML.
    Útil quando o filtro é complexo ou selecionado manualmente pelo usuário.
    """
    if not beneficiarios_filtrados:
        raise HTTPException(
            status_code=400, detail="Nenhum beneficiário fornecido para exportação.")

    status_para_estilo = {
        'EM CADASTRO': 'style_em_cadastro',
        'CADASTRADO': 'style_cadastrado',
        'A CONSTRUIR': 'style_a_construir',
        'CONSTRUÍDA': 'style_construida',
        'DEFAULT': 'style_default'
    }

    kml_styles = """
        <Style id="style_em_cadastro">
            <IconStyle>
                <Icon><href>http://maps.google.com/mapfiles/kml/paddle/ylw-stars.png</href></Icon>
                <scale>1.0</scale>
            </IconStyle>
            <LabelStyle><scale>0.8</scale></LabelStyle>
        </Style>
        <Style id="style_cadastrado">
            <IconStyle>
                <Icon><href>http://maps.google.com/mapfiles/kml/paddle/blu-circle.png</href></Icon>
                 <scale>1.0</scale>
            </IconStyle>
             <LabelStyle><scale>0.8</scale></LabelStyle>
        </Style>
        <Style id="style_a_construir">
            <IconStyle>
                <Icon><href>http://maps.google.com/mapfiles/kml/paddle/wht-blank.png</href></Icon>
                 <scale>1.0</scale>
            </IconStyle>
             <LabelStyle><scale>0.8</scale></LabelStyle>
        </Style>
         <Style id="style_construida">
            <IconStyle>
                <Icon><href>http://maps.google.com/mapfiles/kml/paddle/grn-stars.png</href></Icon>
                 <scale>1.0</scale>
            </IconStyle>
             <LabelStyle><scale>0.8</scale></LabelStyle>
        </Style>
        <Style id="style_default">
            <IconStyle>
                <Icon><href>http://maps.google.com/mapfiles/kml/paddle/red-circle.png</href></Icon>
                 <scale>1.0</scale>
            </IconStyle>
             <LabelStyle><scale>0.8</scale></LabelStyle>
        </Style>
    """

    placemarks = []
    for ben in beneficiarios_filtrados:
        if not ben.latitude or not ben.longitude:
            continue

        try:
            lat = float(str(ben.latitude).replace(',', '.'))
            lon = float(str(ben.longitude).replace(',', '.'))

            # Relaxed Validation: Accept any valid coordinate (Brazil roughly -34 to +5 N, -74 to -34 W)
            # Warning if EXACTLY 0.0 (often default value)
            if lat == 0.0 and lon == 0.0:
                 logging.warning(f"Beneficiário {ben.id} ignorado: Coordenadas Zero.")
                 continue

        except (ValueError, TypeError):
            # logging.debug(f"Beneficiário {ben.id} ignorado: Coordenadas Inválidas ({ben.latitude}, {ben.longitude})")
            continue

        status_normalizado = str(
            ben.status).upper() if ben.status else 'DEFAULT'
        style_id = status_para_estilo.get(
            status_normalizado, status_para_estilo['DEFAULT'])

        description = f"""
            <![CDATA[
                <b>Nome:</b> {ben.nome_completo or 'Não informado'}<br/>
                <b>CPF:</b> {ben.cpf or 'Não informado'}<br/>
                <b>Comunidade:</b> {ben.comunidade or 'Não informada'}<br/>
                <b>Status:</b> {ben.status or 'Não informado'}
            ]]>
        """

        placemark = f"""
            <Placemark>
                <name>{ben.nome_completo or 'Beneficiário sem nome'}</name>
                <description>{description}</description>
                <styleUrl>#{style_id}</styleUrl>
                <Point>
                    <coordinates>{lon},{lat},0</coordinates> 
                </Point>
            </Placemark>
        """
        placemarks.append(placemark)

    if not placemarks:
        raise HTTPException(
            status_code=400, detail="Nenhum beneficiário com coordenadas válidas encontrado para exportar.")

    kml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
    <Document>
        <name>Beneficiarios Agua que Alimenta</name>
        {kml_styles}
        {"".join(placemarks)}
    </Document>
</kml>
    """

    filename = f"beneficiarios_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.kml"  # noqa: F841

    return Response(
        content=kml_content,
        media_type='application/vnd.google-earth.kml+xml',
    )


@router.post("/import/comparar", response_class=JSONResponse)
async def comparar_importacao_csv(
    file: UploadFile = File(...),
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_admin_user)
):
    """
    Recebe um CSV/Excel, localiza colunas dinamicamente e retorna lista consolidada para triagem.
    Retorno: { "lista_triagem": [ { status, nome, cpf, ... } ] }
    """
    import io
    import pandas as pd
    from app.services.utils import limpar_cpf

    content = await file.read()
    filename = file.filename.lower()
    
    rows = []

    try:
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            df = pd.read_excel(io.BytesIO(content))
        else:
            # Fallback básico para CSV, mas Excel é o foco
            import csv
            decoded = content.decode('utf-8-sig')
            csv_reader = csv.DictReader(io.StringIO(decoded), delimiter=';')
            if len(csv_reader.fieldnames or []) < 2:
                csv_reader = csv.DictReader(io.StringIO(decoded), delimiter=',')
            rows = list(csv_reader)
            df = pd.DataFrame(rows)

        # Robust Column Search Helper
        def find_column(df, candidates):
            # Normaliza colunas do DF: strip + upper
            cols_map = {str(c).strip().upper(): c for c in df.columns}
            for candidate in candidates:
                cand_upper = candidate.upper()
                # 1. Tentativa Exata
                if cand_upper in cols_map:
                    return cols_map[cand_upper]
                # 2. Tentativa por "Contém" (menos segura, mas útil se específico)
                # ... Melhor evitar contains genérico para não pegar 'CPF' em 'CPF_PAI' erroneamente
                # Vamos iterar e ver se 'candidate' está contido na coluna (ex: 'NUMEROCPF' contém 'CPF')
                for real_col_upper, real_col_name in cols_map.items():
                    if cand_upper in real_col_upper:
                         return real_col_name
            return None

        col_cpf = find_column(df, ['CPF', 'C.P.F', 'DOC', 'DOCUMENTO', 'NR_CPF'])
        col_nome = find_column(df, ['NOME', 'NOME_COMPLETO', 'BENEFICIARIO', 'CANDIDATO'])
        col_nis = find_column(df, ['NIS', 'PIS', 'NIT'])
        col_comunidade = find_column(df, ['COMUNIDADE', 'LOCALIDADE', 'POVOADO'])
        col_lat = find_column(df, ['LAT', 'LATITUDE', 'COORD_X'])
        col_lon = find_column(df, ['LON', 'LONG', 'LONGITUDE', 'COORD_Y'])
        col_status = find_column(df, ['STATUS', 'SITUACAO', 'ESTADO'])
        col_municipio = find_column(df, ['MUNICIPIO', 'CIDADE', 'MUNICÍPIO'])

        # Pre-fetch CPFs do banco
        cursor = db.cursor()
        cursor.execute("SELECT cpf, nome_completo, status, nis, comunidade, latitude, longitude FROM beneficiarios WHERE cpf IS NOT NULL")
        db_beneficiarios = {row['cpf']: dict(row) for row in cursor.fetchall()}

        lista_triagem = []

        # Itera sobre o DataFrame
        for index, row in df.iterrows():
            # Extração segura
            def get_val(col_name):
                if not col_name: return ""  # noqa: E701
                val = row[col_name]
                return str(val).strip() if pd.notna(val) else ""

            raw_nome = get_val(col_nome) or "Desconhecido"
            raw_cpf = get_val(col_cpf)
            raw_nis = get_val(col_nis)
            raw_com = get_val(col_comunidade)
            raw_lat = get_val(col_lat)
            raw_lon = get_val(col_lon)
            raw_status = get_val(col_status).upper()

            # Limpeza
            # Garantir Município Unificado na comparação (Blindagem)
            raw_mun = remover_acentos(get_val(col_municipio)) if 'col_municipio' in locals() and col_municipio else ""
            if not raw_mun: # Fallback caso col_municipio não tenha sido mapeada mas exista no row de alguma forma
                 # Tenta buscar por nomes comuns se col_municipio falhou
                 candidates = ['MUNICIPIO', 'CIDADE', 'MUNICÍPIO']
                 for c in candidates:
                     val = row.get(c)
                     if pd.notna(val):
                         raw_mun = remover_acentos(val)
                         break

            cpf_limpo = limpar_cpf(raw_cpf) if raw_cpf else None

            # Objeto de Triagem
            item = {
                "id_temp": f"temp_{index}", # ID único temporário
                "nome": raw_nome,
                "cpf": cpf_limpo or "", 
                "cpf_original": raw_cpf,
                "nis": raw_nis,
                "comunidade": raw_com,
                "municipio": raw_mun, # Município já normalizado (blindagem)
                "latitude": raw_lat,
                "longitude": raw_lon,
                "status": raw_status, # Status vindo do CSV ou Default
                "status_triagem": "INVALIDO", # NOVO, DUPLICADO, ALTERADO, INVALIDO
                "msg_erro": "",
                "dados_banco": None,
                "diffs": [] # Lista de discrepâncias found
            }

            # Lógica de Status Triagem e Diffs
            if not cpf_limpo or len(cpf_limpo) != 11:
                item["status_triagem"] = "INVALIDO"
                item["msg_erro"] = "CPF Inválido ou Vazio"
            elif cpf_limpo in db_beneficiarios:
                existing = db_beneficiarios[cpf_limpo]
                item["dados_banco"] = existing
                item["status_triagem"] = "DUPLICADO"
                
                # Detectar alterações/conflitos
                diffs = []
                # Helper comp
                def check_diff(field_csv, field_db, label):
                    val_csv = str(item[field_csv] or "").strip().upper()
                    val_db = str(existing[field_db] or "").strip().upper()
                    if val_csv and val_csv != val_db:
                        diffs.append({"campo": label, "novo": item[field_csv], "antigo": existing[field_db]})

                check_diff("nome", "nome_completo", "Nome")
                check_diff("nis", "nis", "NIS")
                check_diff("comunidade", "comunidade", "Comunidade")
                
                # Status Check logic
                # Se o CSV diz 'CADASTRADO' e banco diz 'EM CADASTRO', é update.
                val_status_csv = raw_status.strip().upper()
                val_status_db = str(existing['status'] or "").strip().upper()
                
                if val_status_csv != val_status_db:
                    diffs.append({"campo": "Status", "novo": raw_status, "antigo": existing['status']})

                if diffs:
                    item["diffs"] = diffs
                    # Se tem diffs, o usuário pode querer atualizar, então destacamos
                    item["status_triagem"] = "DUPLICADO" # Mantemos como duplicado visualmente amarelo, mas com aviso info
            else:
                item["status_triagem"] = "NOVO"
                if not raw_nome or len(raw_nome) < 3 or raw_nome == "Desconhecido":
                     item["status_triagem"] = "ATENCAO" 
                     item["msg_erro"] = "Nome ausente ou muito curto"

            lista_triagem.append(item)

        return {
            "resumo": {
                "total": len(lista_triagem),
                "novos": sum(1 for i in lista_triagem if i['status_triagem'] == 'NOVO'),
                "duplicados": sum(1 for i in lista_triagem if i['status_triagem'] == 'DUPLICADO'),
                "invalidos": sum(1 for i in lista_triagem if i['status_triagem'] in ['INVALIDO', 'ATENCAO'])
            },
            "lista_triagem": lista_triagem
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Erro ao processar arquivo: {str(e)}")


# --- Rotas Consolidadas (não são exatamente /api/beneficiarios mas estão relacionadas) ---
# Vou colocar aqui por enquanto, mas poderiam estar em um router 'dashboard'

@router.get("/consolidado/atividades", response_class=JSONResponse)
def get_consolidado_atividades(db: sqlite3.Connection = Depends(get_db_connection)):
    try:
        cursor = db.cursor()
        # Simplificação: Como os dados estão limpos, o GROUP BY SQL é suficiente e performático
        query = """
            SELECT UPPER(TRIM(municipio)) as municipio, status 
            FROM beneficiarios 
            WHERE municipio IS NOT NULL 
              AND municipio != '' 
              AND UPPER(status) != 'EXCLUIDO'
        """
        cursor.execute(query)
        registros = cursor.fetchall()

        dados_agregados = defaultdict(lambda: defaultdict(int))
        for registro in registros:
            # Blindagem final na agregação
            nome_normalizado = registro["municipio"]

            dados_agregados[nome_normalizado]["total_beneficiarios"] += 1
            status = registro["status"]
            if status in ['Em Cadastro', 'EM CADASTRO']:
                dados_agregados[nome_normalizado]["em_cadastro"] += 1
            elif status in ['Cadastrado', 'CADASTRADO']:
                dados_agregados[nome_normalizado]["cadastrado"] += 1
            elif status in ['A Construir', 'A CONSTRUIR']:
                dados_agregados[nome_normalizado]["a_construir"] += 1
            elif status in ['Construída', 'CONSTRUÍDA']:
                dados_agregados[nome_normalizado]["construida"] += 1
            else:
                dados_agregados[nome_normalizado]["outros_status"] += 1

        dados_consolidados = []
        status_keys = ["em_cadastro", "cadastrado",
                       "a_construir", "construida", "outros_status"]
        for nome, contadores in sorted(dados_agregados.items()):
            resultado_final = {
                'municipio': nome,
                'total_beneficiarios': contadores.get('total_beneficiarios', 0)
            }
            for key in status_keys:
                resultado_final[key] = contadores.get(key, 0)

            dados_consolidados.append(resultado_final)

        return dados_consolidados

    except sqlite3.Error as e:
        logging.error(f"API: Erro ao gerar dados consolidados: {e}")
        raise HTTPException(status_code=500, detail="Erro interno.")


@router.get("/municipios", response_class=JSONResponse)
def get_municipios_unicos(db: sqlite3.Connection = Depends(get_db_connection)):
    try:
        cursor = db.cursor()
        query = "SELECT DISTINCT municipio FROM beneficiarios WHERE municipio IS NOT NULL AND municipio != ''"
        cursor.execute(query)
        rows = cursor.fetchall()
        return sorted([row['municipio'] for row in rows])
    except sqlite3.Error as e:
        logging.error(f"Erro ao buscar municípios: {e}")
        return []


# --- Rota de Salvar Validado (Movi para cá pois lida com beneficiários) ---
# (Função antiga removida para evitar duplicidade e conflito de rota)


@router.post("/fix/sync-cpf", status_code=200)
def fix_sync_cpf_familiar(db: sqlite3.Connection = Depends(get_db_connection), current_user = Depends(get_admin_user)):
    """
    Script de Correção: Iguala cpf_familiar ao cpf para corrigir dados antigos.
    """
    try:
        cursor = db.cursor()
        cursor.execute("""
            UPDATE beneficiarios 
            SET cpf_familiar = cpf 
            WHERE cpf IS NOT NULL AND (cpf_familiar IS NULL OR cpf_familiar != cpf)
        """)
        rows = cursor.rowcount
        db.commit()
        return {"message": f"Sucesso! {rows} beneficiários corrigidos (CPF Familiar sincronizado)."}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router_root.post("/api/salvar-validado", status_code=200)
def salvar_validacao(dados: SchemaValidacao, db: sqlite3.Connection = Depends(get_db_connection), current_user = Depends(get_admin_user)):
    """
    Lógica Corrigida:
    1. Usa o CPF para identificar a pessoa (não o ID da fila).
    2. Se o CPF existe -> Atualiza (UPDATE).
    3. Se o CPF não existe -> Cria (INSERT).
    4. No final, marca o item da fila (id_fila) como 'Validado'.
    """
    # 1. Preparação dos Dados
    cpf_limpo = limpar_cpf(dados.cpf)
    if not cpf_limpo:
        raise HTTPException(status_code=400, detail="CPF inválido ou não informado.")

    # Resolver ID da Fila (para dar baixa depois)
    id_fila_para_baixa = None
    if dados.id_fila:
        id_fila_para_baixa = dados.id_fila
    elif dados.id:
        # Fallback caso o front mande no campo id
        id_fila_para_baixa = dados.id 
        
    # --- LÓGICA DE VÍNCULO DE PDF ---
    from app.services import store
    import os
    import shutil
    
    doc_status_final = "OK"
    
    if id_fila_para_baixa:
        try:
            item_fila = store.get_item(str(id_fila_para_baixa))
            if item_fila and item_fila.get('caminho_arquivo_local'):
                caminho_orig = item_fila['caminho_arquivo_local'] 
                nome_orig = os.path.basename(caminho_orig)
                orig_path = settings.UPLOAD_FOLDER / nome_orig
                
                if orig_path.exists():
                    DEST_FOLDER = settings.UPLOAD_FOLDER / "beneficiarios_docs"
                    DEST_FOLDER.mkdir(parents=True, exist_ok=True)
                    novo_nome = f"doc_{id_fila_para_baixa[:8] if isinstance(id_fila_para_baixa, str) else 'ocr'}_{nome_orig}"
                    novo_path = DEST_FOLDER / novo_nome
                    shutil.move(str(orig_path), str(novo_path))
                    doc_status_final = f"uploads/beneficiarios_docs/{novo_nome}"
        except Exception as e_pdf:
            logging.error(f"Erro ao vincular PDF do OCR: {e_pdf}")
    
    # Campos para salvar (Dicionário dinâmico)
    dados_salvar = {
        # CPFs
        'cpf': cpf_limpo,
        'cpf_familiar': cpf_limpo,    # Obrigatório para a listagem
        
        # Nomes
        'nome_completo': dados.nome_completo,
        'nome_familiar': dados.nome_completo, # Espelhar para aparecer na coluna "Nome Familiar"
        
        # Outros campos
        'data_nascimento': dados.data_nascimento,
        'escolaridade': dados.escolaridade,
        'comunidade': dados.comunidade,
        'municipio': dados.municipio,
        'nis': dados.nis,
        'estado_uf': dados.uf or dados.estado_uf, # Tenta pegar de um ou de outro
        'ref_localizacao': dados.ref_localizacao,
        'sexo': dados.sexo,
        'status': "CADASTRADO", # Status inicial para quem sai da validação
        'doc_status': doc_status_final
    }
    
    # Remove chaves com valores None para não apagar dados existentes sem querer no Update
    dados_salvar = {k: v for k, v in dados_salvar.items() if v is not None}

    cursor = db.cursor()
    try:
        # 2. Verificar se a pessoa já existe pelo CPF
        cursor.execute("SELECT id FROM beneficiarios WHERE cpf = ?", (cpf_limpo,))
        pessoa_existente = cursor.fetchone()
        
        id_beneficiario_final = None

        if pessoa_existente:
            # --- CENÁRIO: ATUALIZAR ---
            id_beneficiario_final = pessoa_existente['id']
            
            set_clause = ", ".join([f"{k} = ?" for k in dados_salvar.keys()])
            values = list(dados_salvar.values())
            values.append(id_beneficiario_final)
            
            cursor.execute(f"UPDATE beneficiarios SET {set_clause} WHERE id = ?", values)  # nosec
            logging.info(f"Beneficiário {cpf_limpo} atualizado (ID {id_beneficiario_final}).")
        
        else:
            # --- CENÁRIO: INSERIR NOVO ---
            colunas = ", ".join(dados_salvar.keys())
            placeholders = ", ".join(["?" for _ in dados_salvar])
            values = list(dados_salvar.values())
            
            cursor.execute(f"INSERT INTO beneficiarios ({colunas}) VALUES ({placeholders})", values)  # nosec
            id_beneficiario_final = cursor.lastrowid
            logging.info(f"Beneficiário {cpf_limpo} criado (ID {id_beneficiario_final}).")

        # 3. DAR BAIXA NA FILA
        if id_fila_para_baixa:
            from app.services import store
            store.delete_item(str(id_fila_para_baixa))
        
        db.commit()
        return {"message": "Salvo com sucesso!", "id": id_beneficiario_final}

    except Exception as e:
        db.rollback()
        logging.error(f"Erro ao salvar validação: {e}")
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/export/kml")
def exportar_beneficiarios_kml(  # noqa: F811
    municipio: str | None = None,
    status: str | None = None,
    comunidade: str | None = None,
    db: sqlite3.Connection = Depends(get_db_connection)
):
    """
    Exportação KML via GET (Query Params).
    
    Gera KML baseado nos filtros de URL.
    Útil para links diretos de download ou integração externa.
    """
    try:
        cursor = db.cursor()
        query = "SELECT nome_completo, cpf, comunidade, latitude, longitude, status, municipio FROM beneficiarios WHERE 1=1"
        params = []
        
        if municipio:
            query += " AND UPPER(municipio) = ?"
            params.append(municipio.upper())
        
        if status:
            query += " AND UPPER(status) = ?"
            params.append(status.upper())
            
        if comunidade:
            query += " AND UPPER(comunidade) LIKE ?"
            params.append(f"%{comunidade.upper()}%")
            
        # Ensure we only pick valid coordinates
        query += " AND latitude IS NOT NULL AND longitude IS NOT NULL AND latitude != 0 AND longitude != 0"
            
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Build KML
        kml = ['<?xml version="1.0" encoding="UTF-8"?>']
        kml.append('<kml xmlns="http://www.opengis.net/kml/2.2">')
        kml.append('<Document>')
        kml.append(f'<name>Beneficiarios_{municipio or "Geral"}</name>')
        
        # Define Style
        kml.append('<Style id="beneficiario">')
        kml.append('<IconStyle>')
        kml.append('<scale>1.2</scale>')
        kml.append('<Icon><href>http://maps.google.com/mapfiles/kml/shapes/man.png</href></Icon>')
        kml.append('</IconStyle>')
        kml.append('</Style>')
        
        for row in rows:
            nome = row['nome_completo'] or "Sem Nome"
            cpf = row['cpf'] or "N/I"
            com = row['comunidade'] or "N/I"
            mun = row['municipio'] or "N/I"
            lat = row['latitude']
            lon = row['longitude']
            
            description = f"<b>Comunidade:</b> {com}<br/><b>CPF:</b> {cpf}<br/><b>Município:</b> {mun}"
            
            kml.append('<Placemark>')
            kml.append(f'<name>{nome}</name>')
            kml.append(f'<description><![CDATA[{description}]]></description>')
            kml.append('<styleUrl>#beneficiario</styleUrl>')
            kml.append('<Point>')
            kml.append(f'<coordinates>{lon},{lat},0</coordinates>')
            kml.append('</Point>')
            kml.append('</Placemark>')
            
        kml.append('</Document>')
        kml.append('</kml>')
        
        kml_content = "\n".join(kml)
        
        filename = f"Export_Beneficiarios_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.kml"
        
        return Response(
            content=kml_content,
            media_type="application/vnd.google-earth.kml+xml",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erro no banco de dados: {e}")

# ==============================================================================
# NOVAS ROTAS: GERADOR DE RELATÓRIOS CUSTOMIZADOS (PROJETO AGENDHA)
# ==============================================================================

@router_root.post("/api/relatorios/excel")
async def gerar_relatorio_excel(data: RelatorioRequest, db: sqlite3.Connection = Depends(get_db)):
    """
    Gera um arquivo Excel com colunas customizadas para os IDs fornecidos.
    """
    if not data.ids:
        raise HTTPException(status_code=400, detail="Nenhum ID fornecido")
    
    try:
        # Extração manual para evitar erro de gerador com Pandas
        cursor = db.cursor()
        
        # Mapeamento seguro de colunas permitidas
        colunas_permitidas = {
            "nome_familiar": "Nome",
            "cpf_familiar": "CPF",
            "municipio": "Município",
            "comunidade": "Comunidade",
            "status": "Status",
            "nis": "NIS",
            "tecnico_agua_que_alimenta": "Técnico",
            "doc_status": "Documento",
            "grh": "GRH"
        }
        
        # Filtra apenas colunas válidas
        cols_to_query = [c for c in data.colunas if c in colunas_permitidas]
        if not cols_to_query:
            cols_to_query = list(colunas_permitidas.keys())

        # Query com placeholders seguros
        placeholders = ','.join(['?'] * len(data.ids))
        query = f"SELECT {', '.join(cols_to_query)} FROM beneficiarios WHERE id IN ({placeholders})"
        
        cursor.execute(query, data.ids)
        rows = cursor.fetchall()
        
        # Converte para lista de dicionários (sqlite3.Row -> dict)
        dados_brutos = [dict(row) for row in rows]
        
        dados = []
        for i, linha in enumerate(dados_brutos, start=1):
            # INTERCEPTAÇÃO: Formata o status do documento para algo amigável no Excel
            if 'doc_status' in linha:
                val = linha['doc_status']
                if val and isinstance(val, str) and ('/' in val or '.pdf' in val.lower() or val == 'OK'):
                    linha['doc_status'] = 'OK'
                else:
                    linha['doc_status'] = 'Procurar documento'
            
            # --- INJEÇÃO DA COLUNA "Nº" (Sequential) ---
            if 'numero_ordem' in data.colunas:
                # Cria um novo dicionário com "Nº" na primeira posição
                nova_linha = {'Nº': i}
                nova_linha.update(linha)
                dados.append(nova_linha)
            else:
                dados.append(linha)

        df = pd.DataFrame(dados)

        # Renomeia colunas para o Excel
        df.rename(columns={k: v for k, v in colunas_permitidas.items() if k in cols_to_query}, inplace=True)

        output = io.BytesIO()
        # Força o uso do openpyxl conforme solicitado para garantir compatibilidade e formatação visual
        try:
            from openpyxl.styles import PatternFill, Font
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Beneficiários')
                worksheet = writer.sheets['Beneficiários']
                
                # 1. Cabeçalho em Negrito
                for cell in worksheet[1]:
                    if cell.value:
                        cell.font = Font(bold=True)
                
                # 2. Ajuste automático da largura das colunas
                for col in worksheet.columns:
                    max_length = 0
                    column = col[0].column_letter # Get the column name
                    for cell in col:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except (TypeError, ValueError):
                            pass
                    adjusted_width = (max_length + 2)
                    worksheet.column_dimensions[column].width = adjusted_width

                # 3. Formatação Condicional: Pintar de Amarelo quem precisa "Procurar documento"
                yellow_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
                for r in worksheet.iter_rows():
                    for cell in r:
                        if cell.value == 'Procurar documento':
                            cell.fill = yellow_fill

        except Exception as e_writer:
            logger.error(f"Erro no ExcelWriter (openpyxl) na formatação: {e_writer}")
            # Fallback final direto caso a formatação avançada falhe
            df.to_excel(output, index=False, engine='openpyxl')

        output.seek(0)
        headers = {
            'Content-Disposition': 'attachment; filename="relatorio_beneficiarios.xlsx"'
        }
        return StreamingResponse(output, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers=headers)

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Erro ao gerar Excel: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno no Excel: {str(e)}")


@router_root.post("/api/relatorios/analise")
async def gerar_analise_ia(data: RelatorioRequest, db: sqlite3.Connection = Depends(get_db)):
    """
    Realiza uma análise de dados via Gemini AI baseado nos registros selecionados.
    """
    if not data.ids:
        raise HTTPException(status_code=400, detail="Nenhum ID fornecido")

    try:
        # Extração manual para evitar erro de gerador com Pandas
        cursor = db.cursor()
        # Busca dados brutos para análise
        cols_for_ai = ["nome_familiar", "municipio", "comunidade", "status", "nis", "tecnico_agua_que_alimenta", "grh", "verificado_bsf"]
        # Query com placeholders seguros
        placeholders = ','.join(['?'] * len(data.ids))
        query = f"SELECT {', '.join(cols_for_ai)} FROM beneficiarios WHERE id IN ({placeholders})"
        
        cursor.execute(query, data.ids)
        rows = cursor.fetchall()
        
        # Converte para lista de dicionários
        dados_brutos = [dict(row) for row in rows]
        
        dados_para_ia = []
        for i, linha in enumerate(dados_brutos, start=1):
            if 'numero_ordem' in data.colunas:
                nova_linha = {'Nº': i}
                nova_linha.update(linha)
                dados_para_ia.append(nova_linha)
            else:
                dados_para_ia.append(linha)

        df = pd.DataFrame(dados_para_ia)

        if df.empty:
            return {"analise": "Nenhum dado encontrado para os IDs informados."}

        # Converte para JSON para o Gemini (Garante que é uma lista de dicts limpa)
        dados_dict = df.head(2000).to_dict(orient="records")
        dados_json = json.dumps(dados_dict, ensure_ascii=False, indent=2)
        
        prompt = f"""
        Você é um analista de dados especialista no projeto social Agendha.
        Analise a seguinte lista de beneficiários ({len(df)} registros) e forneça um resumo executivo:
        
        1. **Resumo por Município/Comunidade**: Quais regiões têm mais beneficiários?
        2. **Status da Obra/Processo**: Como está a distribuição dos status?
        3. **Anomalias/Alertas**: Identifique possíveis gargalos ou dados faltantes.
        4. **Sugestão de Ações**: O que o coordenador deve focar agora?
        
        Responda em formato Markdown elegante, use emojis. Seja conciso e técnico.
        
        DADOS:
        {dados_json}
        """

        # Reutilizando a lógica de configuração e chamada do Gemini
        client = ai_vision.get_gemini_client()
        if client:
            response = await asyncio.to_thread(
                client.models.generate_content,
                model="gemini-2.5-flash",
                contents=[prompt]
            )
            analise_texto = response.text
            
            if data.email:
                logger.info(f"📧 [SIMULAÇÃO] Enviando análise para {data.email}")
            
            return {"analise": analise_texto}
        else:
            return {"analise": "⚠️ Erro: API do Gemini não configurada corretamente."}

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Erro na análise IA: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno na IA: {str(e)}")
