import os
import sys
import logging
from unittest.mock import MagicMock

# Ajusta path para importar o modulo correto do app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Habilita logging para os warnings do parser
logging.basicConfig(level=logging.INFO)

from app.modules.bahia_sem_fome.routers.beneficiarios import parse_links_safe  # noqa: E402

def test_parse_links_safe():
    print("Iniciando testes unitários de Null-Safety para parse_links_safe...")

    # Mock do Supabase Storage
    mock_storage = MagicMock()
    mock_storage.from_.return_value.get_public_url.side_effect = lambda path: f"https://supabase.co/storage/v1/object/public/agendha-uploads/{path}"
    
    mock_supabase = MagicMock()
    mock_supabase.storage = mock_storage

    # Cenário 1: None / Vazio
    assert parse_links_safe(None, mock_supabase) == []
    assert parse_links_safe([], mock_supabase) == []
    assert parse_links_safe("", mock_supabase) == []
    print("   [OK] Cenário 1 (None/Vazio) passou.")

    # Cenário 2: Links válidos absolutos (HTTP/HTTPS)
    links_http = ["http://salvador.ba.gov.br/doc.pdf", "https://google.com/test.png"]
    assert parse_links_safe(links_http, mock_supabase) == links_http
    print("   [OK] Cenário 2 (Links Absolutos) passou.")

    # Cenário 3: Caminhos relativos do Storage
    caminhos_storage = ["bsf/Salvador/123/atv_1/sigater/relatorio.pdf"]
    expected_url = "https://supabase.co/storage/v1/object/public/agendha-uploads/bsf/Salvador/123/atv_1/sigater/relatorio.pdf"
    assert parse_links_safe(caminhos_storage, mock_supabase) == [expected_url]
    print("   [OK] Cenário 3 (Caminhos do Storage) passou.")

    # Cenário 4: Elementos nulos ou tipos inválidos misturados (Corrupção de dados)
    dados_misturados = [None, "http://link-valido.com", 42, ["lista-aninhada"], "bsf/doc.pdf"]
    result_misturados = parse_links_safe(dados_misturados, mock_supabase)
    expected_misturados = [
        "http://link-valido.com",
        "https://supabase.co/storage/v1/object/public/agendha-uploads/bsf/doc.pdf"
    ]
    assert result_misturados == expected_misturados
    print("   [OK] Cenário 4 (Elementos Nulos/Inválidos misturados) passou.")

    # Cenário 5: String representando array JSON (Suporte retroativo/dados crus)
    json_string = '["https://example.com/api", null, "bsf/foto.jpg"]'
    result_json = parse_links_safe(json_string, mock_supabase)
    expected_json = [
        "https://example.com/api",
        "https://supabase.co/storage/v1/object/public/agendha-uploads/bsf/foto.jpg"
    ]
    assert result_json == expected_json
    print("   [OK] Cenário 5 (String JSON) passou.")

    # Cenário 6: String corrompida (não-JSON contendo apenas string individual)
    string_pura = "bsf/manual.pdf"
    expected_pura = ["https://supabase.co/storage/v1/object/public/agendha-uploads/bsf/manual.pdf"]
    assert parse_links_safe(string_pura, mock_supabase) == expected_pura
    
    string_json_malformado = "[http://example.com"
    # Deve ser tratado como uma string individual, porém como não começa com http e não é JSON válido,
    # será interpretada como caminho relativo de storage.
    expected_malformado = ["https://supabase.co/storage/v1/object/public/agendha-uploads/[http://example.com"]
    assert parse_links_safe(string_json_malformado, mock_supabase) == expected_malformado
    print("   [OK] Cenário 6 (Strings puras e JSON malformado) passou.")

    # Cenário 7: Falha catastrófica preventora (get_public_url lança exceção)
    mock_storage_fail = MagicMock()
    mock_storage_fail.from_.return_value.get_public_url.side_effect = Exception("Erro simulado do SDK do Supabase")
    mock_supabase_fail = MagicMock()
    mock_supabase_fail.storage = mock_storage_fail
    
    # Não deve lançar erro 500 no backend. Deve ignorar o caminho relativo problemático.
    assert parse_links_safe(["bsf/caminho.pdf", "http://link-seguro.com"], mock_supabase_fail) == ["http://link-seguro.com"]
    print("   [OK] Cenário 7 (Tratamento preventivo de erros no SDK) passou.")

    print("\n[SUCESSO] Todos os testes unitarios de Null-Safety passaram com sucesso!")

if __name__ == "__main__":
    test_parse_links_safe()
