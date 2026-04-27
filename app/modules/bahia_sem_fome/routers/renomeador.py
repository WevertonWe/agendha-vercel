import re
import io
import json
import logging
import zipfile
import asyncio
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
import fitz # PyMuPDF
import pdfplumber
import os

router = APIRouter(prefix="/api/bahia-sem-fome", tags=["BSF API"])
logger = logging.getLogger(__name__)

class RenameInfo(BaseModel):
    nome: str = Field(description="Nome do beneficiário")
    tipo: str = Field(description="Tipo de documento: ATESTE ou COLLETUM")

MODELOS_PERMITIDOS = ["gemini-3.1-flash-lite", "gemini-2.5-flash-lite", "gemini-3-flash", "gemini-2.5-flash", "gemini-2.0-flash"]

def get_gemini_client():
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        return genai.Client(api_key=api_key)
    return None

def extrair_local_regex(texto: str):
    nome, tipo = None, None
    texto_flat = re.sub(r'\s+', ' ', texto.upper())
    letras_br = r"[A-ZÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛÃÕÇ\s\'\-]"
    
    # A Tesoura: Corta o texto assim que bater em um número ou rótulo do PDF
    paradas = r'(\d|CPF|DAP|CAF|RG|DATA|MUNIC|ENDERE|P[AÁ]GINA)'

    # PADRÃO 1: Ateste de Atividade
    if "ATESTE" in texto_flat:
        tipo = "ATESTE"
        # Pega um bloco sujo de até 150 caracteres após a âncora
        match = re.search(r'BENEFICI[AÁ]RI[OA]?\s*\(?A?\)?\s*[:\-]?\s*(.{5,150})', texto_flat)
        if match:
            bloco = match.group(1)
            fatia = re.split(paradas, bloco)[0] # Corta na primeira parada
            nome_limpo = re.sub(r'[^A-ZÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛÃÕÇ\s\'\-]', '', fatia).strip()
            nome = re.sub(r'\s+', ' ', nome_limpo)

    # PADRÃO 2: Formulário de Atividade (Colletum)
    elif "FORMUL" in texto_flat or "COLLETUM" in texto_flat:
        tipo = "COLLETUM"
        # Tenta pegar direto entre CPFs primeiro
        match = re.search(r'\d{3}\.?\d{3}\.?\d{3}-?\d{2}\s*(' + letras_br + r'{5,120})\s*(?:CPF|DATA|\d{3})', texto_flat)
        if match:
            nome = match.group(1).strip()
        # Fallback Colletum 
        if not nome:
            match = re.search(r'NOME DO BENEFICI[AÁ]RI[OA]?\s*\(?A?\)?\s*[:\-]?\s*(.{5,150})', texto_flat)
            if match:
                bloco = match.group(1)
                fatia = re.split(paradas, bloco)[0]
                nome_limpo = re.sub(r'[^A-ZÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛÃÕÇ\s\'\-]', '', fatia).strip()
                nome = re.sub(r'\s+', ' ', nome_limpo)

    # PADRÃO 3: Acompanhamento Plano Produtivo
    elif "ACOMPANHAMENTO PLANO PRODUTIVO" in texto_flat:
        tipo = "ACOMPANHAMENTO"
        match = re.search(r'TITULAR 1 DO GRUPO FAMILIAR\s*[:\-]?\s*(.{5,150})', texto_flat)
        if match:
            bloco = match.group(1)
            fatia = re.split(paradas, bloco)[0]
            nome_limpo = re.sub(r'[^A-ZÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛÃÕÇ\s\'\-]', '', fatia).strip()
            nome = re.sub(r'\s+', ' ', nome_limpo)

        if not nome or len(nome) < 5:
            match = re.search(r'NOME\s*:\s*(?:P[AÁ]GINA\s+\d+\s+DE\s+\d+\s*)?(' + letras_br + r'{5,120})\s*CPF DO TITULAR', texto_flat)
            if match:
                nome = match.group(1).strip()

    if nome and len(nome) < 5:
        nome = None

    return nome, tipo

async def extrair_e_analisar(file_content: bytes, filename: str):
    """Extrai texto do PDF em cascata (Waterfall) e identifica nome e tipo."""
    try:
        nome_local, tipo_local = None, None

        # 1. TENTATIVA: PyMuPDF (Extremamente rápido)
        try:
            with fitz.open(stream=file_content, filetype="pdf") as pdf:
                text_fitz = ""
                for i in range(min(3, len(pdf))):
                    text_fitz += pdf[i].get_text() + "\n"
                
                if text_fitz.strip():
                    nome_local, tipo_local = extrair_local_regex(text_fitz)
        except Exception as e:
            logger.warning(f"Erro PyMuPDF em {filename}: {e}")

        # 2. TENTATIVA: pdfplumber (Mais preciso com layouts - se a 1 falhar)
        if not nome_local or not tipo_local:
            try:
                with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                    text_plumber = ""
                    for i in range(min(3, len(pdf.pages))):
                        text_plumber += pdf.pages[i].extract_text() + "\n"
                    
                    if text_plumber.strip():
                        nome_local, tipo_local = extrair_local_regex(text_plumber)
            except Exception as e:
                logger.warning(f"Erro pdfplumber em {filename}: {e}")

        # SUCESSO LOCAL (Pula a IA)
        if nome_local and tipo_local:
            # Saneamento básico do nome
            nome_saneado = "".join(c for c in nome_local if c.isalnum() or c in (" ", "-", "_")).strip()
            new_name = f"{nome_saneado} - {tipo_local}.pdf"
            logger.info(f"⚡ Sucesso Local (Waterfall Regex) para {filename}: {new_name}")
            return new_name

        # 3. TENTATIVA: IA Gemini (Fallback se as locais falharem)
        client = get_gemini_client()
        if not client:
             logger.warning("API do Gemini não configurada. IA indisponível.")
             return filename

        text_for_ai = ""
        try:
            with fitz.open(stream=file_content, filetype="pdf") as pdf:
                for i in range(min(3, len(pdf))):
                    text_for_ai += pdf[i].get_text() + "\n"
        except Exception:
            pass

        if not text_for_ai.strip():
            logger.warning(f"Texto não extraído de {filename}. IA não terá contexto.")
            return filename

        prompt = (
            "Analise o texto abaixo extraído de um documento do projeto Bahia Sem Fome. "
            "Extraia o nome do beneficiário (geralmente após 'NOME DO BENEFICIÁRIO') "
            "e o tipo do documento: 'ATESTE' se for um ateste de atividade, ou 'COLLETUM' "
            "se for um Formulário de Atividade Individual Bahia Sem Fome (também chamado de Colletum). "
            "Retorne APENAS um JSON estrito no formato: {\"nome\": \"NOME\", \"tipo\": \"TIPO\"}. "
            f"\n\nTexto:\n{text_for_ai[:4000]}" 
        )

        for nome_modelo in MODELOS_PERMITIDOS:
            try:
                logger.info(f"Tentando renomear '{filename}' com o modelo: {nome_modelo}")
                
                response = await asyncio.to_thread(
                    client.models.generate_content,
                    model=nome_modelo,
                    contents=[prompt],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=RenameInfo
                    )
                )
                
                # Parse do JSON
                data = json.loads(response.text)
                nome = data.get("nome", "DESCONHECIDO").strip().upper()
                tipo = data.get("tipo", "DOCUMENTO").strip().upper()
                
                # Saneamento básico do nome
                nome = "".join(c for c in nome if c.isalnum() or c in (" ", "-", "_")).strip()
                
                new_name = f"{nome} - {tipo}.pdf"
                logger.info(f"✅ Sucesso com {nome_modelo}: {new_name}")
                return new_name

            except Exception as e:
                logger.warning(f"⚠️ Falha no modelo {nome_modelo} para o arquivo {filename}: {e}")
                continue 

        logger.error(f"❌ Todos os modelos falharam para o arquivo {filename}. Mantendo original.")
        return filename

    except Exception as e:
        logger.error(f"Erro fatal ao processar {filename}: {e}")
        return filename

@router.post("/renomeador-lote")
async def renomear_lote(files: List[UploadFile] = File(...)):
    """Recebe múltiplos PDFs, renomeia-os via IA e retorna um ZIP."""
    if not files:
        raise HTTPException(status_code=400, detail="Nenhum arquivo enviado.")

    zip_buffer = io.BytesIO()
    
    try:
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            for file in files:
                content = await file.read()
                
                # Processamento assíncrono para cada arquivo
                new_filename = await extrair_e_analisar(content, file.filename)
                
                # Se o nome falhar ou for vazio, usa o original
                if not new_filename or new_filename.strip() == "":
                    new_filename = file.filename
                
                # Adiciona ao ZIP
                zip_file.writestr(new_filename, content)

        zip_buffer.seek(0)
        
        return StreamingResponse(
            iter([zip_buffer.getvalue()]),
            media_type="application/x-zip-compressed",
            headers={
                "Content-Disposition": f"attachment; filename=BSF_Renomeados_{len(files)}_arquivos.zip"
            }
        )

    except Exception as e:
        logger.error(f"Erro na geração do ZIP: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar pacote ZIP: {str(e)}")
