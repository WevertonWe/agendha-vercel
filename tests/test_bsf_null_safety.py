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
    mock_storage.from_.return_value.create_signed_url.side_effect = lambda path, expires: f"https://supabase.co/storage/v1/object/sign/agendha-uploads/{path}?token=signed_1yr"
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

    # Cenário 3: Caminhos relativos do Storage (Geração de URL assinada)
    caminhos_storage = ["bsf/Salvador/123/atv_1/sigater/relatorio.pdf"]
    expected_url = "https://supabase.co/storage/v1/object/sign/agendha-uploads/bsf/Salvador/123/atv_1/sigater/relatorio.pdf?token=signed_1yr"
    assert parse_links_safe(caminhos_storage, mock_supabase) == [expected_url]
    print("   [OK] Cenário 3 (Caminhos do Storage - Signed URL) passou.")

    # Cenário 4: Elementos nulos ou tipos inválidos misturados (Corrupção de dados)
    dados_misturados = [None, "http://link-valido.com", 42, ["lista-aninhada"], "bsf/doc.pdf"]
    result_misturados = parse_links_safe(dados_misturados, mock_supabase)
    expected_misturados = [
        "http://link-valido.com",
        "https://supabase.co/storage/v1/object/sign/agendha-uploads/bsf/doc.pdf?token=signed_1yr"
    ]
    assert result_misturados == expected_misturados
    print("   [OK] Cenário 4 (Elementos Nulos/Inválidos misturados) passou.")

    # Cenário 5: String representando array JSON (Suporte retroativo/dados crus)
    json_string = '["https://example.com/api", null, "bsf/foto.jpg"]'
    result_json = parse_links_safe(json_string, mock_supabase)
    expected_json = [
        "https://example.com/api",
        "https://supabase.co/storage/v1/object/sign/agendha-uploads/bsf/foto.jpg?token=signed_1yr"
    ]
    assert result_json == expected_json
    print("   [OK] Cenário 5 (String JSON) passou.")

    # Cenário 6: String corrompida (não-JSON contendo apenas string individual)
    string_pura = "bsf/manual.pdf"
    expected_pura = ["https://supabase.co/storage/v1/object/sign/agendha-uploads/bsf/manual.pdf?token=signed_1yr"]
    assert parse_links_safe(string_pura, mock_supabase) == expected_pura
    
    string_json_malformado = "[http://example.com"
    expected_malformado = ["https://supabase.co/storage/v1/object/sign/agendha-uploads/[http://example.com?token=signed_1yr"]
    assert parse_links_safe(string_json_malformado, mock_supabase) == expected_malformado
    print("   [OK] Cenário 6 (Strings puras e JSON malformado) passou.")

    # Cenário 7: Falha catastrófica preventora (Ambos create_signed_url e get_public_url lançam exceção)
    mock_storage_fail = MagicMock()
    mock_storage_fail.from_.return_value.create_signed_url.side_effect = Exception("Erro assinado")
    mock_storage_fail.from_.return_value.get_public_url.side_effect = Exception("Erro publico")
    mock_supabase_fail = MagicMock()
    mock_supabase_fail.storage = mock_storage_fail
    
    # Não deve lançar erro 500 no backend. Deve ignorar o caminho relativo problemático.
    assert parse_links_safe(["bsf/caminho.pdf", "http://link-seguro.com"], mock_supabase_fail) == ["http://link-seguro.com"]
    print("   [OK] Cenário 7 (Tratamento preventivo total de erros no SDK) passou.")

    # Cenário 8: Fallback público ativo (create_signed_url falha, mas get_public_url funciona)
    mock_storage_fallback = MagicMock()
    mock_storage_fallback.from_.return_value.create_signed_url.side_effect = Exception("Erro assinado")
    mock_storage_fallback.from_.return_value.get_public_url.side_effect = lambda path: f"https://supabase.co/storage/v1/object/public/agendha-uploads/{path}"
    mock_supabase_fallback = MagicMock()
    mock_supabase_fallback.storage = mock_storage_fallback
    assert parse_links_safe(["bsf/caminho.pdf"], mock_supabase_fallback) == ["https://supabase.co/storage/v1/object/public/agendha-uploads/bsf/caminho.pdf"]
    print("   [OK] Cenário 8 (Fallback público resiliente) passou.")

    print("\n[SUCESSO] Todos os testes unitarios de Null-Safety passaram com sucesso!")

if __name__ == "__main__":
    test_parse_links_safe()
