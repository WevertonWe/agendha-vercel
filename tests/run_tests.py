"""
Executor de Testes Automatizados - Bahia Sem Fome (BSF)
Executa todos os testes de unidade, integração, segurança e conformidade documental.
"""

import sys
import os
import shutil
import tempfile
import asyncio
from pathlib import Path

# Suporte a caracteres especiais no terminal Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Adiciona o diretório raiz ao sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

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

def run_all_tests():
    print("=" * 70)
    print("🚀 INICIANDO SUÍTE DE TESTES: AUDITORIA, DEDUPLICAÇÃO E COLETUM V2 (BSF)")
    print("=" * 70)

    sucessos = 0
    falhas = 0

    def test(name, func):
        nonlocal sucessos, falhas
        try:
            if asyncio.iscoroutinefunction(func):
                asyncio.run(func())
            else:
                func()
            print(f"  ✅ PASS: {name}")
            sucessos += 1
        except Exception as e:
            print(f"  ❌ FAIL: {name} -> {e}")
            import traceback
            traceback.print_exc()
            falhas += 1

    # 1. Testes de Sanitização e Segurança (Path Traversal)
    def test_sanitizacao_path_traversal():
        assert sanitizar_nome_seguro("../../etc/passwd") == "ETCPASSWD"
        assert sanitizar_nome_seguro("..\\..\\Windows\\System32") == "WINDOWSSYSTEM32"
        assert sanitizar_nome_seguro("JOSÉ / DA SILVA : TESTE") == "JOSE DA SILVA TESTE"
        assert sanitizar_nome_seguro("João   da   Silva---") == "JOAO DA SILVA---"
        assert sanitizar_nome_seguro("COMUNIDADE SÃO JOSÉ (ZONA RURAL)") == "COMUNIDADE SAO JOSE ZONA RURAL"
    test("Sanitização contra Path Traversal e Nomes Seguros", test_sanitizacao_path_traversal)

    # 2. Testes de Normalização Canônica
    def test_normalizacao_canonica():
        assert normalizar_nome_canonico("JOSÉ DA SILVA") == "JOSE DA SILVA"
        assert normalizar_nome_canonico("josé da silva") == "JOSE DA SILVA"
        assert normalizar_nome_canonico("São Francisco do Conde") == "SAO FRANCISCO DO CONDE"
        assert normalizar_nome_canonico("Érica Araújo") == "ERICA ARAUJO"
    test("Normalização Canônica de Nomes e Acentos", test_normalizacao_canonica)

    # 3. Testes de Identificação e Deduplicação de Pastas com Acentos
    def test_deduplicacao_pastas():
        with tempfile.TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir)
            pasta_acentuada = base / "SÃO PEDRO"
            pasta_sem_acento = base / "SAO PEDRO"
            pasta_acentuada.mkdir()
            pasta_sem_acento.mkdir()

            (pasta_acentuada / "doc1.txt").write_text("conteudo 1", encoding="utf-8")
            (pasta_sem_acento / "doc2.txt").write_text("conteudo 2", encoding="utf-8")

            dups = identificar_pastas_duplicadas_por_acentos(base)
            assert len(dups) == 1
            assert dups[0]["nome_canonico"] == "SAO PEDRO"
            assert len(dups[0]["pastas_existentes"]) == 2

            res = consolidar_pastas_duplicadas_segura(base)
            assert res["sucesso"] is True
            assert res["arquivos_movidos"] >= 1

            pasta_final = base / "SAO PEDRO"
            assert pasta_final.exists()
            assert (pasta_final / "doc1.txt").exists()
            assert (pasta_final / "doc2.txt").exists()
            assert not pasta_acentuada.exists()
    test("Identificação e Consolidação Segura de Pastas Duplicadas (Acentos)", test_deduplicacao_pastas)

    # 4. Testes de Conformidade Documental (Pares Ateste + Coletum)
    def test_conformidade_atividades():
        with tempfile.TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir)

            # Completa
            p1 = base / "28.04.2026 - PLANO"
            p1.mkdir()
            (p1 / "JOSE - ATESTE.pdf").write_bytes(b"%PDF-1.4")
            (p1 / "JOSE - COLLETUM.pdf").write_bytes(b"%PDF-1.4")
            conf1 = verificar_conformidade_atividade(p1)
            assert conf1["status"] == "COMPLETO"

            # Só Coletum
            p2 = base / "29.04.2026 - PLANO"
            p2.mkdir()
            (p2 / "MARIA - COLLETUM.pdf").write_bytes(b"%PDF-1.4")
            conf2 = verificar_conformidade_atividade(p2)
            assert conf2["status"] == "PENDENTE_ATESTE"

            # Só Ateste
            p3 = base / "30.04.2026 - PLANO"
            p3.mkdir()
            (p3 / "CARLOS - ATESTE.pdf").write_bytes(b"%PDF-1.4")
            conf3 = verificar_conformidade_atividade(p3)
            assert conf3["status"] == "PENDENTE_COLETUM"
    test("Classificação de Conformidade Documental (Ateste + Coletum)", test_conformidade_atividades)

    # 5. Testes de Auditoria Completa da Árvore de Diretórios
    def test_auditoria_completa_arvore():
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            pasta_tec = base_dir / "caroline" / "documentos-atividades" / "CENTRO" / "MARIA SANTOS"
            pasta_ativ = pasta_tec / "10.05.2026 - VISITA"
            pasta_ativ.mkdir(parents=True)

            (pasta_ativ / "MARIA SANTOS - ATESTE.pdf").write_bytes(b"%PDF-1.4")
            (pasta_ativ / "MARIA SANTOS - COLLETUM.pdf").write_bytes(b"%PDF-1.4")

            res = executar_auditoria_completa_pastas_locais(base_dir=base_dir)
            resumo = res["resumo"]
            assert resumo["total_tecnicos"] == 1
            assert resumo["total_comunidades"] == 1
            assert resumo["total_beneficiarios"] == 1
            assert resumo["total_atividades"] == 1
            assert resumo["atividades_completas"] == 1
            assert resumo["percentual_conformidade"] == 100.0
    test("Varredura e Auditoria Completa da Estrutura de Diretórios", test_auditoria_completa_arvore)

    # 6. Testes de Similaridade de Nomes (Levenshtein)
    def test_similaridade_fuzzy():
        assert calcular_similaridade_nomes("Weverton Silva", "Weverton Silva") == 1.0
        assert calcular_similaridade_nomes("Weverton Silva", "Weverton da Silva") >= 0.85
        assert calcular_similaridade_nomes("Maria Josefa da Silva", "Maria Josefa de Silva") >= 0.90
        assert calcular_similaridade_nomes("Antonio Pereira", "Sebastião Souza") < 0.50
    test("Cálculo de Similaridade Difusa de Nomes (Fuzzy Matching)", test_similaridade_fuzzy)

    # 7. Testes de Extração de Resposta Coletum
    def test_extracao_coletum():
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
        meta = extrair_metadados_resposta_coletum(mock_resposta)
        assert meta["coletum_id"] == "ANS-12345"
        assert meta["beneficiario"] == "Josefa Maria dos Santos"
        assert meta["cpf"] == "12345678900"
        assert meta["municipio"] == "Glória"
        assert meta["data_atividade"] == "12/05/2026"
    test("Extração Dinâmica de Metadados da Resposta Coletum", test_extracao_coletum)

    # 8. Teste Assíncrono de Cruzamento Coletum & Detecção de Discrepâncias
    async def test_cruzamento_coletum_discrepancias():
        import app.services.coletum_service as cs
        original_listar = cs.listar_formularios_coletum
        original_buscar = cs.buscar_respostas_formulario

        try:
            async def mock_listar():
                return [{"id": 37226, "name": "Formulário BSF ATER"}]

            async def mock_buscar(form_id, limit=200):
                return [
                    {
                        "id": "ANS-001",
                        "answer": {
                            "Nome": "Maria Santoss",  # Typo leve
                            "CPF": "11122233344",
                            "Data": "15/05/2026"  # Data divergente
                        }
                    }
                ]

            cs.listar_formularios_coletum = mock_listar
            cs.buscar_respostas_formulario = mock_buscar

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

            resultado = await auditar_discrepancias_coletum(beneficiarios_bd=beneficiarios_mock)
            assert resultado["total_formularios"] == 1
            assert resultado["total_respostas"] == 1
            item = resultado["discrepancias"][0]
            assert item["match_beneficiario"]["nome"] == "Maria Santos"
            assert len(item["mensagens"]) >= 1
        finally:
            cs.listar_formularios_coletum = original_listar
            cs.buscar_respostas_formulario = original_buscar

    test("Cruzamento Coletum v2 com Detecção de Discrepâncias de Nomes e Datas", test_cruzamento_coletum_discrepancias)

    print("=" * 70)
    print(f"📊 RESUMO DOS TESTES: {sucessos} Passaram, {falhas} Falharam.")
    print("=" * 70)

    if falhas > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_all_tests()
