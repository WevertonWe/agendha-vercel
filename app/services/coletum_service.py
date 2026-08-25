import httpx
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

COLETUM_TOKEN = "517vrjljdboc8g0wwsw48k8co40cos8"
BASE_URL = "https://coletum.com/api/answers"

async def buscar_respostas_coletum(form_id: str) -> List[Dict]:
    headers = {"token": COLETUM_TOKEN}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}?formId={form_id}", headers=headers)
            response.raise_for_status()
            data = response.json()
            # Coletum API usually returns data inside a key like 'data' or similar
            return data if isinstance(data, list) else data.get('data', [])
        except Exception as e:
            logger.error(f"Erro ao buscar respostas do Coletum: {e}")
            return []

async def filtrar_respostas(respostas: List[Dict], cpf_ou_nome: str) -> List[Dict]:
    termo = cpf_ou_nome.lower()
    filtradas = []
    for resp in respostas:
        resp_str = str(resp).lower()
        if termo in resp_str:
            filtradas.append(resp)
    return filtradas

async def baixar_anexo_pdf(url_anexo: str) -> Optional[bytes]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url_anexo)
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.error(f"Erro ao baixar PDF {url_anexo}: {e}")
            return None
