import os
import asyncio
import tempfile
import logging
from pathlib import Path
from typing import List
from pydantic import BaseModel
from fastapi import APIRouter, Form, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from app.services.scanner_service import (
    get_base_storage_path,
    salvar_documento_escaneado,
    acionar_scanner_wia_windows,
    localizar_ou_criar_pasta_beneficiario,
    normalizar_texto,
    normalizar_data
)
from app.modules.bahia_sem_fome.routers.renomeador import extrair_e_analisar

router = APIRouter(prefix="/api/bahia-sem-fome/scanner", tags=["BSF Scanner API"])
logger = logging.getLogger(__name__)

@router.get("/status-fila")
async def status_fila():
    from app.services.queue_service import queue_manager
    return JSONResponse(content=queue_manager.get_status())

async def _processar_folha_ia(image_bytes: bytes, filename: str, mode_str: str, tipo_documento: str):
    from app.modules.bahia_sem_fome.routers.renomeador import extrair_e_analisar
    from app.services.scanner_service import salvar_documento_escaneado
    try:
        nome_sugerido, meta_ia = await extrair_e_analisar(image_bytes, filename, mode=mode_str)
        if meta_ia and meta_ia.get("nome"):
            beneficiario = meta_ia.get("nome")
            tipo_doc = meta_ia.get("tipo") if tipo_documento == "AUTO" else tipo_documento
            if not tipo_doc or tipo_doc == "AUTO":
                tipo_doc = "COLLETUM" if "colletum" in filename.lower() or "colletum" in mode_str else "ATESTE"
                
            data_atividade = meta_ia.get("data") or ""
            tecnico = meta_ia.get("tecnico") or "caroline"
            comunidade = meta_ia.get("comunidade") or "GERAL"
            atividade_extraida = meta_ia.get("atividade") or ""
            
            res = await salvar_documento_escaneado(
                file_bytes=image_bytes,
                beneficiario=beneficiario,
                tipo_documento=tipo_doc,
                data_atividade=data_atividade,
                tecnico=tecnico,
                comunidade=comunidade,
                extensao=".pdf",
                atividade_extraida=atividade_extraida
            )
            
            pasta_destino = res.get("pasta_data", "Desconhecida")
            arquivo_final = res.get("nome_arquivo", "Desconhecido")
            
            if res.get("status") == "ignorado":
                msg = f"⏭️ Ignorado: '{arquivo_final}' já existe na pasta '{pasta_destino}'."
                logger.info(msg)
                return msg
            else:
                msg = f"✅ Sucesso: '{filename}' salvo como PDF ('{arquivo_final}') na pasta '{pasta_destino}'."
                logger.info(msg)
                return msg
        else:
            msg = f"⚠️ IA falhou ou cota excedida para '{filename}'. Arquivo pulado/não renomeado."
            logger.warning(msg)
            return msg
    except Exception as e:
        msg = f"❌ Erro ao processar '{filename}': {str(e)}"
        logger.error(msg, exc_info=True)
        return msg

@router.get("/status")
async def scanner_status():
    """Retorna o status do armazenamento local/rede e suporte ao scanner WIA."""
    base_path = get_base_storage_path()
    return {
        "status": "online",
        "storage_path": str(base_path),
        "storage_exists": base_path.exists(),
        "platform": os.name
    }

@router.post("/escanear-auto-ia")
async def escanear_auto_ia():
    """
    Aciona o alimentador do scanner USB físico (ADF), captura TODAS as folhas presentes,
    extrai AUTOMATICAMENTE os metadados via IA Gemini Multimodal e salva cada folha
    na pasta do beneficiário correspondente por data.
    """
    from app.services.scanner_service import acionar_scanner_adf_batch_wia, normalizar_bytes_imagem_para_jpeg
    
    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path_dir = Path(tmp_dir)
            
            # 1. Tenta capturar todas as páginas do alimentador ADF
            scanned_files = acionar_scanner_adf_batch_wia(tmp_path_dir)
            
            # 2. Fallback para escaneamento de folha única se o lote ADF não retornar arquivos
            if not scanned_files:
                single_bmp = tmp_path_dir / "single_scan.bmp"
                sucesso = acionar_scanner_wia_windows(single_bmp)
                if sucesso and single_bmp.exists():
                    scanned_files = [single_bmp]
                    
            if not scanned_files:
                raise HTTPException(
                    status_code=400,
                    detail="Nenhum papel detectado no alimentador ou falha na digitalização. Verifique se as folhas estão posicionadas (com o texto virado para baixo no alimentador) e tente novamente."
                )

            from app.services.queue_service import queue_manager
            
            jobs_enqueued = 0
            
            # --- Modo Um por Um (Síncrono para 1 folha) ---
            if len(scanned_files) == 1:
                img_path = scanned_files[0]
                with open(img_path, "rb") as f:
                    raw_bytes = f.read()
                image_bytes = normalizar_bytes_imagem_para_jpeg(raw_bytes, rotacionar_180=False, auto_crop=True)
                
                # Aguarda o processamento agora mesmo
                msg = await _processar_folha_ia(
                    image_bytes,
                    "folha_1.jpg",
                    "ateste",
                    "ATESTE"
                )
                
                return JSONResponse(content={
                    "status": "sucesso_sincrono",
                    "mensagem": msg,
                    "total_folhas": 1
                })
            
            # --- Modo Lote (Assíncrono na fila para 2+ folhas) ---
            for idx, img_path in enumerate(scanned_files):
                with open(img_path, "rb") as f:
                    raw_bytes = f.read()

                # Normaliza imagem para JPEG limpo com rotação e crop automático (pois vem do alimentador)
                image_bytes = normalizar_bytes_imagem_para_jpeg(raw_bytes, rotacionar_180=False, auto_crop=True)

                await queue_manager.add_job(
                    _processar_folha_ia,
                    image_bytes,
                    f"folha_{idx+1}.jpg",
                    "ateste",
                    "ATESTE"
                )
                jobs_enqueued += 1

            return JSONResponse(content={
                "status": "sucesso",
                "mensagem": f"{jobs_enqueued} folhas digitalizadas e enviadas para processamento em background (IA).",
                "total_folhas": jobs_enqueued
            })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no escaneamento automático ADF IA: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/organizar-lote-upload")
async def organizar_lote_upload(
    files: List[UploadFile] = File(...),
    tipo_documento: str = Form("AUTO")
):
    """
    Recebe um lote de arquivos baixados (PDFs ou Imagens de Colletum/Ateste),
    extrai automaticamente os metadados via IA Gemini Multimodal, encontra a pasta
    existente do beneficiário (onde já está seu ateste) e junta o Colletum/Ateste na pasta correta!
    """
    from app.services.scanner_service import normalizar_bytes_imagem_para_jpeg
    from app.services.queue_service import queue_manager
    jobs_enqueued = 0

    for idx, file in enumerate(files):
        content = await file.read()
        if not content.startswith(b'%PDF'):
            image_bytes = normalizar_bytes_imagem_para_jpeg(content)
        else:
            image_bytes = content

        mode_str = "colletum" if tipo_documento == "COLETUM" else "auto"
        await queue_manager.add_job(
            _processar_folha_ia,
            image_bytes,
            file.filename,
            mode_str,
            tipo_documento
        )
        jobs_enqueued += 1

    return JSONResponse(content={
        "status": "sucesso",
        "mensagem": f"{jobs_enqueued} arquivos baixados enviados para processamento em background (IA).",
        "total_folhas": jobs_enqueued
    })

class MoverPastaLocalRequest(BaseModel):
    caminho_pasta: str
    remover_origem: bool = True
    tipo_documento: str = "AUTO"

@router.post("/organizar-pasta-local")
async def organizar_pasta_local(req: MoverPastaLocalRequest):
    """
    Varre a pasta local indicada no computador do usuário (ex: Downloads ou pasta selecionada),
    analisa cada PDF/Imagem via IA Gemini, salva na pasta oficial do beneficiário (junto com o Ateste)
    e RETIRA/REMOVE o arquivo da pasta de origem (move o arquivo em vez de copiar).
    """
    caminho_limpo = req.caminho_pasta.strip().strip('"').strip("'")
    pasta_path = Path(caminho_limpo)
    
    if not pasta_path.exists() or not pasta_path.is_dir():
        raise HTTPException(status_code=400, detail=f"A pasta local '{caminho_limpo}' não existe ou é inválida.")

    arquivos = [f for f in pasta_path.iterdir() if f.is_file() and f.suffix.lower() in ('.pdf', '.png', '.jpg', '.jpeg', '.bmp', '.tiff')]
    if not arquivos:
        return JSONResponse(content={
            "status": "ia_inconclusiva",
            "mensagem": f"Nenhum arquivo PDF ou Imagem encontrado na pasta '{pasta_path.name}'."
        })

    resultados = []

    for idx, file_path in enumerate(arquivos):
        if idx > 0:
            await asyncio.sleep(1.2)

        try:
            with open(file_path, "rb") as f:
                content = f.read()

            if not content.startswith(b'%PDF'):
                image_bytes = normalizar_bytes_imagem_para_jpeg(content, rotacionar_180=False)
            else:
                image_bytes = content

            mode_str = "colletum" if req.tipo_documento == "COLETUM" else "auto"
            nome_sugerido, meta_ia = await extrair_e_analisar(image_bytes, file_path.name, mode=mode_str)

            if meta_ia and meta_ia.get("nome"):
                beneficiario = meta_ia.get("nome")
                tipo_doc = meta_ia.get("tipo") if req.tipo_documento == "AUTO" else req.tipo_documento
                if not tipo_doc or tipo_doc == "AUTO":
                    tipo_doc = "COLLETUM" if "colletum" in file_path.name.lower() or "colletum" in mode_str else "ATESTE"

                data_atividade = meta_ia.get("data") or ""
                tecnico = meta_ia.get("tecnico") or "caroline"
                comunidade = meta_ia.get("comunidade") or "GERAL"
                atividade_extraida = meta_ia.get("atividade") or ""

                res = await salvar_documento_escaneado(
                    file_bytes=content,
                    beneficiario=beneficiario,
                    tipo_documento=tipo_doc,
                    data_atividade=data_atividade,
                    tecnico=tecnico,
                    comunidade=comunidade,
                    extensao=file_path.suffix,
                    atividade_extraida=atividade_extraida
                )

                # Se remover_origem for True e o arquivo foi processado (não ignorado), retira da pasta local
                if req.remover_origem and res.get("status") != "ignorado":
                    try:
                        os.remove(file_path)
                        logger.info(f"🗑️ Arquivo original movido e removido da pasta de origem: {file_path}")
                    except Exception as e_del:
                        logger.warning(f"Não foi possível remover arquivo de origem {file_path}: {e_del}")

                resultados.append({
                    "folha": idx + 1,
                    "filename": file_path.name,
                    "status": "sucesso",
                    "dados_extraidos": meta_ia,
                    "dados_salvamento": res
                })
            else:
                resultados.append({
                    "folha": idx + 1,
                    "filename": file_path.name,
                    "status": "ia_inconclusiva",
                    "mensagem": f"A IA não conseguiu identificar o beneficiário no arquivo '{file_path.name}'."
                })
        except Exception as e:
            logger.error(f"Erro ao organizar arquivo local {file_path.name}: {e}")
            resultados.append({
                "folha": idx + 1,
                "filename": file_path.name,
                "status": "erro",
                "mensagem": f"Erro em {file_path.name}: {str(e)}"
            })

    sucessos = [r for r in resultados if r["status"] == "sucesso"]
    primeiro = sucessos[0] if sucessos else resultados[0]

    return JSONResponse(content={
        "status": primeiro["status"],
        "mensagem": f"Processados e movidos {len(sucessos)} de {len(arquivos)} arquivos da pasta local!",
        "total_folhas": len(arquivos),
        "lote_completo": resultados
    })

@router.post("/escanear-direto")
async def escanear_direto(
    beneficiario: str = Form(...),
    tipo_documento: str = Form("ATESTE"),
    data_atividade: str = Form(...),
    tecnico: str = Form("caroline"),
    comunidade: str = Form("GERAL")
):
    """
    Aciona o scanner USB físico conectado ao computador Windows com formulário manual.
    """
    try:
        with tempfile.NamedTemporaryFile(suffix=".bmp", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        sucesso_scan = acionar_scanner_wia_windows(tmp_path)
        if not sucesso_scan or not tmp_path.exists():
            if tmp_path.exists():
                os.remove(tmp_path)
            raise HTTPException(
                status_code=400,
                detail="Nenhum scanner USB detectado ou falha na digitalização. Verifique se o scanner está ligado e conectado via USB."
            )

        with open(tmp_path, "rb") as f:
            file_bytes = f.read()

        os.remove(tmp_path)

        # Normaliza a imagem (rotação 180 graus e crop para remover margens brancas do scanner físico)
        from app.services.scanner_service import normalizar_bytes_imagem_para_jpeg
        image_bytes = normalizar_bytes_imagem_para_jpeg(file_bytes, rotacionar_180=True, auto_crop=True)

        res = await salvar_documento_escaneado(
            file_bytes=image_bytes,
            beneficiario=beneficiario,
            tipo_documento=tipo_documento,
            data_atividade=data_atividade,
            tecnico=tecnico,
            comunidade=comunidade,
            extensao=".pdf"
        )

        return JSONResponse(content={
            "status": "sucesso",
            "mensagem": f"Documento digitalizado e salvo em {res['caminho_completo']}",
            "dados": res
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao processar escaneamento direto: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/organizar-upload")
async def organizar_upload(
    file: UploadFile = File(...),
    beneficiario: str = Form(...),
    tipo_documento: str = Form("ATESTE"),
    data_atividade: str = Form(...),
    tecnico: str = Form("caroline"),
    comunidade: str = Form("GERAL")
):
    """
    Recebe um PDF/Imagem já digitalizado, renomeia para '[BENEFICIARIO] - [TIPO_DOC]'
    e organiza na pasta exata do beneficiário por data.
    """
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Arquivo vazio.")

        ext = Path(file.filename).suffix or ".pdf"

        res = await salvar_documento_escaneado(
            file_bytes=content,
            beneficiario=beneficiario,
            tipo_documento=tipo_documento,
            data_atividade=data_atividade,
            tecnico=tecnico,
            comunidade=comunidade,
            extensao=ext
        )

        return JSONResponse(content={
            "status": "sucesso",
            "mensagem": f"Arquivo salvo com sucesso na pasta do beneficiário!",
            "dados": res
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao organizar upload: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
