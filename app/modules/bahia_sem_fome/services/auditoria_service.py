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
            "percentual_conformidade": 0.0
        },
        "duplicidades_detectadas": [],
        "tecnicos": {},
        "detalhes_beneficiarios": []
    }

    if not caminho_base.exists():
        logger.warning(f"Caminho base de armazenamento não encontrado: {caminho_base}")
        _ULTIMO_SNAPSHOT_AUDITORIA = resultado
        return resultado

    ignorar_pastas = {"ATESTES", "DOCUMENTOS", "UPLOADS", "TEMP", "__PYCACHE__", ".GIT"}

    # 1. Varre Técnicos
    pastas_tecnicos = [
        p for p in caminho_base.iterdir()
        if p.is_dir() and p.name.upper() not in ignorar_pastas
    ]
    resultado["resumo"]["total_tecnicos"] = len(pastas_tecnicos)

    for pasta_tec in pastas_tecnicos:
        nome_tec = pasta_tec.name
        doc_ativ = pasta_tec / "documentos-atividades"
        if not doc_ativ.exists():
            # Se não tem a subpasta documentos-atividades, considera a própria pasta do técnico
            doc_ativ = pasta_tec

        # Checagem de pastas duplicadas de comunidades
        dups_comunidades = identificar_pastas_duplicadas_por_acentos(doc_ativ)
        if dups_comunidades:
            resultado["duplicidades_detectadas"].extend(dups_comunidades)
            if auto_consolidar_acentos:
                consolidar_pastas_duplicadas_segura(doc_ativ)

        comunidades_pastas = [c for c in doc_ativ.iterdir() if c.is_dir()]
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

            benef_pastas = [b for b in pasta_com.iterdir() if b.is_dir()]
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

                    if status == "COMPLETO":
                        resumo_tec["atividades_completas"] += 1
                        resultado["resumo"]["atividades_completas"] += 1
                    elif status == "PENDENTE_ATESTE":
                        resumo_tec["pendentes_ateste"] += 1
                        resultado["resumo"]["pendentes_ateste"] += 1
                    elif status == "PENDENTE_COLETUM":
                        resumo_tec["pendentes_coletum"] += 1
                        resultado["resumo"]["pendentes_coletum"] += 1
                    else:
                        resumo_tec["vazias"] += 1
                        resultado["resumo"]["vazias_ou_erro"] += 1

                    nome_exibicao_ativ = pasta_ativ.name if pasta_ativ != pasta_benef else "DOCUMENTOS_GERAIS"
                    atividades_info.append({
                        "pasta_atividade": nome_exibicao_ativ,
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
