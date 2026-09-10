"""
Serviço de Auditoria Local, Deduplicação e Conformidade Documental - Bahia Sem Fome (BSF)
Responsável por:
1. Normalização rigorosa de texto e caminhos (anti-path traversal).
2. Deduplicação e consolidação segura de pastas com/sem acentos (ex: JOSÉ vs JOSE).
3. Verificação da presença obrigatória dos pares de documentos (ATESTE e COLLETUM) por atividade.
4. Geração de relatórios e persistência de snapshots para consulta remota (Vercel).
"""

import os
import re
import shutil
import logging
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict

from app.services.scanner_service import get_base_storage_path, DEFAULT_STORAGE_PATH

logger = logging.getLogger(__name__)

# Cache em memória do último snapshot de auditoria
_ULTIMO_SNAPSHOT_AUDITORIA: Optional[Dict[str, Any]] = None


def sanitizar_nome_seguro(texto: str) -> str:
    """
    Remove caracteres perigosos para evitar Path Traversal (CWE-22)
    e garante nome alfanumérico seguro para diretórios Windows.
    """
    if not texto:
        return ""
    # Remove qualquer tentativa de navegação relativa ou caracteres inválidos no Windows
    texto = texto.replace("..", "").replace("/", "").replace("\\", "").replace(":", "")
    # Normaliza unicode
    nfkd = unicodedata.normalize('NFKD', texto)
    sem_acento = "".join([c for c in nfkd if not unicodedata.combining(c)])
    # Permite apenas letras, números, espaços, hífens e sublinhados
    limpo = re.sub(r'[^a-zA-Z0-9\s\-_]', '', sem_acento)
    return re.sub(r'\s+', ' ', limpo).strip().upper()


def normalizar_nome_canonico(texto: str) -> str:
    """
    Gera a chave canônica para agrupamento e deduplicação (sem acentos, maiúsculo).
    Ex: 'JOSÉ DA SILVA' -> 'JOSE DA SILVA', 'SÃO PEDRO' -> 'SAO PEDRO'
    """
    return sanitizar_nome_seguro(texto)


def extrair_categoria_atividade(nome_pasta: str) -> str:
    """
    Identifica e padroniza a categoria da atividade pelo nome da pasta.
    Exemplos:
    - '23.10.2025 - PLANO PRODUTIVO' -> 'PLANO PRODUTIVO'
    - '24.07.2025 - SOCIOECONOMICO' -> 'SOCIOECONÔMICO'
    - '10.09.2025 - CARACTERIZAÇÃO' -> 'CARACTERIZAÇÃO'
    - '07.07.2026 - VISITA TÉCNICA AVALIATIVA' -> 'VISITA TÉCNICA AVALIATIVA'
    - '18.06.2026 - VISITA TECNICA' -> 'VISITA TÉCNICA'
    """
    if not nome_pasta:
        return "OUTROS"
    
    n = sanitizar_nome_seguro(nome_pasta)
    
    if "PLANO PRODUTIVO" in n or "PLANO" in n:
        return "PLANO PRODUTIVO"
    if "SOCIOECONOMICO" in n or "SOCIO" in n or "GEOLOCALIZACAO" in n:
        return "SOCIOECONÔMICO"
    if "CARACTERIZACAO" in n or "UPF" in n:
        return "CARACTERIZAÇÃO"
    if "AVALIATIVA" in n:
        return "VISITA TÉCNICA AVALIATIVA"
    if "VISITA TECNICA" in n or "VISITA SOCIAL" in n or "VISITA" in n:
        return "VISITA TÉCNICA"
    if "GRUPO FAMILIAR" in n or "CADASTRO" in n:
        return "CADASTRO GRUPO FAMILIAR"
    if "OFICINA" in n:
        return "OFICINA TEMÁTICA"
    if "CAMPO" in n:
        return "DIA DE CAMPO"
    if "CURSO" in n:
        return "CURSO"
    if "SEMINARIO" in n:
        return "SEMINÁRIO"
    
    return "OUTROS"


def identificar_pastas_duplicadas_por_acentos(diretorio_pai: Path) -> List[Dict[str, Any]]:
    """
    Varre os subdiretórios de um diretório e agrupa por nome canônico normalizado.
    Detecta quando existem múltiplas pastas que divergem apenas por acentuação ou caixa alta/baixa.
    """
    if not diretorio_pai.exists() or not diretorio_pai.is_dir():
        return []

    grupos: Dict[str, List[Path]] = {}
    for item in diretorio_pai.iterdir():
        if item.is_dir():
            canonico = normalizar_nome_canonico(item.name)
            if not canonico:
                continue
            if canonico not in grupos:
                grupos[canonico] = []
            grupos[canonico].append(item)

    duplicadas = []
    for canonico, pastas in grupos.items():
        if len(pastas) > 1:
            # Temos duplicidade de pastas (ex: 'JOSÉ' e 'JOSE')
            pasta_canonica_alvo = diretorio_pai / canonico
            duplicadas.append({
                "nome_canonico": canonico,
                "pasta_alvo": str(pasta_canonica_alvo),
                "pastas_existentes": [str(p) for p in pastas],
                "nomes_pastas": [p.name for p in pastas],
                "quantidade": len(pastas)
            })

    return duplicadas


def consolidar_pastas_duplicadas_segura(diretorio_pai: Path) -> Dict[str, Any]:
    """
    Unifica com total segurança pastas duplicadas para o nome canônico (sem acento, maiúsculo).
    Move todos os arquivos e subpastas preservando conteúdo e removendo pastas vazias redundantes.
    """
    if not diretorio_pai.exists() or not diretorio_pai.is_dir():
        return {"sucesso": False, "mensagem": "Diretório inexistente", "movidos": 0}

    grupos_duplicados = identificar_pastas_duplicadas_por_acentos(diretorio_pai)
    total_movidos = 0
    pastas_removidas = []
    erros = []

    for grupo in grupos_duplicados:
        canonico = grupo["nome_canonico"]
        pasta_alvo = diretorio_pai / canonico
        pasta_alvo.mkdir(parents=True, exist_ok=True)

        for caminho_str in grupo["pastas_existentes"]:
            pasta_origem = Path(caminho_str)
            # Se a pasta de origem for exatamente o caminho alvo, não mexe nela
            if pasta_origem.resolve() == pasta_alvo.resolve():
                continue

            try:
                # Move recursivamente arquivos e subdiretórios
                for item in list(pasta_origem.iterdir()):
                    destino_item = pasta_alvo / item.name
                    if item.is_dir():
                        if destino_item.exists() and destino_item.is_dir():
                            # Mescla subpastas recursivamente
                            for sub_file in list(item.iterdir()):
                                sub_dest = destino_item / sub_file.name
                                if not sub_dest.exists():
                                    shutil.move(str(sub_file), str(sub_dest))
                                    total_movidos += 1
                                else:
                                    if sub_file.is_file() and sub_dest.is_file() and sub_file.stat().st_size == sub_dest.stat().st_size:
                                        sub_file.unlink()
                                    else:
                                        novo_nome = f"{sub_file.stem}_duplicado_{int(datetime.now().timestamp())}{sub_file.suffix}"
                                        shutil.move(str(sub_file), str(destino_item / novo_nome))
                                        total_movidos += 1
                            # Remove subpasta esvaziada
                            try:
                                item.rmdir()
                            except OSError:
                                shutil.rmtree(item, ignore_errors=True)
                        else:
                            shutil.move(str(item), str(destino_item))
                            total_movidos += 1
                    else:
                        if not destino_item.exists():
                            shutil.move(str(item), str(destino_item))
                            total_movidos += 1
                        else:
                            # Se colidir com mesmo arquivo, verifica se é idêntico
                            if item.stat().st_size == destino_item.stat().st_size:
                                item.unlink()  # Já temos cópia idêntica
                            else:
                                novo_nome = f"{item.stem}_copia_{int(datetime.now().timestamp())}{item.suffix}"
                                shutil.move(str(item), str(pasta_alvo / novo_nome))
                                total_movidos += 1

                # Tenta remover pasta de origem agora vazia
                try:
                    pasta_origem.rmdir()
                    pastas_removidas.append(pasta_origem.name)
                except OSError:
                    # Se sobrou algo oculto
                    shutil.rmtree(pasta_origem, ignore_errors=True)
                    pastas_removidas.append(pasta_origem.name)

            except Exception as e:
                logger.error(f"Erro ao consolidar pasta '{pasta_origem}': {e}")
                erros.append({"pasta": str(pasta_origem), "erro": str(e)})

    return {
        "sucesso": len(erros) == 0,
        "pastas_duplicadas_detectadas": len(grupos_duplicados),
        "pastas_removidas": pastas_removidas,
        "arquivos_movidos": total_movidos,
        "erros": erros
    }


def consolidar_atividades_complementares_beneficiario(pasta_beneficiario: Path) -> Dict[str, Any]:
    """
    Identifica se um mesmo beneficiário possui atividades da mesma categoria
    divididas em pastas diferentes (ex: uma pasta com o Ateste e outra com o Coletum)
    e consolida tudo em uma única pasta completa (priorizando a data original do Coletum).
    """
    if not pasta_beneficiario.exists() or not pasta_beneficiario.is_dir():
        return {"mescladas": 0, "arquivos_movidos": 0, "pastas_removidas": 0}

    por_categoria = defaultdict(list)
    for sub in pasta_beneficiario.iterdir():
        if sub.is_dir():
            cat = extrair_categoria_atividade(sub.name)
            pdfs = list(sub.glob("*.pdf"))
            tem_ateste = any("ATEST" in f.name.upper() for f in pdfs)
            tem_coletum = any("COL" in f.name.upper() for f in pdfs)
            por_categoria[cat].append({
                "pasta": sub,
                "nome": sub.name,
                "pdfs": pdfs,
                "tem_ateste": tem_ateste,
                "tem_coletum": tem_coletum
            })

    mescladas = 0
    arquivos_movidos = 0
    pastas_removidas = 0

    for cat, lista in por_categoria.items():
        if cat == "OUTROS":
            continue

        # 1. Remove pastas vazias
        for p in list(lista):
            if len(p["pdfs"]) == 0:
                try:
                    shutil.rmtree(str(p["pasta"]), ignore_errors=True)
                    pastas_removidas += 1
                    lista.remove(p)
                except Exception:
                    pass

        # 2. Se sobrou mais de uma pasta para a mesma categoria de atividade
        if len(lista) > 1:
            tem_at = any(p["tem_ateste"] for p in lista)
            tem_col = any(p["tem_coletum"] for p in lista)

            # Se temos ateste em uma e coletum em outra
            if tem_at and tem_col:
                # Pasta destino: prioriza a pasta que já tem o Coletum (data original de campo)
                pasta_destino_info = next((p for p in lista if p["tem_coletum"]), lista[0])
                pasta_destino = pasta_destino_info["pasta"]

                for pasta_origem_info in lista:
                    if pasta_origem_info["pasta"] == pasta_destino:
                        continue

                    pasta_origem = pasta_origem_info["pasta"]
                    for f in list(pasta_origem.glob("*")):
                        if f.is_file():
                            f_dest = pasta_destino / f.name
                            if not f_dest.exists():
                                shutil.move(str(f), str(f_dest))
                                arquivos_movidos += 1
                            else:
                                if f.stat().st_size != f_dest.stat().st_size:
                                    f_dest_alt = pasta_destino / f"ATEST_{f.name}"
                                    shutil.move(str(f), str(f_dest_alt))
                                    arquivos_movidos += 1
                                else:
                                    f.unlink(missing_ok=True)

                    # Remove pasta de origem esvaziada
                    try:
                        shutil.rmtree(str(pasta_origem), ignore_errors=True)
                        pastas_removidas += 1
                    except Exception:
                        pass

                mescladas += 1

    return {
        "mescladas": mescladas,
        "arquivos_movidos": arquivos_movidos,
        "pastas_removidas": pastas_removidas
    }


def consolidar_todas_atividades_divididas(base_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Varre todos os técnicos, comunidades e beneficiários, unificando pastas de
    atividades complementares divididas (Ateste em uma e Coletum em outra).
    """
    caminho_base = base_dir or get_base_storage_path()
    total_mescladas = 0
    total_movidos = 0
    total_removidas = 0

    if not caminho_base.exists():
        return {
            "sucesso": False,
            "total_atividades_mescladas": 0,
            "total_arquivos_movidos": 0,
            "total_pastas_removidas": 0
        }

    ignorar = {"ATESTES", "CARACTERIZAÇÃO", "CARACTERIZACAO", "PLANOS PRODUTIVOS", "TEMP", "UPLOADS", "_IMPORTACOES_PENDENTES_REVISAO"}

    for tec in caminho_base.iterdir():
        if not tec.is_dir() or tec.name.startswith("_") or tec.name.upper() in ignorar:
            continue
        doc_ativ = tec / "documentos-atividades"
        alvo = doc_ativ if doc_ativ.exists() else tec

        for com in alvo.iterdir():
            if not com.is_dir() or com.name.upper() == "ATIVIDADE COLETIVA":
                continue

            for benef in com.iterdir():
                if benef.is_dir():
                    res = consolidar_atividades_complementares_beneficiario(benef)
                    total_mescladas += res["mescladas"]
                    total_movidos += res["arquivos_movidos"]
                    total_removidas += res["pastas_removidas"]

    return {
        "sucesso": True,
        "total_atividades_mescladas": total_mescladas,
        "total_arquivos_movidos": total_movidos,
        "total_pastas_removidas": total_removidas
    }


def verificar_conformidade_atividade(pasta_atividade: Path) -> Dict[str, Any]:
    """
    Analisa os arquivos dentro de uma pasta de atividade de beneficiário
    (ex: '28.04.2026 - PLANO PRODUTIVO' ou '15.05.2026').
    Retorna se possui Ateste, Coletum e seus respectivos arquivos.
    """
    tem_ateste = False
    tem_coletum = False
    arquivos_ateste = []
    arquivos_coletum = []
    outros_arquivos = []

    if not pasta_atividade.exists() or not pasta_atividade.is_dir():
        return {
            "status": "INEXISTENTE",
            "tem_ateste": False,
            "tem_coletum": False,
            "arquivos": []
        }

    for f in pasta_atividade.iterdir():
        if f.is_file():
            nome_upper = f.name.upper()
            ext = f.suffix.lower()

            if ext in [".pdf", ".docx", ".doc"]:
                if "ATESTE" in nome_upper:
                    tem_ateste = True
                    arquivos_ateste.append(f.name)
                elif "COLLETUM" in nome_upper or "COLETUM" in nome_upper:
                    tem_coletum = True
                    arquivos_coletum.append(f.name)
                else:
                    outros_arquivos.append(f.name)
            else:
                outros_arquivos.append(f.name)

    if tem_ateste and tem_coletum:
        status = "COMPLETO"
    elif tem_coletum and not tem_ateste:
        status = "PENDENTE_ATESTE"
    elif tem_ateste and not tem_coletum:
        status = "PENDENTE_COLETUM"
    else:
        status = "VAZIA" if not (arquivos_ateste or arquivos_coletum or outros_arquivos) else "SEM_DOCUMENTOS_PADRAO"

    return {
        "status": status,
        "tem_ateste": tem_ateste,
        "tem_coletum": tem_coletum,
        "arquivos_ateste": arquivos_ateste,
        "arquivos_coletum": arquivos_coletum,
        "outros_arquivos": outros_arquivos
    }


def executar_auditoria_completa_pastas_locais(
    base_dir: Optional[Path] = None,
    auto_consolidar_acentos: bool = False
) -> Dict[str, Any]:
    """
    Realiza a varredura completa da estrutura de técnicos e beneficiários:
    BASE_DIR / [TECNICO] / documentos-atividades / [COMUNIDADE] / [BENEFICIARIO] / [ATIVIDADE]
    """
    global _ULTIMO_SNAPSHOT_AUDITORIA
    caminho_base = base_dir or get_base_storage_path()

    resultado = {
        "timestamp": datetime.now().isoformat(),
        "data_formatada": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "base_storage_path": str(caminho_base),
        "storage_existe": caminho_base.exists(),
        "resumo": {
            "total_tecnicos": 0,
            "total_comunidades": 0,
            "total_beneficiarios": 0,
            "total_atividades": 0,
            "atividades_completas": 0,
            "pendentes_ateste": 0,
            "pendentes_coletum": 0,
            "vazias_ou_erro": 0,
            "total_pastas_duplicadas_acentos": 0,
            "percentual_conformidade": 0.0,
            "por_atividade": {},
            "lista_atividades": []
        },
        "duplicidades_detectadas": [],
        "tecnicos": {},
        "detalhes_beneficiarios": []
    }

    if not caminho_base.exists():
        logger.warning(f"Caminho base de armazenamento não encontrado: {caminho_base}")
        _ULTIMO_SNAPSHOT_AUDITORIA = resultado
        return resultado

    ignorar_pastas = {
        "ATESTES", "DOCUMENTOS", "UPLOADS", "TEMP", "__PYCACHE__", ".GIT",
        "ANDERLAINE", "CARACTERIZAÇÃO", "CARACTERIZACAO", "PLANOS PRODUTIVOS",
        "_IMPORTACOES_PENDENTES_REVISAO", "ATIVIDADES BAIXADAS"
    }

    # 1. Varre Técnicos
    pastas_tecnicos = [
        p for p in caminho_base.iterdir()
        if p.is_dir() and p.name.upper() not in ignorar_pastas and not p.name.startswith("_")
    ]
    resultado["resumo"]["total_tecnicos"] = len(pastas_tecnicos)

    for pasta_tec in pastas_tecnicos:
        nome_tec = pasta_tec.name
        doc_ativ = pasta_tec / "documentos-atividades"
        if not doc_ativ.exists():
            doc_ativ = pasta_tec

        # Checagem de pastas duplicadas de comunidades
        dups_comunidades = identificar_pastas_duplicadas_por_acentos(doc_ativ)
        if dups_comunidades:
            resultado["duplicidades_detectadas"].extend(dups_comunidades)
            if auto_consolidar_acentos:
                consolidar_pastas_duplicadas_segura(doc_ativ)

        comunidades_pastas = [
            c for c in doc_ativ.iterdir()
            if c.is_dir() and "ATIVIDADE COLETIVA" not in c.name.upper() and "ATIVIDADES COLETIVAS" not in c.name.upper()
        ]
        resultado["resumo"]["total_comunidades"] += len(comunidades_pastas)

        resumo_tec = {
            "nome": nome_tec,
            "total_beneficiarios": 0,
            "total_atividades": 0,
            "atividades_completas": 0,
            "pendentes_ateste": 0,
            "pendentes_coletum": 0,
            "vazias": 0
        }

        for pasta_com in comunidades_pastas:
            nome_com = pasta_com.name

            # Checagem de pastas duplicadas de beneficiários nesta comunidade
            dups_benef = identificar_pastas_duplicadas_por_acentos(pasta_com)
            if dups_benef:
                resultado["duplicidades_detectadas"].extend(dups_benef)
                if auto_consolidar_acentos:
                    consolidar_pastas_duplicadas_segura(pasta_com)

            # Filtra apenas pastas que possuam documentos (ignora pastas 100% vazias)
            benef_pastas = []
            for b in pasta_com.iterdir():
                if b.is_dir():
                    tem_pdfs = any(b.glob("**/*.pdf"))
                    if tem_pdfs:
                        benef_pastas.append(b)
                    else:
                        # Remove pasta vazia órfã
                        shutil.rmtree(str(b), ignore_errors=True)

            resumo_tec["total_beneficiarios"] += len(benef_pastas)
            resultado["resumo"]["total_beneficiarios"] += len(benef_pastas)

            for pasta_benef in benef_pastas:
                nome_benef = pasta_benef.name

                # Varre atividades do beneficiário (pastas de data / plano)
                atividades_pastas = [a for a in pasta_benef.iterdir() if a.is_dir()]
                
                # Se não houver subpastas de atividade, mas tiver arquivos soltos na pasta do beneficiário
                if not atividades_pastas and list(pasta_benef.glob("*.pdf")):
                    atividades_pastas = [pasta_benef]

                resumo_tec["total_atividades"] += len(atividades_pastas)
                resultado["resumo"]["total_atividades"] += len(atividades_pastas)

                atividades_info = []
                for pasta_ativ in atividades_pastas:
                    conf = verificar_conformidade_atividade(pasta_ativ)
                    status = conf["status"]
                    nome_exibicao_ativ = pasta_ativ.name if pasta_ativ != pasta_benef else "DOCUMENTOS_GERAIS"
                    cat_ativ = extrair_categoria_atividade(nome_exibicao_ativ)

                    if cat_ativ not in resultado["resumo"]["por_atividade"]:
                        resultado["resumo"]["por_atividade"][cat_ativ] = {
                            "total": 0,
                            "completas": 0,
                            "pendentes_ateste": 0,
                            "pendentes_coletum": 0,
                            "vazias": 0
                        }
                    resultado["resumo"]["por_atividade"][cat_ativ]["total"] += 1

                    if status == "COMPLETO":
                        resumo_tec["atividades_completas"] += 1
                        resultado["resumo"]["atividades_completas"] += 1
                        resultado["resumo"]["por_atividade"][cat_ativ]["completas"] += 1
                    elif status == "PENDENTE_ATESTE":
                        resumo_tec["pendentes_ateste"] += 1
                        resultado["resumo"]["pendentes_ateste"] += 1
                        resultado["resumo"]["por_atividade"][cat_ativ]["pendentes_ateste"] += 1
                    elif status == "PENDENTE_COLETUM":
                        resumo_tec["pendentes_coletum"] += 1
                        resultado["resumo"]["pendentes_coletum"] += 1
                        resultado["resumo"]["por_atividade"][cat_ativ]["pendentes_coletum"] += 1
                    else:
                        resumo_tec["vazias"] += 1
                        resultado["resumo"]["vazias_ou_erro"] += 1
                        resultado["resumo"]["por_atividade"][cat_ativ]["vazias"] += 1

                    atividades_info.append({
                        "pasta_atividade": nome_exibicao_ativ,
                        "categoria": cat_ativ,
                        "status": status,
                        "tem_ateste": conf["tem_ateste"],
                        "tem_coletum": conf["tem_coletum"],
                        "arquivos_ateste": conf["arquivos_ateste"],
                        "arquivos_coletum": conf["arquivos_coletum"],
                        "outros_arquivos": conf["outros_arquivos"]
                    })

                resultado["detalhes_beneficiarios"].append({
                    "tecnico": nome_tec,
                    "comunidade": nome_com,
                    "beneficiario": nome_benef,
                    "caminho_relativo": str(pasta_benef.relative_to(caminho_base)),
                    "total_atividades": len(atividades_pastas),
                    "atividades": atividades_info
                })

        resultado["tecnicos"][nome_tec] = resumo_tec

    # Percentual de conformidade geral
    total_ativ = resultado["resumo"]["total_atividades"]
    total_comp = resultado["resumo"]["atividades_completas"]
    if total_ativ > 0:
        resultado["resumo"]["percentual_conformidade"] = round((total_comp / total_ativ) * 100, 1)
    else:
        resultado["resumo"]["percentual_conformidade"] = 100.0

    resultado["resumo"]["lista_atividades"] = sorted(list(resultado["resumo"]["por_atividade"].keys()))
    resultado["resumo"]["total_pastas_duplicadas_acentos"] = len(resultado["duplicidades_detectadas"])

    _ULTIMO_SNAPSHOT_AUDITORIA = resultado
    logger.info(
        f"✅ Auditoria local concluída: {resultado['resumo']['total_beneficiarios']} beneficiários, "
        f"{total_ativ} atividades ({total_comp} completas, {resultado['resumo']['percentual_conformidade']}%)."
    )

    return resultado


def obter_ultimo_snapshot_auditoria() -> Dict[str, Any]:
    """Retorna o último snapshot gravado em memória ou executa uma varredura se ainda vazio."""
    global _ULTIMO_SNAPSHOT_AUDITORIA
    if _ULTIMO_SNAPSHOT_AUDITORIA is None:
        return executar_auditoria_completa_pastas_locais()
    return _ULTIMO_SNAPSHOT_AUDITORIA
