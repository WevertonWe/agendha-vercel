import os
import uuid
import json
import zipfile
import logging
import openpyxl
import tempfile
from pathlib import Path
from typing import List, Optional
from openpyxl.styles import Alignment

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks, Depends
from fastapi.responses import FileResponse

from app.core.database import get_supabase, fetch_all
from app.core.auth.dependencies import get_current_user
from app.modules.cotacoes.models import (
    CotacaoMaster, CotacaoMasterBase, Proposta, AnaliseCotacaoInput, PropostaBase
)
from app.config import settings
from app.services.pdf import converter_excel_para_pdf, limpar_ficheiros_temp
from app.modules.cotacoes.services.ai_extractor import extrair_dados_proposta

router = APIRouter(tags=["Cotações"])

@router.post("/api/cotacoes-master", response_model=CotacaoMaster, status_code=201)
def criar_cotacao_master(
    cotacao: CotacaoMasterBase,
    current_user = Depends(get_current_user)
):
    try:
        supabase = get_supabase()
        
        dados_master = {
            "codigo_cotacao": cotacao.codigo_cotacao,
            "titulo": cotacao.titulo,
            "descricao": cotacao.descricao,
            "status": cotacao.status
        }
        res = supabase.table('cotacoes_master').insert(dados_master).execute()
        
        if not res.data:
            raise HTTPException(status_code=500, detail="Erro ao criar cotação no Supabase.")
            
        novo_id = res.data[0]['id']

        if cotacao.itens:
            for item in cotacao.itens:
                supabase.table('cotacao_itens').insert({
                    "cotacao_master_id": novo_id,
                    "material_id": item.material_id,
                    "quantidade": item.quantidade
                }).execute()

        nova_cotacao_master = res.data[0]
        
        res_itens = supabase.table('cotacao_itens').select('*').eq('cotacao_master_id', novo_id).execute()
        nova_cotacao_master['itens_detalhes'] = res_itens.data if res_itens.data else []
        
        return CotacaoMaster(**nova_cotacao_master)
    except HTTPException as he:
        raise he
    except Exception as e:
        logging.error(f"Erro ao criar cotação: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no servidor: {e}")


@router.post("/api/cotacoes-master/{master_id}/propostas", response_model=Proposta, status_code=201)
async def criar_proposta_para_cotacao(
    master_id: int,
    nome_fornecedor: Optional[str] = Form(None),
    fornecedor_id: Optional[int] = Form(None),
    tipo_fornecedor: str = Form(...),
    data_contrato: str = Form(...),
    valor: str = Form(...),
    status: str = Form(...),
    observacao: Optional[str] = Form(None),
    arquivos: List[UploadFile] = File(None),
    current_user = Depends(get_current_user)
):
    try:
        valor_float = float(valor.replace('.', '').replace(',', '.'))
    except (ValueError, AttributeError):
        raise HTTPException(status_code=400, detail="O valor fornecido não é um número válido.")

    supabase = get_supabase()
    nome_final_fornecedor = nome_fornecedor
    if fornecedor_id:
        res_forn = supabase.table('fornecedores').select('razao_social').eq('id', fornecedor_id).execute()
        if res_forn.data:
            nome_final_fornecedor = res_forn.data[0]['razao_social']
        else:
            raise HTTPException(status_code=400, detail="Fornecedor ID não encontrado.")
    
    if not nome_final_fornecedor:
        raise HTTPException(status_code=400, detail="Nome do fornecedor ou ID do fornecedor é obrigatório.")

    caminho_zip_relativo = None
    if arquivos and arquivos[0].filename:
        import tempfile
        import zipfile
        nome_zip_unico = f"proposta_{master_id}_{uuid.uuid4().hex[:8]}.zip"
        temp_zip_dir = Path(tempfile.gettempdir())
        caminho_zip_absoluto = temp_zip_dir / nome_zip_unico
        try:
            with zipfile.ZipFile(caminho_zip_absoluto, 'w') as zipf:
                for arquivo in arquivos:
                    conteudo = await arquivo.read()
                    zipf.writestr(arquivo.filename, conteudo)
            
            with open(caminho_zip_absoluto, "rb") as f:
                zip_bytes = f.read()
                
            supabase.storage.from_('agendha-uploads').upload(
                path=f"cotacoes/{nome_zip_unico}",
                file=zip_bytes,
                file_options={"content-type": "application/zip"}
            )
            
            caminho_zip_relativo = supabase.storage.from_('agendha-uploads').get_public_url(f"cotacoes/{nome_zip_unico}")
            
            if caminho_zip_absoluto.exists():
                os.remove(caminho_zip_absoluto)
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao criar o ficheiro ZIP e enviar ao Supabase: {e}")

    try:
        dados_proposta = {
            "cotacao_master_id": master_id,
            "nome_fornecedor": nome_final_fornecedor,
            "fornecedor_id": fornecedor_id,
            "tipo_fornecedor": tipo_fornecedor,
            "data_contrato": str(data_contrato),
            "valor": valor_float,
            "status": status,
            "observacao": observacao,
            "caminho_arquivo": caminho_zip_relativo
        }
        res = supabase.table('propostas').insert(dados_proposta).execute()
        
        if not res.data:
            raise HTTPException(status_code=500, detail="Erro ao salvar proposta no Supabase.")
            
        return Proposta(**res.data[0])
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar a proposta no banco de dados: {e}")


@router.post("/api/cotacoes/analisar-documento")
async def analisar_documento_cotacao(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    if not file:
         raise HTTPException(status_code=400, detail="Arquivo obrigatório")
    
    try:
        content = await file.read()
        mime_type = file.content_type or "application/pdf"
        
        if mime_type == "application/octet-stream":
            if file.filename.lower().endswith(".pdf"):
                mime_type = "application/pdf"
            elif file.filename.lower().endswith((".jpg", ".jpeg")):
                mime_type = "image/jpeg"
            elif file.filename.lower().endswith(".png"):
                mime_type = "image/png"

        resultado_json_str = await extrair_dados_proposta(content, mime_type)
        
        try:
             dados = json.loads(resultado_json_str)
             match_cotacao = None
             match_fornecedor = None
             supabase = get_supabase()

             raw_numero = dados.get('numero_cotacao')
             if raw_numero:
                 termos = raw_numero.replace("Nº", "").replace("Cotação", "").strip()
                 res_found = supabase.table('cotacoes_master').select('id, titulo, codigo_cotacao').eq('codigo_cotacao', termos).execute()
                 if not res_found.data:
                     res_found = supabase.table('cotacoes_master').select('id, titulo, codigo_cotacao').ilike('codigo_cotacao', f"%{termos}%").execute()
                 
                 if res_found.data:
                     match_cotacao = {
                         "id": res_found.data[0]['id'],
                         "titulo": res_found.data[0]['titulo'],
                         "codigo_cotacao": res_found.data[0]['codigo_cotacao']
                     }

             nome_forn = dados.get('nome_fornecedor')
             if nome_forn:
                 res_forn = supabase.table('fornecedores').select('id, razao_social, nome_fantasia').ilike('razao_social', f"%{nome_forn}%").execute()
                 if not res_forn.data:
                     res_forn = supabase.table('fornecedores').select('id, razao_social, nome_fantasia').ilike('nome_fantasia', f"%{nome_forn}%").execute()
                 
                 if res_forn.data:
                     nome_exibicao = res_forn.data[0]['nome_fantasia'] if res_forn.data[0]['nome_fantasia'] else res_forn.data[0]['razao_social']
                     match_fornecedor = {
                         "id": res_forn.data[0]['id'],
                         "nome": nome_exibicao
                     }

             return {
                 "dados_extraidos": dados,
                 "match_cotacao": match_cotacao,
                 "match_fornecedor": match_fornecedor
             }

        except json.JSONDecodeError:
             return {"erro": "Falha ao decodificar resposta da IA", "raw": resultado_json_str}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise IA: {str(e)}")


@router.get("/api/cotacoes-completas", response_model=List[CotacaoMaster])
def listar_cotacoes_com_propostas():
    try:
        cotacoes_master_raw = fetch_all('cotacoes_master')
        propostas_raw = fetch_all('propostas')

        def parse_codigo(codigo):
            if not codigo:
                return (0, 0)
            partes = str(codigo).split('/')
            if len(partes) == 2:
                try:
                    return (int(partes[1]), int(partes[0]))
                except ValueError:
                    pass
            return (0, 0)

        cotacoes_master_raw.sort(key=lambda x: parse_codigo(x.get('codigo_cotacao')), reverse=True)

        resultado_final = []
        for cotacao_master in cotacoes_master_raw:
            cotacao_master_dict = dict(cotacao_master)
            cotacao_master_dict['propostas'] = [
                dict(p) for p in propostas_raw if p.get('cotacao_master_id') == cotacao_master_dict['id']
            ]
            for p in cotacao_master_dict['propostas']:
                p['data_contrato'] = str(p.get('data_contrato') or '')
                
            resultado_final.append(CotacaoMaster(**cotacao_master_dict))

        return resultado_final
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar cotações: {e}")

@router.put("/api/cotacoes-master/{id}", response_model=CotacaoMaster)
def atualizar_cotacao_master(
    id: int,
    cotacao: CotacaoMasterBase,
    current_user = Depends(get_current_user)
):
    try:
        supabase = get_supabase()
        res_check = supabase.table('cotacoes_master').select('id').eq('id', id).execute()
        if not res_check.data:
            raise HTTPException(status_code=404, detail="Cotação não encontrada.")

        dados = {
            "codigo_cotacao": cotacao.codigo_cotacao,
            "titulo": cotacao.titulo,
            "descricao": cotacao.descricao,
            "status": cotacao.status
        }
        supabase.table('cotacoes_master').update(dados).eq('id', id).execute()

        res = supabase.table('cotacoes_master').select('*').eq('id', id).execute()
        updated_cotacao = dict(res.data[0])
        updated_cotacao['propostas'] = [] 
        return CotacaoMaster(**updated_cotacao)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar cotação: {e}")

@router.delete("/api/cotacoes-master/{id}", status_code=204)
def excluir_cotacao_master(
    id: int,
    current_user = Depends(get_current_user)
):
    try:
        supabase = get_supabase()
        res_check = supabase.table('cotacoes_master').select('id').eq('id', id).execute()
        if not res_check.data:
            raise HTTPException(status_code=404, detail="Cotação não encontrada.")
            
        supabase.table('propostas').delete().eq('cotacao_master_id', id).execute()
        supabase.table('cotacoes_master').delete().eq('id', id).execute()
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao excluir cotação: {e}")

@router.delete("/api/cotacoes-propostas/{id}", status_code=204)
def excluir_proposta(
    id: int,
    current_user = Depends(get_current_user)
):
    try:
        supabase = get_supabase()
        res_check = supabase.table('propostas').select('id').eq('id', id).execute()
        if not res_check.data:
            raise HTTPException(status_code=404, detail="Proposta não encontrada.")
            
        supabase.table('propostas').delete().eq('id', id).execute()
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao excluir proposta: {e}")

@router.put("/api/cotacoes-propostas/{id}", response_model=Proposta)
def atualizar_proposta(
    id: int,
    proposta_data: PropostaBase,
    current_user = Depends(get_current_user)
):
    try:
        supabase = get_supabase()
        res_check = supabase.table('propostas').select('id').eq('id', id).execute()
        if not res_check.data:
            raise HTTPException(status_code=404, detail="Proposta não encontrada.")

        dados = {
            "valor": float(proposta_data.valor),
            "status": proposta_data.status,
            "observacao": proposta_data.observacao,
            "nome_fornecedor": proposta_data.nome_fornecedor,
            "tipo_fornecedor": proposta_data.tipo_fornecedor,
            "data_contrato": str(proposta_data.data_contrato)
        }
        supabase.table('propostas').update(dados).eq('id', id).execute()

        res = supabase.table('propostas').select('*').eq('id', id).execute()
        return Proposta(**dict(res.data[0]))
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar proposta: {e}")

@router.post("/api/cotacoes/gerar-analise-final", response_class=FileResponse)
async def gerar_analise_pdf(
    data: AnaliseCotacaoInput,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
):
    logging.info(f"Iniciando geração de análise para Cotação ID: {data.cotacao_id}")
    
    temp_excel_path_str = None
    temp_pdf_path_str = None

    try:
        temp_id = uuid.uuid4().hex[:10]
        sistema_temp_dir = tempfile.gettempdir()
        temp_excel_path_str = str(Path(sistema_temp_dir) / f"analise_{temp_id}.xlsx")

        if not os.path.exists(settings.TEMPLATE_ANALISE_PATH):
            raise HTTPException(status_code=500, detail="Template de análise não encontrado no servidor.")

        workbook = openpyxl.load_workbook(settings.TEMPLATE_ANALISE_PATH)
        sheet = workbook.active

        sheet['B11'] = f"COTAÇÃO Nº {data.codigo_cotacao}"
        sheet['B11'].alignment = Alignment(horizontal='center', vertical='center')
        sheet['B13'] = data.texto_analise
        sheet['B13'].alignment = Alignment(wrap_text=True, vertical='top', horizontal='justify')
        sheet['C24'] = data.descricao_item
        sheet['E24'] = 1
        sheet['F22'] = data.empresa1_nome
        sheet['F24'] = data.empresa1_valor
        sheet['G24'] = data.empresa1_valor
        if data.empresa2_nome:
            sheet['H22'] = data.empresa2_nome
            sheet['H24'] = data.empresa2_valor
            sheet['I24'] = data.empresa2_valor
        if data.empresa3_nome:
            sheet['J22'] = data.empresa3_nome
            sheet['J24'] = data.empresa3_valor
            sheet['K24'] = data.empresa3_valor

        workbook.save(temp_excel_path_str)
        workbook.close()

        try:
            temp_pdf_path_str = await converter_excel_para_pdf(temp_excel_path_str, sistema_temp_dir)

            if not os.path.exists(temp_pdf_path_str):
                raise Exception("Arquivo PDF não foi criado.")

            background_tasks.add_task(limpar_ficheiros_temp, [temp_excel_path_str, temp_pdf_path_str])

            nome_ficheiro_final = f"Analise_Cotacao_{data.codigo_cotacao.replace('/', '-')}.pdf"

            return FileResponse(temp_pdf_path_str, media_type='application/pdf', filename=nome_ficheiro_final)
        except Exception as e_pdf:
            logging.warning(f"Falha na conversão para PDF: {e_pdf}. Retornando arquivo Excel.")
            background_tasks.add_task(limpar_ficheiros_temp, [temp_excel_path_str])
            
            nome_ficheiro_final = f"Analise_Cotacao_{data.codigo_cotacao.replace('/', '-')}.xlsx"
            return FileResponse(
                temp_excel_path_str,
                media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                filename=nome_ficheiro_final
            )

    except Exception as e:
        background_tasks.add_task(limpar_ficheiros_temp, [temp_excel_path_str, temp_pdf_path_str])
        logging.error(f"Erro inesperado ao gerar análise PDF: {e}", exc_info=True)
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Erro interno ao gerar PDF: {e}")
