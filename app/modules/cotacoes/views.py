from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import logging
from app.config import settings

router = APIRouter(tags=["Cotações Views"])
from jinja2 import Environment, FileSystemLoader
_env = Environment(loader=FileSystemLoader("app/templates"), cache_size=0)
templates = Jinja2Templates(env=_env)

async def get_user_context(request: Request):
    is_admin = False
    user_username = "Anônimo"
    token = request.cookies.get("access_token")
    if token:
        try:
            if token.startswith("Bearer "):
                token = token.split(" ")[1]
            from jose import jwt
            from app.core.auth.utils import SECRET_KEY, ALGORITHM
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_username = payload.get("sub", "Anônimo")
            
            from app.core.database import get_supabase
            supabase = get_supabase()
            res_user = supabase.table('users').select('role').eq('username', user_username).execute()
            if res_user.data and res_user.data[0].get('role') == 'admin':
                is_admin = True
        except Exception:
            pass
    return {"is_admin": is_admin, "user_username": user_username}

@router.get("/cotacoes", response_class=HTMLResponse)
async def get_cotacoes_page(request: Request):
    ctx = await get_user_context(request)
    return templates.TemplateResponse(request=request, name="agua/cotacoes.html", context={"current_page": "cotacoes", **ctx})

@router.get("/cotacoes/analise/{cotacao_id}", response_class=HTMLResponse)
async def get_pagina_revisao_analise(cotacao_id: int, request: Request):
    try:
        ctx = await get_user_context(request)
        from app.core.database import get_supabase
        supabase = get_supabase()
        
        res_cot = supabase.table('cotacoes_master').select('*').eq('id', cotacao_id).execute()
        if not res_cot.data:
            raise HTTPException(status_code=404, detail="Cotação não encontrada")
        cotacao = res_cot.data[0]
        
        res_prop = supabase.table('propostas').select('*').eq('cotacao_master_id', cotacao_id).execute()
        propostas = sorted(res_prop.data, key=lambda x: float(x.get('valor') or 0.0))
        
        propostas_top3 = [None, None, None]
        for i, prop in enumerate(propostas[:3]):
            propostas_top3[i] = dict(prop)

        p1, p2, p3 = propostas_top3

        texto_dinamico = f"A Cotação Prévia de Preços nº {cotacao.get('codigo_cotacao', '')}, para {cotacao.get('descricao', '')}, "

        if not p1:
            texto_dinamico += "ainda não recebeu propostas."
        else:
            texto_dinamico += (
                f"teve como vencedora a empresa {str(p1.get('nome_fornecedor', '')).upper()}, "
                f"com o valor de R$ {float(p1.get('valor') or 0.0):.2f}. "
            )
            if p2:
                texto_dinamico += (
                    f"O proponente 2, {str(p2.get('nome_fornecedor', '')).upper()}, "
                    f"apresentou o valor de R$ {float(p2.get('valor') or 0.0):.2f}. "
                )
            if p3:
                texto_dinamico += (
                    f"O proponente 3, {str(p3.get('nome_fornecedor', '')).upper()}, "
                    f"apresentou o valor de R$ {float(p3.get('valor') or 0.0):.2f}."
                )

        texto_dinamico += "\n\n(Texto gerado automaticamente. Revise antes de confirmar.)"

        return templates.TemplateResponse(request=request, name="agua/analise-revisao.html", context={
            "current_page": "cotacoes",
            "cotacao": dict(cotacao),
            "proposta1": p1,
            "proposta2": p2,
            "proposta3": p3,
            "texto_dinamico": texto_dinamico,
            **ctx
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Erro ao buscar cotação no Supabase: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao carregar análise.")
