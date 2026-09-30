import os
import shutil
import uuid
import asyncio
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List
from fastapi import HTTPException
from app.config import settings

# Tenta importar pywin32
try:
    import win32com.client
    import pythoncom
    PYWIN32_DISPONIVEL = True
except ImportError:
    PYWIN32_DISPONIVEL = False
    logging.debug("Biblioteca 'pywin32' não disponível no ambiente (usando fallback multiplataforma).")

PDF_CONVERTER_ENGINE: Optional[str] = None
LIBREOFFICE_EXECUTABLE: Optional[str] = None

def verificar_motores_pdf():
    """
    Verifica quais motores de conversão de PDF estão disponíveis
    no arranque e define a flag global 'PDF_CONVERTER_ENGINE'.
    """
    global PDF_CONVERTER_ENGINE, LIBREOFFICE_EXECUTABLE

    # 1. Tentar o Excel (preferencial em Windows Desktop)
    if PYWIN32_DISPONIVEL:
        try:
            pythoncom.CoInitialize()
            excel = win32com.client.Dispatch("Excel.Application")
            excel.Quit()
            PDF_CONVERTER_ENGINE = "excel"
            logging.info("Detetado motor de PDF: MS Excel (via pywin32)")
            return
        except Exception as e:
            logging.debug(f"pywin32 instalado, mas MS Excel não pôde ser iniciado: {e}")

    # 2. Tentar o LibreOffice (fallback multiplataforma)
    lo_path = getattr(settings, 'LIBREOFFICE_PATH', '')
    if lo_path and os.path.exists(lo_path):
        PDF_CONVERTER_ENGINE = "libreoffice"
        LIBREOFFICE_EXECUTABLE = lo_path
        logging.info(f"Detetado motor de PDF: LibreOffice (em {lo_path})")
    elif shutil.which("libreoffice"):
        PDF_CONVERTER_ENGINE = "libreoffice"
        LIBREOFFICE_EXECUTABLE = shutil.which("libreoffice")
        logging.info(f"Detetado motor de PDF: LibreOffice (via PATH: {LIBREOFFICE_EXECUTABLE})")
    elif shutil.which("soffice"):
        PDF_CONVERTER_ENGINE = "libreoffice"
        LIBREOFFICE_EXECUTABLE = shutil.which("soffice")
        logging.info(f"Detetado motor de PDF: LibreOffice (via soffice PATH: {LIBREOFFICE_EXECUTABLE})")
    else:
        logging.info("Nenhum motor de conversão desktop (Excel/LibreOffice) ativo. Fallback para processamento serverless.")
        PDF_CONVERTER_ENGINE = None
        LIBREOFFICE_EXECUTABLE = None


async def converter_excel_para_pdf(excel_path: str, output_dir: str) -> str:
    """
    Converte um ficheiro Excel para PDF usando o melhor motor
    disponível (Excel ou LibreOffice).
    Retorna o caminho do PDF gerado.
    """
    excel_path_obj = Path(excel_path)
    pdf_path = str(excel_path_obj.with_suffix('.pdf'))

    if PDF_CONVERTER_ENGINE == "excel":
        logging.info("A converter para PDF usando o motor: MS Excel")
        try:
            excel_path_abs = str(excel_path_obj.resolve())
            pdf_path_abs = str(Path(pdf_path).resolve())

            await asyncio.to_thread(pythoncom.CoInitialize)

            def run_excel_conversion():
                excel = None
                workbook = None
                try:
                    excel = win32com.client.Dispatch("Excel.Application")
                    excel.Visible = False
                    workbook = excel.Workbooks.Open(excel_path_abs)
                    workbook.ExportAsFixedFormat(0, pdf_path_abs, 0)
                finally:
                    if workbook:
                        workbook.Close(False)
                    if excel:
                        excel.Quit()
                    pythoncom.CoUninitialize()

            await asyncio.to_thread(run_excel_conversion)
            return pdf_path

        except Exception as e:
            logging.error(
                f"Falha na conversão com MS Excel: {e}", exc_info=True)
            raise HTTPException(
                500, detail=f"Erro ao converter com Excel: {e}")

    elif PDF_CONVERTER_ENGINE == "libreoffice":
        logging.info("A converter para PDF usando o motor: LibreOffice")

        temp_id = uuid.uuid4().hex[:10]
        # Usa o diretório temp do sistema, não o 'output_dir' passado
        sistema_temp_dir = tempfile.gettempdir()
        temp_profile_dir = Path(sistema_temp_dir) / \
            f"libreoffice_profile_{temp_id}"
        os.makedirs(temp_profile_dir, exist_ok=True)

        try:
            executable = LIBREOFFICE_EXECUTABLE or settings.LIBREOFFICE_PATH
            quoted_libreoffice_path = f'"{executable}"'
            # CORREÇÃO: Usa o 'sistema_temp_dir'
            quoted_outdir = f'"{sistema_temp_dir}"'
            quoted_excel_path = f'"{excel_path}"'

            temp_profile_url = f"file:///{str(temp_profile_dir).replace('\\', '/')}"
            temp_profile_url_com_aspas = f'"{temp_profile_url}"'
            temp_profile_arg = f'-env:UserInstallation={temp_profile_url_com_aspas}'

            cmd_string = (
                f"{quoted_libreoffice_path} "
                f"{temp_profile_arg} "
                f"--headless "
                f"--convert-to pdf "
                f"--outdir {quoted_outdir} "
                f"{quoted_excel_path}"
            )

            logging.info(f"Executando comando (com shell=True): {cmd_string}")

            resultado_processo = await asyncio.to_thread(
                subprocess.run,
                cmd_string,
                check=True, timeout=30, shell=True,
                capture_output=True, text=True, encoding='cp850'
            )
            if resultado_processo.stderr:
                logging.warning(
                    f"LibreOffice stderr (não-erro): {resultado_processo.stderr}")

            # O PDF foi salvo em 'sistema_temp_dir', mas o nome do ficheiro está em 'pdf_path'
            return pdf_path

        except Exception as e:
            logging.error(
                f"Falha na conversão com LibreOffice: {e}", exc_info=True)
            raise HTTPException(
                500, detail=f"Erro ao converter com LibreOffice: {e}")
        finally:
            if os.path.exists(temp_profile_dir):
                shutil.rmtree(temp_profile_dir)
    else:
        logging.error("Nenhum motor de conversão PDF foi carregado.")
        raise HTTPException(
            status_code=500, detail="Servidor não configurado: Nenhum motor de conversão (Excel ou LibreOffice) foi encontrado.")


def limpar_ficheiros_temp(caminhos_para_apagar: List[str]):
    """
    Função de limpeza em segundo plano para apagar ficheiros temporários.
    """
    logging.info(
        f"Limpeza em segundo plano: A apagar {len(caminhos_para_apagar)} ficheiro(s)...")
    for caminho in caminhos_para_apagar:
        try:
            if caminho and os.path.exists(caminho):
                os.remove(caminho)
        except Exception as e:
            # Não é um erro crítico se a limpeza falhar, apenas regista
            logging.error(
                f"Erro na limpeza em segundo plano ao apagar {caminho}: {e}")
