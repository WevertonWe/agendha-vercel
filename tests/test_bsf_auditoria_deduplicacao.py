"""
Suíte de Testes Automatizados: Auditoria Local, Deduplicação de Pastas e Coletum v2
Estruturada conforme o padrão AAA (Arrange, Act, Assert) e a Pirâmide de Testes.
Engenharia de Software + Blindagem de Segurança (Penetration Testing).
"""

import os
import shutil
import tempfile
import pytest
from pathlib import Path

from app.modules.bahia_sem_fome.services.auditoria_service import (
    sanitizar_nome_seguro,
    normalizar_nome_canonico,
    identificar_pastas_duplicadas_por_acentos,
    consolidar_pastas_duplicadas_segura,
    verificar_conformidade_atividade,
    executar_auditoria_completa_pastas_locais
)
from app.services.coletum_service import (
    normalizar_texto_comparacao,
    normalizar_cpf_comparacao,
    calcular_similaridade_nomes,
    extrair_metadados_resposta_coletum,
    auditar_discrepancias_coletum
)


# ==============================================================================
# 1. TESTES UNITÁRIOS: NORMALIZAÇÃO & BLINDAGEM DE PATH TRAVERSAL
# ==============================================================================

def test_sanitizacao_nome_seguro_e_path_traversal():
    # Arrange
    malicious_inputs = [
        ("../../etc/passwd", "ETCPASSWD"),
        ("..\\..\\Windows\\System32", "WINDOWSSYSTEM32"),
        ("JOSÉ / DA SILVA : TESTE", "JOSE DA SILVA TESTE"),
        ("João   da   Silva---", "JOAO DA SILVA---"),
        ("COMUNIDADE SÃO JOSÉ (ZONA RURAL)", "COMUNIDADE SAO JOSE ZONA RURAL")
    ]

    # Act & Assert
    for entrada, esperado in malicious_inputs:
        resultado = sanitizar_nome_seguro(entrada)
        assert resultado == esperado
        # Garante ausência de caracteres de traversal
        assert ".." not in resultado
        assert "/" not in resultado
        assert "\\" not in resultado
        assert ":" not in resultado


def test_normalizacao_nome_canonico_acentos():
    # Arrange
    variacoes = [
        ("JOSÉ DA SILVA", "JOSE DA SILVA"),
        ("josé da silva", "JOSE DA SILVA"),
        ("JOSE DA SILVA", "JOSE DA SILVA"),
        ("São Francisco do Conde", "SAO FRANCISCO DO CONDE"),
        ("SÃO FRANCISCO DO CONDE", "SAO FRANCISCO DO CONDE"),
        ("Érica Araújo", "ERICA ARAUJO")
    ]

    # Act & Assert
    for entrada, esperado in variacoes:
        assert normalizar_nome_canonico(entrada) == esperado


# ==============================================================================
# 2. TESTES DE INTEGRAÇÃO: IDENTIFICAÇÃO E CONSOLIDAÇÃO DE PASTAS DUPLICADAS
# ==============================================================================

def test_identificacao_e_consolidacao_pastas_duplicadas():
    # Arrange: Cria estrutura temporária com duplicidades de acento
    with tempfile.TemporaryDirectory() as tmp_dir:
        base = Path(tmp_dir)
        
        # Cria pastas duplicadas de comunidade
        pasta_acentuada = base / "SÃO PEDRO"
        pasta_sem_acento = base / "SAO PEDRO"
        pasta_acentuada.mkdir()
        pasta_sem_acento.mkdir()

        # Cria arquivos em cada uma
        (pasta_acentuada / "doc1.txt").write_text("conteudo 1", encoding="utf-8")
        (pasta_sem_acento / "doc2.txt").write_text("conteudo 2", encoding="utf-8")

        # Act 1: Identificar duplicidades
        dups = identificar_pastas_duplicadas_por_acentos(base)
        
        # Assert 1
        assert len(dups) == 1
        assert dups[0]["nome_canonico"] == "SAO PEDRO"
        assert len(dups[0]["pastas_existentes"]) == 2

        # Act 2: Consolidar pastas com segurança
        res_consolidacao = consolidar_pastas_duplicadas_segura(base)

        # Assert 2
        assert res_consolidacao["sucesso"] is True
        assert res_consolidacao["arquivos_movidos"] >= 1
        
        # A pasta canônica SAO PEDRO deve conter ambos os arquivos
        pasta_final = base / "SAO PEDRO"
        assert pasta_final.exists()
        assert (pasta_final / "doc1.txt").exists()
        assert (pasta_final / "doc2.txt").exists()
        
        # A pasta duplicada SÃO PEDRO deve ter sido removida com segurança
        assert not pasta_acentuada.exists()


# ==============================================================================
# 3. TESTES DE CONFORMIDADE DOCUMENTAL (ATESTE + COLETUM)
# ==============================================================================

def test_verificacao_conformidade_atividade_completa():
    with tempfile.TemporaryDirectory() as tmp_dir:
        pasta_ativ = Path(tmp_dir) / "28.04.2026 - PLANO PRODUTIVO"
        pasta_ativ.mkdir()

        # Arrange: Adiciona ambos os documentos
        (pasta_ativ / "MARIA SANTOS - ATESTE.pdf").write_bytes(b"%PDF-1.4 test")
        (pasta_ativ / "MARIA SANTOS - COLLETUM.pdf").write_bytes(b"%PDF-1.4 test")

        # Act
        conf = verificar_conformidade_atividade(pasta_ativ)

        # Assert
        assert conf["status"] == "COMPLETO"
        assert conf["tem_ateste"] is True
        assert conf["tem_coletum"] is True
        assert len(conf["arquivos_ateste"]) == 1
        assert len(conf["arquivos_coletum"]) == 1


def test_verificacao_conformidade_pendente_ateste():
    with tempfile.TemporaryDirectory() as tmp_dir:
        pasta_ativ = Path(tmp_dir) / "28.04.2026 - PLANO PRODUTIVO"
        pasta_ativ.mkdir()

        # Arrange: Apenas Coletum
        (pasta_ativ / "JOAO SILVA - COLLETUM.pdf").write_bytes(b"%PDF-1.4 test")

        # Act
        conf = verificar_conformidade_atividade(pasta_ativ)

        # Assert
        assert conf["status"] == "PENDENTE_ATESTE"
        assert conf["tem_ateste"] is False
        assert conf["tem_coletum"] is True


def test_verificacao_conformidade_pendente_coletum():
    with tempfile.TemporaryDirectory() as tmp_dir:
        pasta_ativ = Path(tmp_dir) / "28.04.2026 - PLANO PRODUTIVO"
        pasta_ativ.mkdir()

        # Arrange: Apenas Ateste
        (pasta_ativ / "CARLOS ALVES - ATESTE.pdf").write_bytes(b"%PDF-1.4 test")

        # Act
        conf = verificar_conformidade_atividade(pasta_ativ)

        # Assert
        assert conf["status"] == "PENDENTE_COLETUM"
        assert conf["tem_ateste"] is True
        assert conf["tem_coletum"] is False


def test_auditoria_completa_estrutura_pastas_locais():
    with tempfile.TemporaryDirectory() as tmp_dir:
        base_dir = Path(tmp_dir)
        
        # Cria técnico, comunidade e beneficiário
        pasta_tec = base_dir / "caroline" / "documentos-atividades" / "CENTRO" / "MARIA SANTOS"
        pasta_ativ = pasta_tec / "10.05.2026 - VISITA"
        pasta_ativ.mkdir(parents=True)

        (pasta_ativ / "MARIA SANTOS - ATESTE.pdf").write_bytes(b"%PDF-1.4")
        (pasta_ativ / "MARIA SANTOS - COLLETUM.pdf").write_bytes(b"%PDF-1.4")

        # Act
        resultado = executar_auditoria_completa_pastas_locais(base_dir=base_dir)

        # Assert
        resumo = resultado["resumo"]
        assert resumo["total_tecnicos"] == 1
        assert resumo["total_comunidades"] == 1
        assert resumo["total_beneficiarios"] == 1
        assert resumo["total_atividades"] == 1
        assert resumo["atividades_completas"] == 1
        assert resumo["percentual_conformidade"] == 100.0


# ==============================================================================
# 4. TESTES DE CRUZAMENTO COLETUM & DETECÇÃO DE DISCREPÂNCIAS (FUZZY & DATAS)
# ==============================================================================

def test_similaridade_nomes_fuzzy_levenshtein():
    # Arrange & Act
    score_exato = calcular_similaridade_nomes("Weverton Silva", "Weverton Silva")
    score_variacao = calcular_similaridade_nomes("Weverton Silva", "Weverton da Silva")
    score_typo = calcular_similaridade_nomes("Maria Josefa da Silva", "Maria Josefa de Silva")
    score_diferente = calcular_similaridade_nomes("Antonio Pereira", "Sebastião Souza")

    # Assert
    assert score_exato == 1.0
    assert score_variacao >= 0.85
    assert score_typo >= 0.90
    assert score_diferente < 0.40


def test_extracao_metadados_resposta_coletum():
    # Arrange: Resposta típica do Coletum
    mock_resposta = {
        "id": "ANS-12345",
        "created_at": "2026-05-12T14:30:00Z",
        "answer": {
            "Nome do Beneficiário": "Josefa Maria dos Santos",
            "CPF do Beneficiário": "123.456.789-00",
            "Município": "Glória",
            "Comunidade": "Quixaba",
            "Nome do Técnico Responsável": "Caroline",
            "Data da Atividade": "12/05/2026"
        }
    }

    # Act
    meta = extrair_metadados_resposta_coletum(mock_resposta)

    # Assert
    assert meta["coletum_id"] == "ANS-12345"
    assert meta["beneficiario"] == "Josefa Maria dos Santos"
    assert meta["cpf"] == "12345678900"
    assert meta["municipio"] == "Glória"
    assert meta["data_atividade"] == "12/05/2026"


@pytest.mark.asyncio
async def test_auditoria_discrepancias_coletum_com_mock(monkeypatch):
    # Arrange: Mock dos formulários e respostas do Coletum
    async def mock_listar_formularios():
        return [{"id": 37226, "name": "Formulário BSF ATER"}]

    async def mock_buscar_respostas(form_id, limit=200):
        return [
            {
                "id": "ANS-001",
                "answer": {
                    "Nome": "Maria Santoss",  # Typo proposital (similar ao BD 'Maria Santos')
                    "CPF": "11122233344",
                    "Data": "15/05/2026"  # Data diferente do Ateste no BD ('10/05/2026')
                }
            }
        ]

    import app.services.coletum_service as cs
    monkeypatch.setattr(cs, "listar_formularios_coletum", mock_listar_formularios)
    monkeypatch.setattr(cs, "buscar_respostas_formulario", mock_buscar_respostas)

    beneficiarios_mock = [
        {
            "id": 1,
            "nome_completo": "Maria Santos",
            "cpf": "111.222.333-44",
            "municipio": "Paulo Afonso",
            "nome_tecnico": "Caroline",
            "data_atividade": "10/05/2026"
        }
    ]

    # Act
    resultado = await auditar_discrepancias_coletum(beneficiarios_bd=beneficiarios_mock)

    # Assert
    assert resultado["total_formularios"] == 1
    assert resultado["total_respostas"] == 1
    discrepancia = resultado["discrepancias"][0]
    
    # Deve identificar match por CPF e marcar atenção por leve variação no nome + aviso de data
    assert discrepancia["match_beneficiario"]["nome"] == "Maria Santos"
    assert len(discrepancia["mensagens"]) >= 1
    assert "Aviso de Data" in str(discrepancia["mensagens"]) or "Divergência de grafia" in str(discrepancia["mensagens"])
