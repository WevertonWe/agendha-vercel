from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
import sqlite3
from app.dependencies import get_db_connection
from app.modules.agua_que_alimenta.services.logistica_service import calculate_logistics_preview
from app.modules.agua_que_alimenta.services.pdf_service_abare import gerar_pdf_cotacao_logistica

router = APIRouter(prefix="/api/logistica", tags=["Logística"])

@router.get("/abare/preview", response_class=JSONResponse)
def get_abare_preview(
    request: Request,
    db: sqlite3.Connection = Depends(get_db_connection),
    # current_user = Depends(get_current_user) # Disabled for flexible session support
):
    """
    Retorna uma prévia JSON dos dados logísticos para Abaré.
    
    Verifica se o usuário tem token/cookie (simulação de auth).
    Chama 'calculate_logistics_preview' para processar candidatos e custos.
    """
    # Manual Auth Check (Cookie or Header)
    token = request.cookies.get("access_token") or request.headers.get("Authorization")
    if not token:
        # For dev/test comfort as requested:
        # raise HTTPException(status_code=401, detail="Não autenticado")
        pass # Allow for now as requested for "teste rápido"
    
    try:
        resultado = calculate_logistics_preview(db)
        return resultado
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao gerar prévia logística: {str(e)}")

@router.get("/abare/pdf", response_class=StreamingResponse)
def get_abare_pdf(
    request: Request,
    db: sqlite3.Connection = Depends(get_db_connection),
    # current_user = Depends(get_current_user) # Disabled for flexible session support
):
    """
    Gera e retorna o PDF da Cotação Logística de Abaré.
    
    1. Calcula a prévia logística (dados).
    2. Gera o PDF em memória (BytesIO) usando 'gerar_pdf_cotacao_logistica'.
    3. Retorna como StreamingResponse (download).
    """
    # Manual Auth Check
    token = request.cookies.get("access_token")
    if not token and not request.headers.get("Authorization"):
         pass # Allow for now

    try:
        dados = calculate_logistics_preview(db)
        pdf_buffer = gerar_pdf_cotacao_logistica(dados)
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=Cotacao_Logistica_Abare.pdf"}
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao gerar PDF: {str(e)}")
