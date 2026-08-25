import os
from pathlib import Path
from fastapi import APIRouter, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from pydantic import BaseModel

from app.main import templates

router = APIRouter(tags=["Classificador Manual"])

# Caminho base das pastas dos técnicos
BASE_DIR = Path(r"C:\Users\CLIENTE\Desktop\BAHIA_SEM_FOME\weverton\técnicos")

class RenomearRequest(BaseModel):
    caminho_pasta: str
    atividade: str

@router.get("/bahia-sem-fome/classificador", response_class=HTMLResponse)
async def classificador_page(request: Request):
    """Renderiza a página principal do classificador manual."""
    return templates.TemplateResponse(
        request=request,
        name="bahia-sem-fome/classificador.html",
        context={"current_page": "bsf_classificador", "page_title": "Classificador Rápido de Documentos"}
    )

@router.get("/api/classificador/proxima")
async def buscar_proxima_pasta():
    """Busca a próxima pasta que ainda não possui atividade (nome com exatos 10 caracteres)."""
    if not BASE_DIR.exists():
        return JSONResponse({"status": "erro", "mensagem": "Diretório base não encontrado."})

    for item in BASE_DIR.rglob("*"):
        if item.is_dir() and len(item.name) == 10:
            partes = item.name.split('.')
            if len(partes) == 3 and partes[0].isdigit() and partes[1].isdigit() and partes[2].isdigit():
                # Encontrou uma pasta válida. Vamos procurar um PDF ou imagem dentro dela.
                arquivos = [f for f in item.iterdir() if f.is_file() and f.suffix.lower() in ('.pdf', '.jpg', '.jpeg', '.png')]
                if arquivos:
                    arquivo = arquivos[0]
                    return {
                        "status": "sucesso",
                        "pasta_nome": item.name,
                        "caminho_pasta": str(item),
                        "caminho_arquivo": str(arquivo),
                        "nome_arquivo": arquivo.name
                    }
    
    return {"status": "concluido", "mensagem": "Nenhuma pasta pendente encontrada!"}

@router.get("/api/classificador/arquivo")
async def servir_arquivo(caminho: str):
    """Serve o arquivo (PDF/Imagem) para ser exibido no Iframe da tela."""
    path = Path(caminho)
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.")
        
    # Proteção de segurança básica: garantir que o arquivo esteja dentro do BASE_DIR
    try:
        path.resolve().relative_to(BASE_DIR.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Acesso negado.")
        
    return FileResponse(path)

@router.post("/api/classificador/renomear")
async def renomear_pasta(payload: RenomearRequest):
    """Renomeia a pasta concatenando a atividade escolhida pelo usuário."""
    pasta_atual = Path(payload.caminho_pasta)
    atividade = payload.atividade.strip()
    
    if not pasta_atual.exists() or not pasta_atual.is_dir():
        raise HTTPException(status_code=404, detail="Pasta original não encontrada.")
        
    if not atividade:
        raise HTTPException(status_code=400, detail="Atividade inválida.")
        
    novo_nome = f"{pasta_atual.name} - {atividade}"
    nova_pasta_path = pasta_atual.parent / novo_nome
    
    # Se a pasta já existir, adiciona um sufixo (1), (2) para não dar erro
    contador = 1
    while nova_pasta_path.exists():
        novo_nome = f"{pasta_atual.name} - {atividade} ({contador})"
        nova_pasta_path = pasta_atual.parent / novo_nome
        contador += 1
    
    try:
        pasta_atual.rename(nova_pasta_path)
        return {"status": "sucesso", "mensagem": f"Pasta renomeada para {novo_nome}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao renomear pasta: {str(e)}")
