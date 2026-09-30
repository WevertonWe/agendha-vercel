import os
import sys
import json
from pathlib import Path

# Suporte ao carregamento do SQLite no Windows caso dependências GIS estejam presentes
if sys.platform == "win32":
    qgis_path = r"C:\Program Files\QGIS 3.44.12\bin"
    if os.path.exists(qgis_path):
        try:
            os.add_dll_directory(qgis_path)
        except Exception:
            pass

# Garante raiz do projeto no path
ROOT_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(ROOT_DIR))

from app.modules.bahia_sem_fome.services.sigater_hub_service import (
    calcular_competencia_mes_contrato,
    gerar_script_f12_dinamico,
    salvar_pendencias_no_banco,
    listar_pendencias_do_banco,
    alterar_status_pendencia,
    remover_pendencia,
    ATIVIDADES_BSF
)
from fastapi.testclient import TestClient
from app.main import app


def test_calcular_competencia_mes_contrato():
    """Testa os cálculos de competência para diversos meses do contrato."""
    # Mês 1: Julho/2024, Ano 1
    c1 = calcular_competencia_mes_contrato(1)
    assert c1["mes"] == 7
    assert c1["ano"] == 2024
    assert c1["ano_contrato"] == 1
    assert "Julho" in c1["nome_mes"]

    # Mês 17: Novembro/2025, Ano 2
    c17 = calcular_competencia_mes_contrato(17)
    assert c17["mes"] == 11
    assert c17["ano"] == 2025
    assert c17["ano_contrato"] == 2
    assert "Novembro" in c17["nome_mes"]

    # Mês 22: Abril/2026, Ano 2
    c22 = calcular_competencia_mes_contrato(22)
    assert c22["mes"] == 4
    assert c22["ano"] == 2026
    assert c22["ano_contrato"] == 2
    assert "Abril" in c22["nome_mes"]

    # Mês 23: Maio/2026, Ano 2
    c23 = calcular_competencia_mes_contrato(23)
    assert c23["mes"] == 5
    assert c23["ano"] == 2026
    assert c23["ano_contrato"] == 2
    assert "Maio" in c23["nome_mes"]

    # Mês 24: Junho/2026, Ano 2
    c24 = calcular_competencia_mes_contrato(24)
    assert c24["mes"] == 6
    assert c24["ano"] == 2026
    assert c24["ano_contrato"] == 2
    assert "Junho" in c24["nome_mes"]

    # Mês 25: Julho/2026, Ano 3
    c25 = calcular_competencia_mes_contrato(25)
    assert c25["mes"] == 7
    assert c25["ano"] == 2026
    assert c25["ano_contrato"] == 3
    assert "Julho" in c25["nome_mes"]


def test_gerar_script_f12_dinamico():
    """Valida se o gerador cria o script em JavaScript com a sintaxe correta."""
    beneficiarios_exemplo = [
        {
            "beneficiario_nome": "MARIA DA SILVA",
            "beneficiario_cpf": "123.456.789-00",
            "tecnico_nome": "JOAO TECNICO",
            "comunidade": "COMUNIDADE BOA VISTA",
            "municipio": "CANUDOS",
            "data_coletum": "15/06/2026"
        }
    ]

    script = gerar_script_f12_dinamico(
        atividade_codigo="PLANO_PRODUTIVO",
        mes_contrato=24,
        beneficiarios=beneficiarios_exemplo
    )

    assert isinstance(script, str)
    assert "MARIA DA SILVA" in script
    assert "Plano Produtivo" in script
    assert "btnCopiarTudoAgendha" in script
    assert "Copiar Todos" in script
    assert "navigator.clipboard.writeText" in script


def test_salvar_e_listar_pendencias_estruturado():
    """Testa o salvamento e listagem de pendências via lista estruturada."""
    pendentes = [
        {
            "beneficiario": "TESTE BENEFICIARIO ESTRUTURADO",
            "cpf": "999.888.777-66",
            "tecnico": "TECNICO TESTE",
            "comunidade": "ASSENTAMENTO TESTE",
            "municipio": "UAUA",
            "data": "10/06/2026"
        }
    ]

    resultado = salvar_pendencias_no_banco(
        mes_contrato=99,
        mes_ano_referencia="06/2026",
        atividade_nome="Visita Técnica Individual",
        pendentes=pendentes
    )
    assert resultado["total_processados"] >= 1

    # Listar
    itens = listar_pendencias_do_banco(mes_contrato=99, atividade_nome="Visita Técnica Individual")
    assert len(itens) >= 1
    item_encontrado = next((i for i in itens if i["beneficiario_nome"] == "TESTE BENEFICIARIO ESTRUTURADO"), None)
    assert item_encontrado is not None
    assert item_encontrado["status"] == "PENDENTE"

    # Alternar status
    sucesso_status = alterar_status_pendencia(item_encontrado["id"], "RESOLVIDO")
    assert sucesso_status is True

    itens_apos = listar_pendencias_do_banco(mes_contrato=99, atividade_nome="Visita Técnica Individual")
    item_atualizado = next(i for i in itens_apos if i["id"] == item_encontrado["id"])
    assert item_atualizado["status"] == "RESOLVIDO"

    # Remover para limpeza do teste
    removido = remover_pendencia(item_encontrado["id"])
    assert removido is True


def test_api_sigater_hub_endpoints():
    """Testa os endpoints HTTP do roteador SIGATER Hub."""
    client = TestClient(app)

    # 1. Configurações
    resp = client.get("/api/bsf/sigater-hub/configuracoes")
    assert resp.status_code == 200
    dados = resp.json()
    assert "meses" in dados
    assert "atividades" in dados
    assert len(dados["meses"]) == 36
    assert len(dados["atividades"]) == len(ATIVIDADES_BSF)

    # 2. Salvar pendência via API com texto colado
    texto_sigater = "1. FULANO DA SILVA TESTE API | CPF: 000.111.222-33 | Técnico: Carlos - Riacho (Uauá) | Data: 10/10/2025"
    resp_salvar = client.post(
        "/api/bsf/sigater-hub/salvar-pendencias",
        json={
            "mes_contrato": 97,
            "atividade_nome": "Cadastro Familiar",
            "conteudo_colado": texto_sigater
        }
    )
    assert resp_salvar.status_code == 200
    res_salvar_data = resp_salvar.json()
    assert res_salvar_data["total_processados"] == 1

    # 3. Listar pendências via API
    resp_listar = client.get("/api/bsf/sigater-hub/pendencias?mes_contrato=97&atividade_nome=Cadastro")
    assert resp_listar.status_code == 200
    res_listar_data = resp_listar.json()
    assert res_listar_data["total"] >= 1
    item_id = res_listar_data["pendencias"][0]["id"]

    # 4. Alterar status via API
    resp_status = client.patch(
        f"/api/bsf/sigater-hub/pendencias/{item_id}/status",
        json={"status": "RESOLVIDO"}
    )
    assert resp_status.status_code == 200

    # 5. Atualizar Nome do Beneficiário e Código via PATCH
    resp_edit_nome = client.patch(
        f"/api/bsf/sigater-hub/pendencias/{item_id}/codigo",
        json={
            "codigo_sigater": "633530",
            "beneficiario_nome": "MARIA JOSE CORRIGIDA",
            "beneficiario_cpf": "999.888.777-66",
            "tecnico": "Caroline Silva",
            "comunidade": "Serrota",
            "municipio": "Glória",
            "status": "LANCADO"
        }
    )
    assert resp_edit_nome.status_code == 200
    res_edit_data = resp_edit_nome.json()
    assert res_edit_data["sucesso"] is True
    assert res_edit_data["codigo_sigater"] == "633530"

    # Confirma que o nome e dados foram atualizados no banco
    resp_listar_atualizado = client.get("/api/bsf/sigater-hub/pendencias?mes_contrato=97&atividade_nome=Cadastro")
    assert resp_listar_atualizado.status_code == 200
    item_editado = next((i for i in resp_listar_atualizado.json()["pendencias"] if i["id"] == item_id), None)
    assert item_editado is not None
    assert item_editado["beneficiario_nome"] == "MARIA JOSE CORRIGIDA"
    assert item_editado["beneficiario_cpf"] == "999.888.777-66"
    assert item_editado["codigo_sigater"] == "633530"
    assert item_editado["status"] == "LANCADO"

    # 6. Salvar apenas_sigater (SEM_COLETUM) e validar
    resp_sem_coletum = client.post(
        "/api/bsf/sigater-hub/salvar-pendencias",
        json={
            "mes_contrato": 97,
            "atividade_nome": "Cadastro Familiar",
            "apenas_sigater": [{
                "beneficiario": "TESTE DIVERGENCIA SEM COLETUM",
                "cpf": "111.222.333-44",
                "tecnico": "SIGATER (Sem Coletum)",
                "codigo_sigater": "463753",
                "link_sigater": "https://sigater.ba.gov.br/execucao/read/463753",
                "status": "SEM_COLETUM"
            }]
        }
    )
    assert resp_sem_coletum.status_code == 200
    res_sem_coletum_data = resp_sem_coletum.json()
    assert res_sem_coletum_data["total_apenas_sigater"] == 1

    # Listar com filtro de status SEM_COLETUM
    resp_listar_sc = client.get("/api/bsf/sigater-hub/pendencias?mes_contrato=97&status=SEM_COLETUM")
    assert resp_listar_sc.status_code == 200
    itens_sc = resp_listar_sc.json()["pendencias"]
    assert len(itens_sc) >= 1
    assert any(i["codigo_sigater"] == "463753" for i in itens_sc)

    # Limpeza
    client.delete(f"/api/bsf/sigater-hub/pendencias/{item_id}")
    for item in itens_sc:
        if item["beneficiario_nome"] == "TESTE DIVERGENCIA SEM COLETUM":
            client.delete(f"/api/bsf/sigater-hub/pendencias/{item['id']}")


if __name__ == "__main__":
    print("Executando testes da suite SIGATER Hub...")
    test_calcular_competencia_mes_contrato()
    print("  [OK] test_calcular_competencia_mes_contrato")
    test_gerar_script_f12_dinamico()
    print("  [OK] test_gerar_script_f12_dinamico")
    test_salvar_e_listar_pendencias_estruturado()
    print("  [OK] test_salvar_e_listar_pendencias_estruturado")
    test_api_sigater_hub_endpoints()
    print("  [OK] test_api_sigater_hub_endpoints")
    print("\nTODOS OS TESTES DO SIGATER HUB PASSARAM COM SUCESSO!")

