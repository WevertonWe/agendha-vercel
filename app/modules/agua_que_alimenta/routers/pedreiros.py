import logging
import uuid
import shutil
from typing import List

from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.database import get_supabase, fetch_all
from app.core.auth.dependencies import get_admin_user
from app.modules.agua_que_alimenta.models import Pedreiro, PedreiroCreate, PedreiroUpdate, FaturamentoCreate
from app.config import settings

router = APIRouter(prefix="/api/pedreiros", tags=["Pedreiros"])
from jinja2 import Environment, FileSystemLoader  # noqa: E402
_env = Environment(loader=FileSystemLoader("app/templates"), cache_size=0)
templates = Jinja2Templates(env=_env)

@router.get("", response_model=List[Pedreiro])
def listar_pedreiros():
    """
    Lista todos os pedreiros cadastrados.
    """
    try:
        pedreiros_bd = fetch_all('pedreiros')
        beneficiarios = fetch_all('beneficiarios')
        
        resultado = []
        for p in pedreiros_bd:
            pedreiro_dict = dict(p)
            pedreiro_id = pedreiro_dict.get('id')
            
            # Filtrar beneficiários deste pedreiro em memória
            obras = [b for b in beneficiarios if b.get('pedreiro_id') == pedreiro_id]
            
            producao_count = 0
            ultima_producao = None
            pendencias = 0
            
            for o in obras:
                status_obra = str(o.get('status') or '').upper()
                if 'CONSTRU' in status_obra or 'CONCLU' in status_obra:
                    producao_count += 1
                    dt_conc = o.get('data_conclusao')
                    if dt_conc:
                        if not ultima_producao or str(dt_conc) > str(ultima_producao):
                            ultima_producao = dt_conc
                    if str(o.get('status_pagamento') or '').upper() == 'PENDENTE':
                        pendencias += 1
                        
            pedreiro_dict['producao_count'] = producao_count
            pedreiro_dict['ultima_producao'] = str(ultima_producao) if ultima_producao else None
            
            if producao_count == 0:
                pedreiro_dict['status_financeiro'] = 'Sem Obras'
            elif pendencias > 0:
                pedreiro_dict['status_financeiro'] = 'Pendente'
            else:
                pedreiro_dict['status_financeiro'] = 'Pago'
                
            # Sanitização preventiva de datas
            for k in pedreiro_dict.keys():
                if 'data' in k or 'created' in k or 'updated' in k:
                    pedreiro_dict[k] = str(pedreiro_dict[k]) if pedreiro_dict[k] is not None else ''
                    
            resultado.append(pedreiro_dict)
            
        return [Pedreiro(**r) for r in resultado]
    except Exception as e:
        logging.error(f"Erro ao listar pedreiros: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar pedreiros.")

@router.post("", response_model=Pedreiro, status_code=201)
def criar_pedreiro(
    pedreiro: PedreiroCreate, 
    current_user = Depends(get_admin_user)
):
    try:
        supabase = get_supabase()
        res_check = supabase.table('pedreiros').select('id').eq('cpf', pedreiro.cpf).execute()
        if res_check.data:
            raise HTTPException(status_code=400, detail="CPF já cadastrado.")

        dados = pedreiro.dict(exclude_unset=True)
        res = supabase.table('pedreiros').insert(dados).execute()
        
        if not res.data:
            raise HTTPException(status_code=500, detail="Erro ao salvar pedreiro no Supabase.")
            
        novo_registro = res.data[0]
        novo_registro['producao_count'] = 0
        return Pedreiro(**novo_registro)
    except HTTPException as he:
        raise he
    except Exception as e:
        logging.error(f"Erro ao criar pedreiro: {e}")
        raise HTTPException(status_code=500, detail="Erro ao salvar pedreiro.")

@router.get("/perfil/{id}", response_class=HTMLResponse)
def perfil_pedreiro(request: Request, id: int):
    supabase = get_supabase()
    res_ped = supabase.table('pedreiros').select('*').eq('id', id).execute()
    if not res_ped.data:
        return templates.TemplateResponse("errors/404.html", {"request": request}, status_code=404)
        
    pedreiro = res_ped.data[0]
    
    beneficiarios = fetch_all('beneficiarios')
    obras = [b for b in beneficiarios if b.get('pedreiro_id') == id]
    
    producao_count = 0
    for o in obras:
        status_obra = str(o.get('status') or '').upper()
        if 'CONSTRU' in status_obra or 'CONCLU' in status_obra:
            producao_count += 1
            
    pedreiro['producao_count'] = producao_count
    
    # Sanitização de datas
    for o in obras:
        for k in o.keys():
            if 'data' in k:
                o[k] = str(o[k]) if o[k] is not None else ''
                
    return templates.TemplateResponse("pedreiros/perfil.html", {
        "request": request, 
        "pedreiro": pedreiro, 
        "obras": obras
    })

@router.put("/{pedreiro_id}", response_model=Pedreiro)
def atualizar_pedreiro(
    pedreiro_id: int,
    dados: PedreiroUpdate,
    current_user = Depends(get_admin_user)
):
    try:
        supabase = get_supabase()
        res_check = supabase.table('pedreiros').select('id').eq('id', pedreiro_id).execute()
        if not res_check.data:
            raise HTTPException(status_code=404, detail="Pedreiro não encontrado.")

        campos_para_atualizar = dados.dict(exclude_unset=True)
        if campos_para_atualizar:
            supabase.table('pedreiros').update(campos_para_atualizar).eq('id', pedreiro_id).execute()
            
        res = supabase.table('pedreiros').select('*').eq('id', pedreiro_id).execute()
        pedreiro = res.data[0]
        
        beneficiarios = fetch_all('beneficiarios')
        producao_count = len([b for b in beneficiarios if b.get('pedreiro_id') == pedreiro_id and ('CONSTRU' in str(b.get('status') or '').upper() or 'CONCLU' in str(b.get('status') or '').upper())])
        
        pedreiro['producao_count'] = producao_count
        return Pedreiro(**pedreiro)
    except HTTPException as he:
        raise he
    except Exception as e:
        logging.error(f"Erro ao atualizar pedreiro: {e}")
        raise HTTPException(status_code=500, detail="Erro ao atualizar pedreiro.")

@router.get("/{pedreiro_id}/producao", response_model=List[dict])
def listar_producao_pedreiro(pedreiro_id: int):
    try:
        beneficiarios = fetch_all('beneficiarios')
        obras = []
        for b in beneficiarios:
            if b.get('pedreiro_id') == pedreiro_id:
                status_obra = str(b.get('status') or '').upper()
                if 'CONSTRU' in status_obra or 'CONCLU' in status_obra:
                    b['data_conclusao'] = str(b.get('data_conclusao') or '')
                    obras.append(b)
                    
        obras.sort(key=lambda x: x.get('data_conclusao', ''), reverse=True)
        return obras
    except Exception as e:
        logging.error(f"Erro ao listar produção do pedreiro {pedreiro_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar produção.")

@router.get("/{pedreiro_id}/pendentes", response_model=List[dict])
def listar_pendentes_faturamento(pedreiro_id: int):
    try:
        beneficiarios = fetch_all('beneficiarios')
        obras = []
        for b in beneficiarios:
            if b.get('pedreiro_id') == pedreiro_id:
                status_obra = str(b.get('status') or '').upper()
                if ('CONSTRU' in status_obra or 'CONCLU' in status_obra) and b.get('faturamento_id') is None:
                    b['valor_sugerido'] = 1000.0
                    b['data_conclusao'] = str(b.get('data_conclusao') or '')
                    obras.append(b)
                    
        obras.sort(key=lambda x: x.get('nome_completo', ''))
        return obras
    except Exception as e:
        logging.error(f"Erro ao listar pendentes do pedreiro {pedreiro_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar pendentes de faturamento.")

@router.post("/faturamentos", status_code=201)
def gerar_lote_faturamento(
    payload: FaturamentoCreate,
    current_user = Depends(get_admin_user)
):
    if not payload.beneficiarios_ids:
        raise HTTPException(status_code=400, detail="Nenhuma cisterna foi enviada para faturar.")
        
    try:
        supabase = get_supabase()
        
        dados_fat = {
            "pedreiro_id": payload.pedreiro_id,
            "valor_total": payload.valor_total,
            "valor_dam": payload.valor_dam,
            "status_dam": "Pendente"
        }
        res_fat = supabase.table('faturamentos').insert(dados_fat).execute()
        
        if not res_fat.data:
            raise HTTPException(status_code=500, detail="Erro ao gerar lote de faturamento no Supabase.")
            
        novo_faturamento_id = res_fat.data[0]['id']
        
        for b_id in payload.beneficiarios_ids:
            supabase.table('beneficiarios').update({
                "faturamento_id": novo_faturamento_id,
                "status_pagamento": "PAGO"
            }).eq('id', b_id).execute()
            
        return {"message": "Lote gerado com sucesso", "faturamento_id": novo_faturamento_id}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logging.error(f"Erro ao gerar faturamento lote: {e}")
        raise HTTPException(status_code=500, detail="Erro ao gerar faturamento.")

@router.get("/{pedreiro_id}/faturamentos", response_model=List[dict])
def listar_historico_faturamentos(pedreiro_id: int):
    try:
        faturamentos = fetch_all('faturamentos')
        beneficiarios = fetch_all('beneficiarios')
        
        faturamentos_pedreiro = [f for f in faturamentos if f.get('pedreiro_id') == pedreiro_id]
        
        resultado = []
        for f in faturamentos_pedreiro:
            item = dict(f)
            fat_id = item.get('id')
            
            obras_vinculadas = [b for b in beneficiarios if b.get('faturamento_id') == fat_id]
            item['qtd_obras'] = len(obras_vinculadas)
            
            obras_detalhes = []
            for b in obras_vinculadas:
                obras_detalhes.append({
                    "nome": b.get('nome_completo'),
                    "local": b.get('comunidade') or b.get('municipio') or ''
                })
            item['obras'] = obras_detalhes
            
            for k in item.keys():
                if 'data' in k:
                    item[k] = str(item[k]) if item[k] is not None else ''
                    
            resultado.append(item)
            
        resultado.sort(key=lambda x: x.get('data_criacao', ''), reverse=True)
        return resultado
        
    except Exception as e:
        logging.error(f"Erro ao listar histórico de faturamentos do pedreiro {pedreiro_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar histórico financeiro.")

@router.post("/faturamentos/{faturamento_id}/upload-nf")
async def upload_faturamento_nf(
    faturamento_id: int,
    arquivo: UploadFile = File(...),
    current_user = Depends(get_admin_user)
):
    DEST_FOLDER = settings.UPLOAD_FOLDER / "financeiro"
    DEST_FOLDER.mkdir(parents=True, exist_ok=True)

    nome_arquivo_unico = f"nf_lote_{faturamento_id}_{uuid.uuid4().hex[:8]}_{arquivo.filename}"
    caminho_absoluto = DEST_FOLDER / nome_arquivo_unico
    
    with open(caminho_absoluto, "wb") as buffer:
        shutil.copyfileobj(arquivo.file, buffer)

    caminho_web_relativo = f"uploads/financeiro/{nome_arquivo_unico}"

    try:
        supabase = get_supabase()
        supabase.table('faturamentos').update({"arquivo_nf": caminho_web_relativo}).eq('id', faturamento_id).execute()
        return {"message": "Nota Fiscal salva com sucesso", "url": caminho_web_relativo}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar NF no banco: {e}")

@router.post("/faturamentos/{faturamento_id}/upload-dam")
async def upload_faturamento_dam(
    faturamento_id: int,
    arquivo: UploadFile = File(...),
    current_user = Depends(get_admin_user)
):
    DEST_FOLDER = settings.UPLOAD_FOLDER / "financeiro"
    DEST_FOLDER.mkdir(parents=True, exist_ok=True)

    nome_arquivo_unico = f"dam_lote_{faturamento_id}_{uuid.uuid4().hex[:8]}_{arquivo.filename}"
    caminho_absoluto = DEST_FOLDER / nome_arquivo_unico
    
    with open(caminho_absoluto, "wb") as buffer:
        shutil.copyfileobj(arquivo.file, buffer)

    caminho_web_relativo = f"uploads/financeiro/{nome_arquivo_unico}"

    try:
        supabase = get_supabase()
        supabase.table('faturamentos').update({"arquivo_dam": caminho_web_relativo}).eq('id', faturamento_id).execute()
        return {"message": "DAM salvo com sucesso", "url": caminho_web_relativo}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar DAM no banco: {e}")

@router.delete("/faturamentos/{faturamento_id}")
def estornar_lote_faturamento(
    faturamento_id: int,
    current_user = Depends(get_admin_user)
):
    try:
        supabase = get_supabase()
        
        supabase.table('beneficiarios').update({
            "faturamento_id": None, 
            "status_pagamento": "PENDENTE"
        }).eq('faturamento_id', faturamento_id).execute()
        
        res = supabase.table('faturamentos').delete().eq('id', faturamento_id).execute()
        
        if not res.data:
            raise HTTPException(status_code=404, detail="Lote de faturamento não encontrado.")
            
        return {"message": "Lote estornado com sucesso."}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logging.error(f"Erro ao estornar faturamento lote {faturamento_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao estornar lote de faturamento.")
