import os
import uuid
import json
import zipfile
import logging
import sqlite3
import openpyxl
import tempfile
from pathlib import Path
from typing import List, Optional
from openpyxl.styles import Alignment

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse

from app.dependencies import get_db_connection
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
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_current_user)
):
    try:
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO cotacoes_master (codigo_cotacao, titulo, descricao, status) VALUES (?, ?, ?, ?)",
            (cotacao.codigo_cotacao, cotacao.titulo,
             cotacao.descricao, cotacao.status)
        )
        novo_id = cursor.lastrowid

        # Inserção de Itens (Novo)
        if cotacao.itens:
            for item in cotacao.itens:
                cursor.execute(
                    "INSERT INTO cotacao_itens (cotacao_master_id, material_id, quantidade) VALUES (?, ?, ?)",
                    (novo_id, item.material_id, item.quantidade)
                )

        db.commit()

        cursor.execute(
            "SELECT * FROM cotacoes_master WHERE id = ?", (novo_id,))
        nova_cotacao_master = dict(cursor.fetchone())
        
        # Carregar itens para retorno (opcional, mas bom para consistência)
        cursor.execute("SELECT * FROM cotacao_itens WHERE cotacao_master_id = ?", (novo_id,))
        nova_cotacao_master['itens_detalhes'] = [dict(i) for i in cursor.fetchall()]
        
        return CotacaoMaster(**nova_cotacao_master)
    except sqlite3.IntegrityError as e:
        raise HTTPException(
            status_code=400, detail=f"Erro de integridade, talvez o código da cotação já exista: {e}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro no servidor: {e}")


@router.post("/api/cotacoes-master/{master_id}/propostas", response_model=Proposta, status_code=201)
async def criar_proposta_para_cotacao(
    master_id: int,
    nome_fornecedor: Optional[str] = Form(None), # Tornado opcional se vier ID
    fornecedor_id: Optional[int] = Form(None),   # Novo campo
    tipo_fornecedor: str = Form(...),
    data_contrato: str = Form(...),
    valor: str = Form(...),
    status: str = Form(...),
    observacao: Optional[str] = Form(None),
    arquivos: List[UploadFile] = File(None),
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_current_user)
):
    try:
        valor_float = float(valor.replace('.', '').replace(',', '.'))
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=400, detail="O valor fornecido não é um número válido.")

    # Lógica Híbrida para Fornecedor
    nome_final_fornecedor = nome_fornecedor
    if fornecedor_id:
        # Se veio ID, busca o nome no cadastro para garantir (ou usa o ID como fonte da verdade)
        cursor_check = db.cursor()
        cursor_check.execute("SELECT razao_social FROM fornecedores WHERE id = ?", (fornecedor_id,))
        forn = cursor_check.fetchone()
        if forn:
            nome_final_fornecedor = forn['razao_social']
        else:
            # ID inválido? Pode falhar ou ignorar. Vamos falhar por coerência.
            raise HTTPException(status_code=400, detail="Fornecedor ID não encontrado.")
    
    if not nome_final_fornecedor:
        raise HTTPException(status_code=400, detail="Nome do fornecedor ou ID do fornecedor é obrigatório.")

    caminho_zip_relativo = None
    if arquivos and arquivos[0].filename:
        nome_zip_unico = f"proposta_{master_id}_{uuid.uuid4().hex[:8]}.zip"
        caminho_zip_absoluto = settings.COTACOES_FOLDER / nome_zip_unico
        try:
            with zipfile.ZipFile(caminho_zip_absoluto, 'w') as zipf:
                for arquivo in arquivos:
                    conteudo = await arquivo.read()
                    zipf.writestr(arquivo.filename, conteudo)
            caminho_zip_relativo = f"uploads/cotacoes/{nome_zip_unico}"
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Erro ao criar o ficheiro ZIP: {e}")

    try:
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO propostas (cotacao_master_id, nome_fornecedor, fornecedor_id, tipo_fornecedor, data_contrato, valor, status, observacao, caminho_arquivo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (master_id, nome_final_fornecedor, fornecedor_id, tipo_fornecedor, data_contrato,
             valor_float, status, observacao, caminho_zip_relativo)
        )
        novo_id = cursor.lastrowid
        db.commit()

        cursor.execute("SELECT * FROM propostas WHERE id = ?", (novo_id,))
        nova_proposta = dict(cursor.fetchone())
        return Proposta(**nova_proposta)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Erro ao salvar a proposta no banco de dados: {e}")


@router.post("/api/cotacoes/analisar-documento")
async def analisar_documento_cotacao(
    file: UploadFile = File(...),
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_current_user)
):
    """
    Recebe um arquivo (PDF/Imagem), envia para o Gemini e retorna os dados extraídos + Match de Cotação e Fornecedor.
    """
    if not file:
         raise HTTPException(status_code=400, detail="Arquivo obrigatório")
    
    try:
        content = await file.read()
        mime_type = file.content_type or "application/pdf"
        
        # Fallback simples de mime-type
        if mime_type == "application/octet-stream":
            if file.filename.lower().endswith(".pdf"):
                mime_type = "application/pdf"
            elif file.filename.lower().endswith((".jpg", ".jpeg")):
                mime_type = "image/jpeg"
            elif file.filename.lower().endswith(".png"):
                mime_type = "image/png"

        resultado_json_str = await extrair_dados_proposta(content, mime_type)
        
        # Validar e retornar
        try:
             dados = json.loads(resultado_json_str)

             # --- Lógica de Match (Detetive) ---
             match_cotacao = None
             match_fornecedor = None
             cursor = db.cursor()

             # 1. Tentar encontrar Cotação Mestra
             raw_numero = dados.get('numero_cotacao')
             if raw_numero:
                 # Tenta limpar string (pega ex: "013")
                 # Se o sistema usa "013/2026", e o PDF tem "013/2026", perfeito.
                 # Se o PDF tem "Nº 013", vamos tentar match parcial ou exato com codigo_cotacao
                 termos = raw_numero.replace("Nº", "").replace("Cotação", "").strip()
                 
                 # Busca exata primeiro
                 cursor.execute("SELECT id, titulo, codigo_cotacao FROM cotacoes_master WHERE codigo_cotacao = ?", (termos,))
                 found = cursor.fetchone()
                 if not found:
                     # Busca por Like (Ex: '%013%') - perigoso se for numero pequeno, mas util
                     cursor.execute("SELECT id, titulo, codigo_cotacao FROM cotacoes_master WHERE codigo_cotacao LIKE ?", (f"%{termos}%",))
                     found = cursor.fetchone()
                 
                 if found:
                     match_cotacao = {
                         "id": found['id'],
                         "titulo": found['titulo'],
                         "codigo_cotacao": found['codigo_cotacao']
                     }

             # 2. Tentar encontrar Fornecedor
             nome_forn = dados.get('nome_fornecedor')
             cnpj_forn = dados.get('cnpj_fornecedor')
             
             forn_found = None
             if cnpj_forn:
                 # Limpa CNPJ para busca apenas numeros
                 cnpj_limpo = "".join(filter(str.isdigit, cnpj_forn))  # noqa: F841
                 # A busca no banco depende de como está salvo. Vamos tentar padrão.
                 # (assumindo tabela fornecedores com coluna cnpj ou documento)
                 # Se não tiver coluna cnpj explícita verificada, tentamos nome.
                 # TODO: Verificar schema de fornecedores. Por segurança, vamos pelo NOME que é garantido existir na extração IA.
                 pass

             if not forn_found and nome_forn:
                 # Busca por Nome (Razão Social ou Fantasia)
                 cursor.execute(
                     "SELECT id, razao_social, nome_fantasia FROM fornecedores WHERE razao_social LIKE ? OR nome_fantasia LIKE ?", 
                     (f"%{nome_forn}%", f"%{nome_forn}%")
                 )
                 forn_found = cursor.fetchone()
            
             if forn_found:
                 # Prioriza Nome Fantasia, se não tiver usa Razão Social
                 nome_exibicao = forn_found['nome_fantasia'] if forn_found['nome_fantasia'] else forn_found['razao_social']
                 match_fornecedor = {
                     "id": forn_found['id'],
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
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro na análise IA: {str(e)}")


@router.get("/api/cotacoes-completas", response_model=List[CotacaoMaster])
def listar_cotacoes_com_propostas(db: sqlite3.Connection = Depends(get_db_connection)):
    try:
        cursor = db.cursor()
        # Order by Year (last 4 chars) DESC, then Sequential Number (first 3 chars) DESC
        cursor.execute("""
            SELECT * FROM cotacoes_master 
            ORDER BY 
                substr(codigo_cotacao, -4) DESC, 
                substr(codigo_cotacao, 1, 3) DESC
        """)
        cotacoes_master_raw = cursor.fetchall()

        resultado_final = []
        for cotacao_master in cotacoes_master_raw:
            cotacao_master_dict = dict(cotacao_master)
            cursor.execute(
                "SELECT * FROM propostas WHERE cotacao_master_id = ? ORDER BY id", (cotacao_master_dict['id'],))
            propostas_raw = cursor.fetchall()
            cotacao_master_dict['propostas'] = [dict(p) for p in propostas_raw]
            resultado_final.append(CotacaoMaster(**cotacao_master_dict))

        return resultado_final
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao buscar cotações: {e}")

@router.put("/api/cotacoes-master/{id}", response_model=CotacaoMaster)
def atualizar_cotacao_master(
    id: int,
    cotacao: CotacaoMasterBase,
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_current_user)
):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT id FROM cotacoes_master WHERE id = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Cotação não encontrada.")

        cursor.execute(
            """
            UPDATE cotacoes_master 
            SET codigo_cotacao = ?, titulo = ?, descricao = ?, status = ?
            WHERE id = ?
            """,
            (cotacao.codigo_cotacao, cotacao.titulo, cotacao.descricao, cotacao.status, id)
        )
        db.commit()

        cursor.execute("SELECT * FROM cotacoes_master WHERE id = ?", (id,))
        updated_cotacao = dict(cursor.fetchone())
        updated_cotacao['propostas'] = [] 
        return CotacaoMaster(**updated_cotacao)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar cotação: {e}")

@router.delete("/api/cotacoes-master/{id}", status_code=204)
def excluir_cotacao_master(
    id: int,
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_current_user)
):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT id FROM cotacoes_master WHERE id = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Cotação não encontrada.")
            
        cursor.execute("DELETE FROM propostas WHERE cotacao_master_id = ?", (id,))
        cursor.execute("DELETE FROM cotacoes_master WHERE id = ?", (id,))
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao excluir cotação: {e}")


@router.delete("/api/cotacoes-propostas/{id}", status_code=204)
def excluir_proposta(
    id: int,
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_current_user)
):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT id FROM propostas WHERE id = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Proposta não encontrada.")
            
        cursor.execute("DELETE FROM propostas WHERE id = ?", (id,))
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao excluir proposta: {e}")

@router.put("/api/cotacoes-propostas/{id}", response_model=Proposta)
def atualizar_proposta(
    id: int,
    proposta_data: PropostaBase,
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_current_user)
):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT id FROM propostas WHERE id = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Proposta não encontrada.")

        # Update fields allowed: valor, status, observacao (others too if needed, but keeping it simple as per request logic)
        # Using PropostaBase allows updating everything passed in data
        cursor.execute(
            """
            UPDATE propostas 
            SET valor = ?, status = ?, observacao = ?, nome_fornecedor = ?, tipo_fornecedor = ?, data_contrato = ?
            WHERE id = ?
            """,
            (proposta_data.valor, proposta_data.status, proposta_data.observacao, 
             proposta_data.nome_fornecedor, proposta_data.tipo_fornecedor, proposta_data.data_contrato, id)
        )
        db.commit()

        cursor.execute("SELECT * FROM propostas WHERE id = ?", (id,))
        updated_proposta = dict(cursor.fetchone())
        return Proposta(**updated_proposta)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar proposta: {e}")


@router.post("/api/cotacoes/gerar-analise-final", response_class=FileResponse)
async def gerar_analise_pdf(
    data: AnaliseCotacaoInput,
    background_tasks: BackgroundTasks,
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_current_user)
):
    logging.info(
        f"Iniciando geração de análise para Cotação ID: {data.cotacao_id}")
    
    temp_excel_path_str = None
    temp_pdf_path_str = None

    try:
        temp_id = uuid.uuid4().hex[:10]
        sistema_temp_dir = tempfile.gettempdir()
        temp_excel_path_str = str(
            Path(sistema_temp_dir) / f"analise_{temp_id}.xlsx")

        if not os.path.exists(settings.TEMPLATE_ANALISE_PATH):
            raise HTTPException(
                status_code=500, detail="Template de análise não encontrado no servidor.")

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
        logging.info(f"Excel temporário salvo em: {temp_excel_path_str}")

        try:
            temp_pdf_path_str = await converter_excel_para_pdf(
                temp_excel_path_str,
                sistema_temp_dir
            )

            if not os.path.exists(temp_pdf_path_str):
                raise Exception("Arquivo PDF não foi criado.")

            logging.info(f"PDF gerado com sucesso em: {temp_pdf_path_str}")

            background_tasks.add_task(
                limpar_ficheiros_temp, 
                [temp_excel_path_str, temp_pdf_path_str]
            )

            nome_ficheiro_final = f"Analise_Cotacao_{data.codigo_cotacao.replace('/', '-')}.pdf"

            return FileResponse(
                temp_pdf_path_str,
                media_type='application/pdf',
                filename=nome_ficheiro_final
            )
        except Exception as e_pdf:
            logging.warning(f"Falha na conversão para PDF: {e_pdf}. Retornando arquivo Excel.")
            
            # Se falhar PDF, retorna o Excel gerado
            background_tasks.add_task(
                limpar_ficheiros_temp, 
                [temp_excel_path_str] # Limpa só o Excel depois de enviar? Não, FileResponse precisa do arquivo. 
                # BackgroundTasks executa DEPOIS da resposta. Então pode limpar.
            )
            
            nome_ficheiro_final = f"Analise_Cotacao_{data.codigo_cotacao.replace('/', '-')}.xlsx"
            return FileResponse(
                temp_excel_path_str,
                media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                filename=nome_ficheiro_final
            )

    except Exception as e:
        background_tasks.add_task(
            limpar_ficheiros_temp, 
            [temp_excel_path_str, temp_pdf_path_str]
        )
        
        logging.error(f"Erro inesperado ao gerar análise PDF: {e}", exc_info=True)
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500, detail=f"Erro interno ao gerar PDF: {e}")
