import re
import unicodedata
from typing import Any

def limpar_cpf(cpf_bruto: Any) -> str | None:
    """
    Limpa e normaliza um número de CPF, removendo caracteres não numéricos
    e garantindo que tenha 11 dígitos (com zeros à esquerda).

    Esta é a versão robusta que trata:
    - Valores None
    - Espaços em branco (strip)
    - Caracteres não numéricos (re.sub)
    - CPFs curtos (zfill)
    """
    if cpf_bruto is None:
        return None

    # 1. Converte para string e remove espaços em branco no início/fim
    cpf_str = str(cpf_bruto).strip()

    # 2. Remove tudo exceto dígitos
    cpf_limpo = re.sub(r'[^0-9]', '', cpf_str)

    # 3. Se estiver vazio após a limpeza (ex: "NaN" ou ""), retorna None
    if not cpf_limpo:
        return None

    # 4. Garante 11 dígitos, preenchendo com zeros à esquerda
    #    (Ex: "3608925589" -> "03608925589")
    cpf_normalizado = cpf_limpo.zfill(11)

    return cpf_normalizado


def remover_acentos(texto: Any) -> str | None:
    """
    Remove acentos de uma string, converte para maiúsculas e remove espaços.
    Útil para comparações de nomes.
    """
    if texto is None:
        return None

    texto_str = str(texto)

    # Normaliza para 'NFD' (Canonical Decomposition) e filtra caracteres não-ASCII
    nfkd_form = unicodedata.normalize('NFD', texto_str)
    texto_sem_acentos = "".join(
        [c for c in nfkd_form if not unicodedata.combining(c)])

    # Converte para maiúsculas e remove espaços extra
    return texto_sem_acentos.upper().strip()
