import io
import logging
import zipfile
import os
import tempfile
import shutil
import subprocess
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from docxtpl import DocxTemplate
from app.config import settings

# Importações condicionais para o Word COM (Windows apenas)
try:
    import pythoncom
    import win32com.client
    HAS_WIN32COM = True
except ImportError:
    HAS_WIN32COM = False

router = APIRouter(prefix="/api/bsf", tags=["BSF API"])
logger = logging.getLogger(__name__)

TEMPLATE_PATH = settings.BASE_DIR / "app" / "modules" / "bahia_sem_fome" / "assets" / "atestes.docx"


def converter_para_pdf(word_app, docx_path: Path, pdf_path: Path):
    """
    Tenta converter para PDF usando Word COM (Windows) ou LibreOffice (Linux/Windows).
    Retorna True se conseguir, False caso contrário.
    """
    # 1. Tentar LibreOffice (soffice) primeiro, pois funciona tanto em Linux quanto em Windows se instalado
    soffice_cmd = shutil.which("soffice") or shutil.which("libreoffice")
    if soffice_cmd:
        try:
            logger.info(f"Tentando converter usando LibreOffice: {soffice_cmd}")
            # O LibreOffice salva o PDF no output directory com o mesmo nome do docx, mas com extensão .pdf
            # Ex: soffice --headless --convert-to pdf --outdir <outdir> <docx_path>
            subprocess.run(
                [
                    soffice_cmd,
                    "--headless",
                    "--convert-to", "pdf",
                    "--outdir", str(pdf_path.parent),
                    str(docx_path)
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30,
                check=True
            )
            generated_pdf = pdf_path.parent / f"{docx_path.stem}.pdf"
            if generated_pdf.exists():
                if generated_pdf.resolve() != pdf_path.resolve():
                    shutil.move(str(generated_pdf), str(pdf_path))
                return True
        except Exception as e:
            logger.error(f"Erro ao converter com LibreOffice: {e}")

    # 2. Tentar Word COM se win32com estiver disponível e estiver no Windows
    if HAS_WIN32COM:
        local_word = None
        try:
            pythoncom.CoInitialize()
            if word_app is None:
                local_word = win32com.client.Dispatch("Word.Application")
                local_word.Visible = False
                active_word = local_word
            else:
                active_word = word_app

            doc = active_word.Documents.Open(str(docx_path))
            # 17 representa wdFormatPDF
            doc.SaveAs(str(pdf_path), FileFormat=17)
            doc.Close()
            return pdf_path.exists()
        except Exception as e:
            logger.error(f"Erro ao converter com Word COM: {e}")
        finally:
            if local_word:
                try:
                    local_word.Quit()
                except Exception:
                    pass
            if word_app is None:
                try:
                    pythoncom.CoUninitialize()
                except Exception:
                    pass

    logger.warning("Nenhum conversor de PDF (Word COM ou LibreOffice) conseguiu realizar a conversão.")
    return False


@router.post("/gerar-atestes")
async def gerar_atestes(file: UploadFile = File(...)):
    """
    Lê uma planilha Excel/CSV, preenche o template Word, converte para PDF (ou DOCX fallback) e retorna um ZIP.
    """
    if not file:
        raise HTTPException(status_code=400, detail="Nenhum arquivo enviado.")

    # 1. Carregar planilha
    try:
        content = await file.read()
        df = None

        if file.filename.lower().endswith('.csv'):
            try:
                import pandas as pd
                df = pd.read_csv(io.BytesIO(content), sep=None, engine='python')
                df.columns = df.columns.astype(str).str.strip()
            except ImportError:
                raise HTTPException(status_code=501, detail="Processamento de planilhas desativado neste ambiente (Pandas missing).")
        else:
            try:
                import pandas as pd
                planilhas = pd.read_excel(io.BytesIO(content), sheet_name=None)
                if len(planilhas) == 1:
                    df = list(planilhas.values())[0]
                    df.columns = df.columns.astype(str).str.strip()
                else:
                    for _, aba_df in planilhas.items():
                        aba_df.columns = aba_df.columns.astype(str).str.strip()
                        colunas_up = [str(c).upper() for c in aba_df.columns]
                        if any("DADOS DO GRUPO FAMILIAR > NOME" in c for c in colunas_up) or any("NOME" in c for c in colunas_up):
                            df = aba_df
                            break
            except ImportError:
                raise HTTPException(status_code=501, detail="Processamento de Excel desativado neste ambiente (Pandas missing).")

        if df is None or df.empty:
            raise HTTPException(status_code=400, detail="Planilha inválida. Aba de dados não encontrada.")

        # Busca Flexível de Colunas (insensível a acentos e maiúsculas/minúsculas)
        import unicodedata
        def normalize_str(s):
            s = str(s).upper()
            return "".join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

        def find_col(key):
            norm_key = normalize_str(key)
            return next((c for c in df.columns if norm_key in normalize_str(c)), None)

        col_nome = find_col("DADOS DO GRUPO FAMILIAR > NOME") or find_col("NOME")
        col_cpf = find_col("DADOS DO GRUPO FAMILIAR > CPF") or find_col("CPF DO BENEFICIÁRIO") or find_col("CPF")
        col_caf = find_col("DAP / CAF") or find_col("DAP") or find_col("CAF")
        col_nome_tecnico = find_col("DADOS DE EXECUÇÃO > NOME DO(A) TÉCNICO(A) RESPONSÁVEL") or find_col("NOME DO TÉCNICO") or find_col("TECNICO")
        col_cpf_tecnico = find_col("DADOS DE EXECUÇÃO > CPF DO(A) TÉCNICO(A) RESPONSÁVEL") or find_col("CPF DO TÉCNICO")
        col_municipio = find_col("MUNICIPIO")
        col_comunidade = find_col("DADOS DE EXECUÇÃO > COMUNIDADE") or find_col("COMUNIDADE")
        
        if col_nome:
            df = df.dropna(subset=[col_nome])
        else:
            raise HTTPException(status_code=400, detail="Coluna de nome do beneficiário não encontrada na planilha.")

    except Exception as e:
        logger.error(f"Erro ao ler planilha: {e}")
        raise HTTPException(status_code=400, detail="Formato de planilha inválido ou colunas ausentes.")

    if not os.path.exists(str(TEMPLATE_PATH)):
        raise HTTPException(status_code=500, detail="Template DOCX não encontrado.")

    # Inicializa Word COM se disponível
    word_app = None
    if HAS_WIN32COM:
        try:
            pythoncom.CoInitialize()
            word_app = win32com.client.Dispatch("Word.Application")
            word_app.Visible = False
        except Exception as e:
            logger.warning(f"Não foi possível inicializar Word COM globalmente: {e}")
            word_app = None
    
    try:
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
                        if val is None or str(val).lower() == 'nan':
                             return ""
                        v = str(val).strip()
                        if v.endswith(".0"): 
                            v = v[:-2]
                        return v

                    # Lógica para o Município (que está na coluna 'MUNICIPIO' da planilha reduzida)
                    mun_bruto = limpar_valor(row.get(col_municipio, '')) if col_municipio else ''
                    mun_limpo = mun_bruto.split('-')[0].strip().upper()

                    mapa = {
                        "nome_beneficiario": limpar_valor(row.get(col_nome, '')),
                        "cpf_beneficiario": limpar_valor(row.get(col_cpf, '')) if col_cpf else '',
                        "caf_beneficiario": limpar_valor(row.get(col_caf, '')) if col_caf else '',
                        "nome_tecnico": limpar_valor(row.get(col_nome_tecnico, '')) if col_nome_tecnico else '',
                        "cpf_tecnico": limpar_valor(row.get(col_cpf_tecnico, '')) if col_cpf_tecnico else '',
                        "MUNICIPIO": mun_limpo,
                        "COMUNIDADE": limpar_valor(row.get(col_comunidade, '')).upper() if col_comunidade else ''
                    }

                    # 3. Renderiza usando o padrão do docxtpl (chaves duplas {{ }})
                    doc.render(mapa)
                    
                    safe_name = "".join(c for c in nome_beneficiario.upper() if c.isalnum() or c in (" ", "-", "_")).strip()
                    docx_path = tmp_path / f"{safe_name}.docx"
                    pdf_path = tmp_path / f"{safe_name}.pdf"
                    
                    doc.save(str(docx_path))

                    # 2. Converter para PDF (Word COM ou LibreOffice)
                    pdf_gerado = converter_para_pdf(word_app, docx_path, pdf_path)
                    if pdf_gerado and pdf_path.exists():
                        zip_file.write(str(pdf_path), f"{safe_name} - ATESTE.pdf")
                        arquivos_gerados += 1
                        logger.info(f"Ateste PDF gerado com sucesso para: {nome_beneficiario}")
                    else:
                        # Fallback: inclui o DOCX no ZIP se a conversão falhou ou não está disponível
                        if docx_path.exists():
                            zip_file.write(str(docx_path), f"{safe_name} - ATESTE.docx")
                            arquivos_gerados += 1
                            logger.warning(f"Ateste DOCX gerado (sem conversão para PDF) para: {nome_beneficiario}")
                    
                if arquivos_gerados == 0:
                    logger.error("Nenhum arquivo (PDF ou DOCX) foi gerado.")
                    raise HTTPException(
                        status_code=500, 
                        detail="Falha na geração dos atestes. Nenhum arquivo pôde ser criado."
                    )

            zip_buffer.seek(0)
            return StreamingResponse(
                iter([zip_buffer.getvalue()]),
                media_type="application/x-zip-compressed",
                headers={"Content-Disposition": "attachment; filename=BSF_Atestes_Gerados.zip"}
            )

    except HTTPException:
        raise
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
        if HAS_WIN32COM:
            try:
                pythoncom.CoUninitialize()
            except Exception:
                pass
