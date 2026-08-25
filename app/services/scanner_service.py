import os
import re
import sys
import glob
import logging
import subprocess
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from app.config import settings

logger = logging.getLogger(__name__)

# Configuração da Pasta Raiz dos Técnicos (Padrão ou via Variável de Ambiente)
DEFAULT_STORAGE_PATH = r"C:\Users\CLIENTE\Desktop\BAHIA_SEM_FOME\weverton\técnicos"

def get_base_storage_path() -> Path:
    """Retorna o caminho base das pastas dos técnicos no servidor local/rede."""
    custom_path = os.getenv("LOCAL_STORAGE_BASE_PATH")
    if custom_path and os.path.exists(custom_path):
        return Path(custom_path)
    if os.path.exists(DEFAULT_STORAGE_PATH):
        return Path(DEFAULT_STORAGE_PATH)
    # Fallback para pasta UPLOAD_FOLDER da aplicação
    fallback = settings.UPLOAD_FOLDER / "tecnicos"
    os.makedirs(fallback, exist_ok=True)
    return fallback

def normalizar_texto(texto: str) -> str:
    """Remove acentos, espaços extras e converte para maiúsculas para comparação segura."""
    if not texto:
        return ""
    nfkd_form = unicodedata.normalize('NFKD', texto)
    texto_sem_acento = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    limpo = re.sub(r'[^a-zA-Z0-9\s\-]', '', texto_sem_acento)
    return re.sub(r'\s+', ' ', limpo).strip().upper()

def normalizar_data(data_str: str) -> str:
    """
    Normaliza a data no formato DD.MM.AAAA para criação da subpasta.
    Exemplo: '28/04/2026', '28-04-2026', '2026-04-28' -> '28.04.2026'
    """
    if not data_str:
        return datetime.now().strftime("%d.%m.%Y")
    
    data_clean = data_str.strip().replace('/', '-').replace('.', '-')
    parts = data_clean.split('-')
    
    try:
        if len(parts) == 3:
            # Formato AAAA-MM-DD
            if len(parts[0]) == 4:
                ano, mes, dia = parts[0], parts[1], parts[2]
                return f"{int(dia):02d}.{int(mes):02d}.{ano}"
            # Formato DD-MM-AAAA
            elif len(parts[2]) == 4:
                dia, mes, ano = parts[0], parts[1], parts[2]
                return f"{int(dia):02d}.{int(mes):02d}.{ano}"
    except Exception:
        pass
    
    return datetime.now().strftime("%d.%m.%Y")

def obter_pastas_tecnicos_validas() -> List[Path]:
    """Retorna apenas as pastas de técnicos legítimas/existentes na raiz do diretório."""
    base_dir = get_base_storage_path()
    if not base_dir.exists():
        return []
    
    ignorar = {"ATESTES", "DOCUMENTOS", "UPLOADS", "TEMP"}
    pastas = []
    for item in base_dir.iterdir():
        if item.is_dir() and normalizar_texto(item.name) not in ignorar:
            pastas.append(item)
    return pastas

def encontrar_pasta_tecnico_existente(tecnico_sugerido: str, comunidade_sugerida: str = "") -> Path:
    """
    Localiza a pasta de um técnico existente na raiz. NUNCA cria pastas novas de técnico.
    1. Tenta casar o primeiro nome do técnico (ex: MIGSON BRAYNE -> migson).
    2. Tenta encontrar a comunidade dentro da pasta de algum técnico existente.
    3. Se não encontrar nada, utiliza o primeiro técnico existente da lista (ex: caroline).
    """
    pastas_tecnicos = obter_pastas_tecnicos_validas()
    if not pastas_tecnicos:
        base_dir = get_base_storage_path()
        return base_dir / "caroline"

    norm_tec = normalizar_texto(tecnico_sugerido)
    primeiro_nome_tec = norm_tec.split()[0] if norm_tec else ""

    # 1. Tenta casar pelo primeiro nome do técnico (ex: 'MIGSON' -> 'migson', 'WANDISSON' -> 'Wandisson')
    if primeiro_nome_tec:
        for pasta in pastas_tecnicos:
            norm_pasta = normalizar_texto(pasta.name)
            if primeiro_nome_tec in norm_pasta or norm_pasta in primeiro_nome_tec:
                logger.info(f"🎯 Técnico '{tecnico_sugerido}' casou com a pasta existente: '{pasta.name}'")
                return pasta

    # 2. Se não casou pelo nome do técnico, tenta procurar em qual técnico a comunidade já existe
    norm_com = normalizar_texto(comunidade_sugerida)
    if norm_com:
        for pasta in pastas_tecnicos:
            for sub in pasta.glob("**/*"):
                if sub.is_dir() and normalizar_texto(sub.name) == norm_com:
                    logger.info(f"🎯 Comunidade '{comunidade_sugerida}' localizada dentro da pasta do técnico '{pasta.name}'")
                    return pasta

    # 3. Fallback: Retorna a primeira pasta de técnico existente (ex: caroline)
    logger.info(f"⚠️ Técnico '{tecnico_sugerido}' não casou com pastas existentes. Reusando pasta '{pastas_tecnicos[0].name}'")
    return pastas_tecnicos[0]

def encontrar_ou_criar_pasta_comunidade(pasta_tecnico: Path, comunidade_sugerida: str) -> Path:
    """
    Localiza uma pasta de comunidade existente dentro do técnico ou cria apenas se não existir.
    """
    doc_atividades = pasta_tecnico / "documentos-atividades"
    doc_atividades.mkdir(parents=True, exist_ok=True)

    norm_com = normalizar_texto(comunidade_sugerida)
    if norm_com:
        for sub in doc_atividades.glob("**/*"):
            if sub.is_dir() and normalizar_texto(sub.name) == norm_com:
                logger.info(f"✅ Comunidade existente encontrada: '{sub}'")
                return sub

    # Se não existir comunidade com esse nome, cria a subpasta da comunidade dentro de documentos-atividades
    nome_comunidade_final = normalizar_texto(comunidade_sugerida) or "GERAL"
    pasta_comunidade = doc_atividades / nome_comunidade_final
    pasta_comunidade.mkdir(parents=True, exist_ok=True)
    return pasta_comunidade

def localizar_ou_criar_pasta_beneficiario(
    tecnico: str,
    comunidade: str,
    beneficiario: str
) -> Path:
    """
    Procura a pasta de um beneficiário em toda a árvore de técnicos/comunidades.
    Se não encontrar, vincula a um técnico e comunidade EXISTENTES sem criar novos técnicos.
    """
    base_dir = get_base_storage_path()
    norm_benef = normalizar_texto(beneficiario)
    
    logger.info(f"Buscando pasta para beneficiário: '{beneficiario}' (Norm: '{norm_benef}') em '{base_dir}'")
    
    # 1. Busca recursiva por pasta com o nome do beneficiário em QUALQUER pasta de técnico
    if base_dir.exists():
        for item in base_dir.glob("**/*"):
            if item.is_dir() and normalizar_texto(item.name) == norm_benef:
                logger.info(f"✅ Pasta de beneficiário existente encontrada: {item}")
                return item

    # 2. Se a pasta do beneficiário não existir, localiza a pasta de técnico e comunidade EXISTENTES
    pasta_tecnico = encontrar_pasta_tecnico_existente(tecnico, comunidade)
    pasta_comunidade = encontrar_ou_criar_pasta_comunidade(pasta_tecnico, comunidade)
    
    beneficiario_folder = normalizar_texto(beneficiario) or "BENEFICIARIO_DESCONHECIDO"
    pasta_beneficiario = pasta_comunidade / beneficiario_folder
    pasta_beneficiario.mkdir(parents=True, exist_ok=True)
    logger.info(f"📁 Pasta de beneficiário criada na estrutura existente: {pasta_beneficiario}")
    return pasta_beneficiario

def acionar_scanner_wia_windows(save_image_path: Path) -> bool:
    """
    Aciona o scanner USB conectado via Windows WIA usando PowerShell.
    Captura a folha do scanner e salva em save_image_path.
    """
    if sys.platform != "win32":
        logger.warning("Acionamento de WIA disponível apenas em ambiente Windows.")
        return False

    ps_script = f"""
    $ErrorActionPreference = 'Stop'
    try {{
        $deviceManager = New-Object -ComObject WIA.DeviceManager
        $device = $null
        
        # 1. Procura especificamente por scanner Canon ou primeiro scanner USB WIA
        # Primeiro passamos procurando CANON
        $canonFound = $false
        foreach ($info in $deviceManager.DeviceInfos) {{
            if ($info.Properties.Item("Name").Value -like "*CANON*") {{
                $canonFound = $true
                try {{
                    $device = $info.Connect()
                    break
                }} catch {{
                    Write-Output "CANON_BUSY"
                    exit 1
                }}
            }}
        }}
        
        # Se não achou CANON, tenta qualquer scanner (Type 1)
        if ($null -eq $device -and -not $canonFound) {{
            foreach ($info in $deviceManager.DeviceInfos) {{
                if ($info.Type -eq 1) {{
                    try {{
                        $device = $info.Connect()
                        break
                    }} catch {{ }}
                }}
            }}
        }}
        
        if ($null -eq $device) {{
            Write-Error "Nenhum scanner disponível ou acessível."
            exit 1
        }}
        
        $item = $device.Items.Item(1)
        # GUID do formato JPEG no WIA: {{B96B3CAE-0728-11D3-9D7B-0000F81EF32E}}
        $imageFormatId = "{{B96B3CAE-0728-11D3-9D7B-0000F81EF32E}}"
        $image = $item.Transfer($imageFormatId)
        
        $outputPath = "{str(save_image_path).replace('\\', '\\\\')}"
        if (Test-Path $outputPath) {{ Remove-Item $outputPath -Force }}
        $image.SaveFile($outputPath)
        Write-Output "SUCCESS"
    }} catch {{
        Write-Error $_.Exception.Message
        exit 1
    }}
    """
    
    # Tentativa de digitalização com até 3 re-tentativas (para dar tempo de reset do driver Canon)
    import time
    for tentativa in range(1, 4):
        try:
            cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if "CANON_BUSY" in result.stdout:
                logger.error("Scanner CANON detectado mas ocupado/bloqueado.")
                return False
            if result.returncode == 0 and "SUCCESS" in result.stdout:
                logger.info(f"✅ Digitalização WIA concluída com sucesso (tentativa {tentativa}): {save_image_path}")
                return True
            else:
                logger.warning(f"⚠️ Tentativa {tentativa}/3 falhou no scanner WIA: {result.stderr or result.stdout}")
                time.sleep(1.5)
        except Exception as e:
            logger.error(f"Erro na tentativa {tentativa} do script WIA: {e}")
            time.sleep(1.5)
            
    return False

def acionar_scanner_adf_batch_wia(temp_dir_path: Path) -> List[Path]:
    """
    Aciona o alimentador automático (ADF) do scanner USB (como Canon DR-C240)
    e captura TODAS as páginas presentes no alimentador para o diretório temp_dir_path.
    Retorna a lista de caminhos dos arquivos de imagem capturados.
    """
    if sys.platform != "win32":
        logger.warning("Acionamento WIA disponível apenas no Windows.")
        return []

    temp_dir_path.mkdir(parents=True, exist_ok=True)
    import time
    
    ps_script = f"""
    $ErrorActionPreference = 'Stop'
    $imageFormatId = "{{B96B3CAE-0728-11D3-9D7B-0000F81EF32E}}"
    $outputDir = "{str(temp_dir_path).replace('\\', '\\\\')}"
    
    $pageCount = 0
    try {{
        $deviceManager = New-Object -ComObject WIA.DeviceManager
        $device = $null
        
        # Prioriza CANON
        $canonFound = $false
        foreach ($info in $deviceManager.DeviceInfos) {{
            if ($info.Properties.Item("Name").Value -like "*CANON*") {{
                $canonFound = $true
                try {{
                    $device = $info.Connect()
                    break
                }} catch {{ 
                    Write-Output "CANON_BUSY"
                    exit 1
                }}
            }}
        }}
        
        # Fallback para qualquer scanner se não houver CANON conectado
        if ($null -eq $device -and -not $canonFound) {{
            foreach ($info in $deviceManager.DeviceInfos) {{
                if ($info.Type -eq 1) {{
                    try {{
                        $device = $info.Connect()
                        break
                    }} catch {{ }}
                }}
            }}
        }}
        
        if ($null -eq $device) {{ 
            Write-Error "Nenhum scanner ADF disponível."
            exit 1 
        }}

        # Configura alimentador ADF (1 = Feeder)
        try {{ $device.Properties.Item("3088").Value = 1 }} catch {{ }}
        
        # WIA_DPS_PAGES (3096) = 1 (Lê 1 página por vez no Transfer, ideal para JPEG)
        try {{ $device.Properties.Item("3096").Value = 1 }} catch {{ }}

        for ($i = 1; $i -le 100; $i++) {{
            try {{
                # Alguns drivers exigem re-acessar o Item(1) a cada iteração
                $item = $device.Items.Item(1)
                $image = $item.Transfer($imageFormatId)
                $pageCount++
                $filePath = Join-Path $outputDir "sheet_$pageCount.jpg"
                if (Test-Path $filePath) {{ Remove-Item $filePath -Force }}
                $image.SaveFile($filePath)
                Write-Output "PAGE_SAVED:$filePath"
            }} catch {{
                # Fim do lote (alimentador sem mais papéis)
                break
            }}
        }}
    }} catch {{
        Write-Error $_.Exception.Message
    }}
    Write-Output "TOTAL_PAGES:$pageCount"
    """

    for tentativa in range(1, 4):
        try:
            cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
            
            if "CANON_BUSY" in result.stdout:
                logger.error("Scanner CANON detectado, mas está em uso ou com erro WIA.")
                raise Exception("O Scanner CANON foi detectado mas está ocupado/offline. Desligue e ligue o equipamento ou feche outro programa que o esteja usando (ex: CaptureOnTouch).")
                
            pages_found = []
            
            # Mesmo que o script tenha dado erro (returncode != 0),
            # ele pode ter conseguido salvar algumas páginas (PAGE_SAVED)
            # antes do erro de COM ocorrer (ex: fim do papel).
            for line in result.stdout.splitlines():
                if line.startswith("PAGE_SAVED:"):
                    p = Path(line.replace("PAGE_SAVED:", "").strip())
                    if p.exists():
                        pages_found.append(p)
                        
            if pages_found:
                logger.info(f"✅ Capturadas {len(pages_found)} páginas do alimentador ADF (tentativa {tentativa}).")
                # Se deu erro no final, apenas avisamos, mas não perdemos as folhas lidas
                if result.returncode != 0:
                    logger.warning(f"⚠️ Scanner reportou erro, mas resgatamos {len(pages_found)} páginas: {result.stderr}")
                return pages_found
            else:
                logger.warning(f"⚠️ Tentativa ADF {tentativa}/3 sem folhas ou ocupado: {result.stderr or result.stdout}")
                time.sleep(1.5)
        except Exception as e:
            logger.error(f"Erro na tentativa {tentativa} do ADF: {e}")
            time.sleep(1.5)

    return []

def normalizar_bytes_imagem_para_jpeg(image_bytes: bytes, rotacionar_180: bool = False, auto_crop: bool = False) -> bytes:
    """
    Garante que qualquer imagem (BMP, PNG, TIFF, JPEG) seja convertida para JPEG limpo.
    Por padrão, não altera a rotação a menos que rotacionar_180 seja ativado explicitamente (scanner USB ADF).
    Com auto_crop=True, remove espaços em branco (margens) desnecessários.
    """
    from PIL import Image, ImageChops
    import io
    
    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
                
            if rotacionar_180:
                img = img.rotate(180, expand=True)
                
            if auto_crop:
                # Remove bordas brancas (Crop)
                bg = Image.new(img.mode, img.size, (255, 255, 255))
                diff = ImageChops.difference(img, bg)
                diff = ImageChops.add(diff, diff, 2.0, -100)
                bbox = diff.getbbox()
                if bbox:
                    # Adiciona uma margem de segurança de 20px
                    left = max(0, bbox[0] - 20)
                    top = max(0, bbox[1] - 20)
                    right = min(img.size[0], bbox[2] + 20)
                    bottom = min(img.size[1], bbox[3] + 20)
                    img = img.crop((left, top, right, bottom))
                
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=95)
            return output.getvalue()
    except Exception as e:
        logger.warning(f"Falha ao normalizar imagem via PIL: {e}")
        return image_bytes

async def salvar_documento_escaneado(
    file_bytes: bytes,
    beneficiario: str,
    tipo_documento: str, # 'ATESTE' ou 'COLETUM'
    data_atividade: str,
    tecnico: str = "caroline",
    comunidade: str = "GERAL",
    extensao: str = ".pdf",
    atividade_extraida: str = ""
) -> Dict[str, Any]:
    """
    Salva um documento (PDF/Imagem) na estrutura correta do beneficiário:
    .../BENEFICIARIO/DD.MM.AAAA - ATIVIDADE/[BENEFICIARIO] - [TIPO_DOC].pdf
    Verifica se já existe para evitar reprocessamento indevido.
    """
    pasta_beneficiario = localizar_ou_criar_pasta_beneficiario(tecnico, comunidade, beneficiario)
    data_formatada = normalizar_data(data_atividade)
    
    atividade = atividade_extraida
    if not atividade:
        from app.services.ai_vision import identificar_tipo_atividade_gemini
        nome_arquivo_temp = "documento" + extensao
        atividade = await identificar_tipo_atividade_gemini(file_bytes, nome_arquivo_temp)
    
    if atividade and atividade != "DOCUMENTO" and atividade != "DOCUMENTO_SEM_IA":
        pasta_data = pasta_beneficiario / f"{data_formatada} - {atividade}"
    else:
        pasta_data = pasta_beneficiario / data_formatada

    pasta_data.mkdir(parents=True, exist_ok=True)
    
    nome_benef_norm = normalizar_texto(beneficiario)
    tipo_doc_norm = normalizar_texto(tipo_documento) or "DOCUMENTO"
    
    ext = extensao if extensao.startswith(".") else f".{extensao}"
    nome_arquivo = f"{nome_benef_norm} - {tipo_doc_norm}{ext}"
    
    caminho_final = pasta_data / nome_arquivo
    
    # === VERIFICAÇÃO DE DUPLICIDADE (Ignora se já existir) ===
    if caminho_final.exists():
        logger.info(f"⏭️ Arquivo já existe, ignorando processamento duplicado: {caminho_final}")
        return {
            "status": "ignorado",
            "caminho_completo": str(caminho_final),
            "nome_arquivo": nome_arquivo,
            "pasta_data": pasta_data.name,
            "beneficiario": nome_benef_norm,
            "tipo_documento": tipo_doc_norm,
            "mensagem": "Já existe um arquivo salvo para esta pessoa e data/atividade."
        }

    # Se a extensão for PDF e os bytes NÃO forem um PDF válido (%PDF), converte a imagem para PDF limpo
    if extensao.lower() == ".pdf" and not file_bytes.startswith(b'%PDF'):
        try:
            from PIL import Image
            import io
            with Image.open(io.BytesIO(file_bytes)) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                pdf_io = io.BytesIO()
                img.save(pdf_io, format='PDF', quality=100)
                file_bytes = pdf_io.getvalue()
                logger.info("📄 Imagem convertida com sucesso para PDF limpo via Pillow.")
        except Exception as e_pdf:
            logger.error(f"Erro ao converter imagem para PDF via Pillow: {e_pdf}")

    with open(caminho_final, "wb") as f:
        f.write(file_bytes)
        
    logger.info(f"✅ Documento salvo em: {caminho_final}")
    
    return {
        "status": "sucesso",
        "caminho_completo": str(caminho_final),
        "nome_arquivo": nome_arquivo,
        "pasta_data": pasta_data.name,
        "beneficiario": nome_benef_norm,
        "tipo_documento": tipo_doc_norm
    }
