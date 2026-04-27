import io
import logging
import zipfile
import os
import tempfile
import pandas as pd
import win32com.client
import pythoncom
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from docxtpl import DocxTemplate
from app.config import settings

router = APIRouter(prefix="/api/bsf", tags=["BSF API"])
logger = logging.getLogger(__name__)

TEMPLATE_PATH = settings.BASE_DIR / "app" / "modules" / "bahia_sem_fome" / "assets" / "atestes.docx"



def converter_para_pdf(word_app, docx_path: Path, pdf_path: Path):
    """
    Converte um arquivo DOCX para PDF usando o Microsoft Word instalado.
    """
    try:
        # Abre o documento (Caminho DEVE ser absoluto no Windows)
        doc = word_app.Documents.Open(str(docx_path))
        # wdFormatPDF = 17
        doc.SaveAs(str(pdf_path), FileFormat=17)
        doc.Close()
        logger.info(f"Conversão Word -> PDF concluída: {pdf_path.name}")
        return True
    except Exception as e:
        logger.error(f"Falha na conversão para PDF via Word: {e}")
        return False

@router.post("/gerar-atestes")
async def gerar_atestes(file: UploadFile = File(...)):
    """
    Lê uma planilha Excel/CSV, preenche o template Word, converte para PDF e retorna um ZIP.
    """
    if not file:
        raise HTTPException(status_code=400, detail="Nenhum arquivo enviado.")

    # 1. Carregar planilha
    try:
        content = await file.read()
        df = None

        if file.filename.lower().endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content), sep=None, engine='python')
            df.columns = df.columns.astype(str).str.strip()
        else:
            planilhas = pd.read_excel(io.BytesIO(content), sheet_name=None)
            
            for _, aba_df in planilhas.items():
                aba_df.columns = aba_df.columns.astype(str).str.strip()
                colunas_up = [str(c).upper() for c in aba_df.columns]
                if any("DADOS DO GRUPO FAMILIAR > NOME" in c for c in colunas_up):
                    df = aba_df
                    break

        if df is None or df.empty:
            raise HTTPException(status_code=400, detail="Planilha inválida. Aba de dados não encontrada.")

        # Busca Flexível de Colunas
        def find_col(key):
            return next((c for c in df.columns if key.upper() in str(c).upper()), None)

        col_nome = find_col("DADOS DO GRUPO FAMILIAR > NOME")
        col_nome = find_col("DADOS DO GRUPO FAMILIAR > NOME")
        
        if col_nome:
            df = df.dropna(subset=[col_nome])
        else:
            raise HTTPException(status_code=400, detail="Coluna de nome não encontrada.")

    except Exception as e:
        logger.error(f"Erro ao ler planilha: {e}")
        raise HTTPException(status_code=400, detail="Formato de planilha inválido.")

    if not os.path.exists(str(TEMPLATE_PATH)):
        raise HTTPException(status_code=500, detail="Template DOCX não encontrado.")

    # 1. Preparar ambiente para conversão via Word (Opção B)
    pythoncom.CoInitialize()
    word_app = None
    
    try:
        # Inicia instância silenciosa do Word
        word_app = win32com.client.Dispatch("Word.Application")
        word_app.Visible = False
        
        zip_buffer = io.BytesIO()
        arquivos_gerados = 0
        
        # Usar diretório temporário para conversão PDF
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir).resolve() # Caminho absoluto obrigatório para COM
            
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                for index, row in df.iterrows():
                    nome_beneficiario = str(row.get(col_nome, "")).strip()
                    if not nome_beneficiario or nome_beneficiario.lower() == "nan":
                        continue

                    # 1. Carrega o template usando docxtpl
                    doc = DocxTemplate(str(TEMPLATE_PATH))
                    
                    # Extração e Limpeza
                    def limpar_valor(val):
                        v = str(val).strip() if pd.notna(val) and str(val).lower() != 'nan' else ""
                        if v.endswith(".0"): 
                            v = v[:-2]
                        return v

                    # Lógica para o Município (que está na coluna 'MUNICIPIO' da planilha reduzida)
                    mun_bruto = limpar_valor(row.get('MUNICIPIO', ''))
                    mun_limpo = mun_bruto.split('-')[0].strip().upper()

                    mapa = {
                        "nome_beneficiario": limpar_valor(row.get('Dados do Grupo Familiar > Nome', '')),
                        "cpf_beneficiario": limpar_valor(row.get('Dados do Grupo Familiar > CPF', '')),
                        "caf_beneficiario": limpar_valor(row.get('DAP / CAF', '')),
                        "nome_tecnico": limpar_valor(row.get('Dados de Execução > Nome do(a) técnico(a) responsável', '')),
                        "cpf_tecnico": limpar_valor(row.get('Dados de Execução > CPF do(a) técnico(a) responsável', '')),
                        "MUNICIPIO": mun_limpo,
                        "COMUNIDADE": limpar_valor(row.get('Dados de Execução > Comunidade', '')).upper()
                    }

                    # 3. Renderiza usando o padrão do docxtpl (chaves duplas {{ }})
                    doc.render(mapa)
                    
                    safe_name = "".join(c for c in nome_beneficiario.upper() if c.isalnum() or c in (" ", "-", "_")).strip()
                    docx_path = tmp_path / f"{safe_name}.docx"
                    pdf_path = tmp_path / f"{safe_name}.pdf"
                    
                    doc.save(str(docx_path))

                    # 2. Converter para PDF (Word COM)
                    if converter_para_pdf(word_app, docx_path, pdf_path):
                        if pdf_path.exists():
                            zip_file.write(str(pdf_path), f"{safe_name} - ATESTE.pdf")
                            arquivos_gerados += 1
                            logger.info(f"Ateste gerado com sucesso para: {nome_beneficiario}")
                    
                if arquivos_gerados == 0:
                    logger.error("Nenhum PDF foi gerado via Word COM.")
                    raise HTTPException(
                        status_code=500, 
                        detail="Falha na conversão PDF. Verifique se o Word está funcionando corretamente no servidor."
                    )

            zip_buffer.seek(0)
            return StreamingResponse(
                iter([zip_buffer.getvalue()]),
                media_type="application/x-zip-compressed",
                headers={"Content-Disposition": "attachment; filename=BSF_Atestes_Gerados.zip"}
            )

    except Exception as e:
        logger.error(f"Erro na geração dos atestes: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno no motor de conversão: {str(e)}")
    
    finally:
        # Garante o fechamento do Word e limpeza do COM
        if word_app:
            try:
                word_app.Quit()
            except Exception:
                pass
        pythoncom.CoUninitialize()
