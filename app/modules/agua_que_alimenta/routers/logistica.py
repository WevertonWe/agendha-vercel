from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from app.modules.agua_que_alimenta.services.logistica_service import calculate_logistics_preview
from app.modules.agua_que_alimenta.services.pdf_service_abare import gerar_pdf_cotacao_logistica

router = APIRouter(prefix="/api/logistica", tags=["Logística"])

@router.get("/abare/preview", response_class=JSONResponse)
def get_abare_preview(request: Request):
    token = request.cookies.get("access_token") or request.headers.get("Authorization")
    if not token:
        pass
    
    try:
        resultado = calculate_logistics_preview()
        return resultado
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao gerar prévia logística: {str(e)}")

@router.get("/abare/pdf", response_class=StreamingResponse)
def get_abare_pdf(request: Request):
    token = request.cookies.get("access_token")
    if not token and not request.headers.get("Authorization"):
         pass

    try:
        dados = calculate_logistics_preview()
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

