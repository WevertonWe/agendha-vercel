import io
import zipfile
import pandas as pd
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_gerar_atestes_docx_fallback():
    """
    Testa se o gerador de atestes retorna um arquivo ZIP contendo documentos .docx
    quando a conversão para PDF falha/não está disponível (cenário padrão na Vercel).
    """
    # 1. Arrange: Criar planilha simulando 'novos.xlsx' com colunas do usuário
    dados = {
        "Dados de Execução > Nome do(a) técnico(a) responsável": ["Caroline Evangelista de Queiroz"],
        "Dados de Execução > CPF do(a) técnico(a) responsável": ["079.781.045-59"],
        "MUNICIPIO": ["ABARÉ"],
        "Dados de Execução > Comunidade": ["LAGOA DO JOSE ALVES"],
        "Dados do Grupo Familiar > Nome": ["LEANDRA DA SILVA SANTOS"],
        "Dados do Grupo Familiar > CPF": ["066.570.035-01"],
        "DAP / CAF": ["BA092025.01.0040655756CAF"]
    }
    df = pd.DataFrame(dados)
    
    # Grava DataFrame em Bytes Excel
    excel_io = io.BytesIO()
    with pd.ExcelWriter(excel_io, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Atestes")
    excel_content = excel_io.getvalue()
    
    # 2. Act: Enviar arquivo para o endpoint simulando a conversão de PDF falhando (return False)
    with patch("app.modules.bahia_sem_fome.routers.atestes.converter_para_pdf") as mock_convert:
        mock_convert.return_value = False  # Força fallback para DOCX
        
        response = client.post(
            "/api/bsf/gerar-atestes",
            files={"file": ("novos.xlsx", excel_content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        )
        
    # 3. Assert: Verificar status 200, tipo de retorno ZIP e presença de arquivo .docx no ZIP
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/x-zip-compressed"
    
    # Lendo o ZIP gerado
    zip_bytes = io.BytesIO(response.content)
    with zipfile.ZipFile(zip_bytes) as z:
        filenames = z.namelist()
        assert len(filenames) == 1
        assert "LEANDRA DA SILVA SANTOS - ATESTE.docx" in filenames
        assert "LEANDRA DA SILVA SANTOS - ATESTE.pdf" not in filenames


def test_gerar_atestes_pdf_sucesso():
    """
    Testa se o gerador de atestes retorna um arquivo ZIP contendo documentos .pdf
    quando a conversão para PDF é bem-sucedida (cenário local com Word/LibreOffice).
    """
    dados = {
        "Dados de Execução > Nome do(a) técnico(a) responsável": ["Caroline Evangelista de Queiroz"],
        "Dados de Execução > CPF do(a) técnico(a) responsável": ["079.781.045-59"],
        "MUNICIPIO": ["ABARÉ"],
        "Dados de Execução > Comunidade": ["LAGOA DO JOSE ALVES"],
        "Dados do Grupo Familiar > Nome": ["LEANDRA DA SILVA SANTOS"],
        "Dados do Grupo Familiar > CPF": ["066.570.035-01"],
        "DAP / CAF": ["BA092025.01.0040655756CAF"]
    }
    df = pd.DataFrame(dados)
    
    excel_io = io.BytesIO()
    with pd.ExcelWriter(excel_io, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Atestes")
    excel_content = excel_io.getvalue()
    
    # Mock do conversor para PDF simulando que o PDF foi gerado
    def mock_converter_para_pdf_impl(word_app, docx_path, pdf_path):
        # Simula criação física do arquivo .pdf para o zip_file.write não falhar
        with open(pdf_path, "wb") as f:
            f.write(b"%PDF-1.4 dummy pdf content")
        return True

    with patch("app.modules.bahia_sem_fome.routers.atestes.converter_para_pdf", side_effect=mock_converter_para_pdf_impl):
        response = client.post(
            "/api/bsf/gerar-atestes",
            files={"file": ("novos.xlsx", excel_content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        )
        
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/x-zip-compressed"
    
    zip_bytes = io.BytesIO(response.content)
    with zipfile.ZipFile(zip_bytes) as z:
        filenames = z.namelist()
        assert len(filenames) == 1
        assert "LEANDRA DA SILVA SANTOS - ATESTE.pdf" in filenames
        assert "LEANDRA DA SILVA SANTOS - ATESTE.docx" not in filenames


def test_gerar_atestes_flexible_columns():
    """
    Testa se o gerador de atestes aceita cabeçalhos de coluna levemente modificados
    (espaços extras, minúsculas, partes ausentes) graças à busca flexível.
    """
    # Planilha com colunas em formatos diferentes:
    # "nome" em vez de "Dados do Grupo Familiar > Nome"
    # "dap" em vez de "DAP / CAF"
    # "tecnico" em vez de "Dados de Execução > Nome do(a) técnico(a) responsável"
    dados = {
        "tecnico": ["Caroline Evangelista de Queiroz"],
        "cpf": ["079.781.045-59"],
        "municipio": ["ABARÉ"],
        "comunidade": ["LAGOA DO JOSE ALVES"],
        "nome": ["LEANDRA DA SILVA SANTOS"],
        "dap": ["BA092025.01.0040655756CAF"]
    }
    df = pd.DataFrame(dados)
    
    excel_io = io.BytesIO()
    with pd.ExcelWriter(excel_io, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    excel_content = excel_io.getvalue()
    
    with patch("app.modules.bahia_sem_fome.routers.atestes.converter_para_pdf", return_value=False):
        response = client.post(
            "/api/bsf/gerar-atestes",
            files={"file": ("novos.xlsx", excel_content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        )
        
    assert response.status_code == 200
    zip_bytes = io.BytesIO(response.content)
    with zipfile.ZipFile(zip_bytes) as z:
        filenames = z.namelist()
        assert "LEANDRA DA SILVA SANTOS - ATESTE.docx" in filenames
