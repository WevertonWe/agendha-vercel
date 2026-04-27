import logging
import asyncio
from typing import Dict, Any
import json
# import cv2
# import numpy as np
# import pytesseract
# from PIL import Image
from app.config import settings

# --- Configuração de Ferramentas Externas ---
# Configura o caminho do Tesseract a partir das settings
# pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

# ==============================================================================
# CONFIGURAÇÕES DE OCR (ROIs)
# ==============================================================================
LARGURA_PADRAO = 1000

RETANGULO_PRINCIPAL_PAG1_COORDS = {"x": 10, "y": 10, "w": 980, "h": 300}

# Definições de ROI para a Página 1
ROI_DEFINICOES_PAGINA1 = {
    "nome_completo_l1": {"x": 175, "y": 11, "w": 760, "h": 32, "tipo": "texto"},
    "nome_completo_l2": {"x": 6, "y": 45, "w": 502, "h": 32, "tipo": "texto"},
    "data_nascimento":  {"x": 207, "y": 75, "w": 251, "h": 30, "tipo": "texto"},
    "cpf":              {"x": 600, "y": 75, "w": 325, "h": 30, "tipo": "texto"},
    "sexo_cb_masc":     {"x": 725, "y": 53, "w": 25, "h": 25, "tipo": "checkbox", "campo_destino": "sexo", "valor_marcado": "Masculino"},
    "sexo_cb_fem":      {"x": 870, "y": 53, "w": 25, "h": 25, "tipo": "checkbox", "campo_destino": "sexo", "valor_marcado": "Feminino"},
    "escolaridade_cb_analfabeto":   {"x": 281, "y": 116, "w": 25, "h": 18, "tipo": "checkbox", "campo_destino": "escolaridade", "valor_marcado": "Analfabeto"},
    "escolaridade_cb_sabe_ler":     {"x": 402, "y": 115, "w": 30, "h": 19, "tipo": "checkbox", "campo_destino": "escolaridade", "valor_marcado": "Sabe ler e escrever"},
    "escolaridade_cb_fund_4":       {"x": 600, "y": 115, "w": 23, "h": 19, "tipo": "checkbox", "campo_destino": "escolaridade", "valor_marcado": "Ensino Fundamental - até a 4ª série"},
    "escolaridade_cb_fund_8":       {"x": 13, "y": 150, "w": 24, "h": 19, "tipo": "checkbox", "campo_destino": "escolaridade", "valor_marcado": "Ensino Fundamental - de 5ª a 8ª série"},
    "escolaridade_cb_medio_inc":    {"x": 353, "y": 150, "w": 27, "h": 17, "tipo": "checkbox", "campo_destino": "escolaridade", "valor_marcado": "Ensino Médio - Incompleto"},
    "escolaridade_cb_medio_comp":   {"x": 600, "y": 145, "w": 25, "h": 22, "tipo": "checkbox", "campo_destino": "escolaridade", "valor_marcado": "Ensino Médio - Completo"},
    "escolaridade_cb_sup_inc":      {"x": 10, "y": 185, "w": 27, "h": 15, "tipo": "checkbox", "campo_destino": "escolaridade", "valor_marcado": "Ensino Superior - Incompleto"},
    "escolaridade_cb_sup_comp":     {"x": 353, "y": 183, "w": 27, "h": 17, "tipo": "checkbox", "campo_destino": "escolaridade", "valor_marcado": "Ensino Superior - Completo"},
    "comunidade":       {"x": 157, "y": 209, "w": 764, "h": 24, "tipo": "texto"},
    "ref_localizacao":  {"x": 267, "y": 244, "w": 648, "h": 16, "tipo": "texto"},
    "municipio":        {"x": 129, "y": 273, "w": 594, "h": 27, "tipo": "texto"},
    "estado_uf":        {"x": 863, "y": 278, "w": 59,  "h": 22, "tipo": "texto"}
}

# Definições de ROI para a Página 2
ROI_DEFINICOES_PAGINA2 = {
    # Usamos as coordenadas que você encontrou!
    "nis": {"x": 300, "y": 540, "w": 173, "h": 16, "tipo": "texto"},
}

# Estrutura principal que o nosso código vai usar
TODAS_ROIS_POR_PAGINA = {
    1: {
        "retangulo_principal": RETANGULO_PRINCIPAL_PAG1_COORDS,
        "campos": ROI_DEFINICOES_PAGINA1
    },
    2: {
        # Para a página 2, não vamos recortar um retângulo principal, vamos usar a página inteira.
        "retangulo_principal": None,
        "campos": ROI_DEFINICOES_PAGINA2
    },
}


def _converter_pil_para_cv_e_redimensionar(imagem_pil: Image.Image, largura_alvo: int) -> np.ndarray:
    img_cv_rgb = np.array(imagem_pil.convert('RGB'))
    img_cv_bgr = cv2.cvtColor(img_cv_rgb, cv2.COLOR_RGB2BGR)
    altura_original, largura_original = img_cv_bgr.shape[:2]
    if largura_original == 0:
        raise ValueError("Imagem com largura original zero.")
    proporcao = largura_alvo / float(largura_original)
    altura_alvo = int(altura_original * proporcao)
    return cv2.resize(img_cv_bgr, (largura_alvo, altura_alvo), interpolation=cv2.INTER_AREA)


def _corrigir_perspectiva(imagem_cv_bgr: np.ndarray) -> np.ndarray:
    # --- Constantes para o algoritmo de deteção ---
    GAUSSIAN_BLUR_KERNEL = (5, 5)
    CANNY_THRESHOLD_1 = 75
    CANNY_THRESHOLD_2 = 200
    MAX_CONTOURS_TO_CHECK = 5
    CONTOUR_APPROX_FACTOR = 0.02
    imagem_processo = imagem_cv_bgr.copy()
    cinza = cv2.cvtColor(imagem_processo, cv2.COLOR_BGR2GRAY)
    desfoque = cv2.GaussianBlur(cinza, GAUSSIAN_BLUR_KERNEL, 0)
    bordas = cv2.Canny(desfoque, CANNY_THRESHOLD_1, CANNY_THRESHOLD_2)
    contornos, _ = cv2.findContours(
        bordas, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contornos = sorted(contornos, key=cv2.contourArea, reverse=True)[
        :MAX_CONTOURS_TO_CHECK]
    contorno_tela = None
    for c in contornos:
        perimetro = cv2.arcLength(c, True)
        aprox = cv2.approxPolyDP(c, CONTOUR_APPROX_FACTOR * perimetro, True)
        if len(aprox) == 4:
            contorno_tela = aprox
            break
    if contorno_tela is None:
        return imagem_cv_bgr
    pontos = contorno_tela.reshape(4, 2)
    pontos_ret = np.zeros((4, 2), dtype="float32")
    soma = pontos.sum(axis=1)
    pontos_ret[0] = pontos[np.argmin(soma)]
    pontos_ret[2] = pontos[np.argmax(soma)]
    diff = np.diff(pontos, axis=1)
    pontos_ret[1] = pontos[np.argmin(diff)]
    pontos_ret[3] = pontos[np.argmax(diff)]
    (sup_esq, sup_dir, inf_dir, inf_esq) = pontos_ret
    largura_a = np.sqrt(
        ((inf_dir[0] - inf_esq[0]) ** 2) + ((inf_dir[1] - inf_esq[1]) ** 2))
    largura_b = np.sqrt(
        ((sup_dir[0] - sup_esq[0]) ** 2) + ((sup_dir[1] - sup_esq[1]) ** 2))
    max_largura = max(int(largura_a), int(largura_b))
    altura_a = np.sqrt(
        ((sup_dir[0] - inf_dir[0]) ** 2) + ((sup_dir[1] - inf_dir[1]) ** 2))
    altura_b = np.sqrt(
        ((sup_esq[0] - inf_esq[0]) ** 2) + ((sup_esq[1] - inf_esq[1]) ** 2))
    max_altura = max(int(altura_a), int(altura_b))
    dst = np.array([[0, 0], [max_largura - 1, 0], [max_largura - 1,
                   max_altura - 1], [0, max_altura - 1]], dtype="float32")
    matriz_transformacao = cv2.getPerspectiveTransform(pontos_ret, dst)
    imagem_corrigida = cv2.warpPerspective(
        imagem_processo, matriz_transformacao, (max_largura, max_altura))
    return imagem_corrigida


def _preprocessar_texto_em_caixas(img_cv: np.ndarray) -> np.ndarray:
    img_cinza = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    img_invertida = cv2.bitwise_not(img_cinza)
    _, img_binarizada = cv2.threshold(
        img_invertida, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    h, w = img_binarizada.shape
    largura_kernel_h = max(1, int(w / 4))
    kernel_horizontal = cv2.getStructuringElement(
        cv2.MORPH_RECT, (largura_kernel_h, 1))
    linhas_detectadas_h = cv2.morphologyEx(
        img_binarizada, cv2.MORPH_OPEN, kernel_horizontal, iterations=2)
    img_sem_horizontais = cv2.subtract(img_binarizada, linhas_detectadas_h)
    altura_kernel_v = max(1, int(h / 4))
    kernel_vertical = cv2.getStructuringElement(
        cv2.MORPH_RECT, (1, altura_kernel_v))
    linhas_detectadas_v = cv2.morphologyEx(
        img_sem_horizontais, cv2.MORPH_OPEN, kernel_vertical, iterations=2)
    img_sem_linhas = cv2.subtract(img_sem_horizontais, linhas_detectadas_v)
    return cv2.bitwise_not(img_sem_linhas)


def _analisar_checkbox(roi_img_checkbox: np.ndarray, nome_do_campo: str) -> bool:
    LIMIAR_MARCACAO = 0.05
    if roi_img_checkbox.size == 0:
        return False
    cinza = cv2.cvtColor(roi_img_checkbox, cv2.COLOR_BGR2GRAY)
    _, binarizada = cv2.threshold(cinza, 150, 255, cv2.THRESH_BINARY_INV)
    pixels_marcados = cv2.countNonZero(binarizada)
    total_pixels = binarizada.size
    if total_pixels == 0:
        return False
    return (pixels_marcados / total_pixels) >= LIMIAR_MARCACAO


def _limpar_valor_extraido(valor: str) -> str:
    if valor:
        return ' '.join(valor.split()).strip()
    return ""


async def _preparar_pagina(imagem_pil: Image.Image, pagina_num: int, definicoes_pagina: dict) -> np.ndarray:
    """Aplica o pré-processamento (redimensionar, perspectiva, etc.) a uma única página."""
    logging.info(f"Preparando página {pagina_num}...")
    img_redim = _converter_pil_para_cv_e_redimensionar(
        imagem_pil, LARGURA_PADRAO)
    img_corrigida = _corrigir_perspectiva(img_redim)

    imagem_base_para_processar = img_corrigida
    if definicoes_pagina and definicoes_pagina.get("retangulo_principal"):
        # Lógica de recorte se necessário
        pass  # Pode adicionar a lógica de recorte aqui se precisar

    return imagem_base_para_processar


async def _extrair_dados_roi_atualizado(imagem_processada: np.ndarray, definicoes_rois: Dict[str, Any]) -> Dict[str, str]:
    """Versão atualizada da sua função _extrair_dados_roi."""
    dados_extraidos = {}
    configs_tesseract = {
        "texto_livre": r'--oem 3 --psm 7',
        "texto_caixas": r'--oem 3 --psm 6',
        "texto_curto": r'--oem 3 --psm 8',
        "numeros": r'--oem 3 --psm 7 -c tessedit_char_whitelist="0123456789"'
    }
    mapa_configs = {
        "nome_completo_l1": "texto_livre", "comunidade": "texto_livre", "municipio": "texto_livre",
        "ref_localizacao": "texto_livre", "data_nascimento": "numeros", "cpf": "numeros",
        "estado_uf": "texto_curto", "nis": "numeros"
    }
    campos_com_caixas = ["data_nascimento", "cpf", "comunidade",
                         "municipio", "ref_localizacao", "estado_uf", "nis"]

    for nome_campo, roi_info in definicoes_rois.items():
        if roi_info.get("tipo") == "texto":
            x, y, w, h = (roi_info["x"], roi_info["y"],
                          roi_info["w"], roi_info["h"])
            roi_img = imagem_processada[y:y+h, x:x+w]
            if roi_img.size == 0:
                continue

            img_para_ocr = _preprocessar_texto_em_caixas(
                roi_img) if nome_campo in campos_com_caixas else cv2.cvtColor(roi_img, cv2.COLOR_BGR2GRAY)

            config_key = mapa_configs.get(nome_campo, "texto_caixas")
            config_ocr = configs_tesseract[config_key]
            texto = await asyncio.to_thread(pytesseract.image_to_string, img_para_ocr, lang='por', config=config_ocr)
            dados_extraidos[nome_campo] = _limpar_valor_extraido(texto)

    # Processamento de checkboxes
    for nome_campo, roi_info in definicoes_rois.items():
        if roi_info.get("tipo") == "checkbox":
            campo_destino = roi_info["campo_destino"]
            x, y, w, h = (roi_info["x"], roi_info["y"],
                          roi_info["w"], roi_info["h"])
            roi_cb_img = imagem_processada[y:y+h, x:x+w]
            if _analisar_checkbox(roi_cb_img, nome_campo):
                dados_extraidos[campo_destino] = roi_info["valor_marcado"]
                break

    return dados_extraidos


from app.services import ai_vision  # noqa: E402

async def processar_ocr_completo(file_path: str) -> Dict[str, Any]:
    """
    Função principal: orquestra o processo de OCR usando Google Gemini Flash.
    Suporta PDF e Imagens nativamente via API do Gemini.
    """
    try:
        # Passa o caminho do arquivo diretamente para o serviço de visão
        # O serviço agora lida com o upload para o Gemini (que aceita PDF e imagens)
        result = await ai_vision.processar_imagem_gemini(file_path)
        
        full_text = ""
        structured_data = {}
        
        # Try to parse JSON if Gemini returns a JSON block as requested
        # Gemini might return ```json ... ```
        clean_result = result.strip()
        if clean_result.startswith("```json"):
            clean_result = clean_result.replace("```json", "").replace("```", "").strip()
        
        try:
            page_data = json.loads(clean_result)
            if isinstance(page_data, dict):
                structured_data.update(page_data)
        except json.JSONDecodeError:
            full_text = result

        # If we got structured data, return it
        if structured_data:
            return structured_data
            
        # Fallback: Return text in a dict
        return {"texto_bruto": full_text}

    except Exception as e:
        logging.error(f"Erro no OCR Gemini: {e}")
        raise e
