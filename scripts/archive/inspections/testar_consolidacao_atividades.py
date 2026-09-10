import sys
import shutil
from pathlib import Path
from collections import defaultdict
from app.modules.bahia_sem_fome.services.auditoria_service import extrair_categoria_atividade

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

base = Path(r"C:\Users\CLIENTE\Desktop\BAHIA_SEM_FOME\weverton\técnicos")

def consolidar_atividades_divididas(base_dir: Path, executar: bool = False):
    total_beneficiarios = 0
    total_mesclados = 0
    pastas_removidas = 0
    arquivos_movidos = 0

    for tec in base_dir.iterdir():
        if not tec.is_dir() or tec.name.startswith("_") or tec.name in {"atestes", "caracterização", "planos produtivos"}:
            continue
        doc_ativ = tec / "documentos-atividades"
        alvo = doc_ativ if doc_ativ.exists() else tec
        
        for com in alvo.iterdir():
            if not com.is_dir() or com.name.upper() == "ATIVIDADE COLETIVA":
                continue
            for benef in com.iterdir():
                if not benef.is_dir():
                    continue
                total_beneficiarios += 1
                
                # Agrupa subpastas por categoria de atividade
                por_categoria = defaultdict(list)
                for sub in benef.iterdir():
                    if sub.is_dir():
                        cat = extrair_categoria_atividade(sub.name)
                        pdfs = list(sub.glob("*.pdf"))
                        tem_ateste = any("ATEST" in f.name.upper() for f in pdfs)
                        tem_coletum = any("COL" in f.name.upper() for f in pdfs)
                        por_categoria[cat].append({
                            "pasta": sub,
                            "nome": sub.name,
                            "pdfs": pdfs,
                            "tem_ateste": tem_ateste,
                            "tem_coletum": tem_coletum
                        })
                
                for cat, lista in por_categoria.items():
                    if len(lista) > 1 and cat != "OUTROS":
                        # 1. Se tem pasta vazia (0 PDFs), remove
                        for p in lista:
                            if len(p["pdfs"]) == 0:
                                if executar:
                                    shutil.rmtree(str(p["pasta"]), ignore_errors=True)
                                    pastas_removidas += 1

                        pastas_com_arquivos = [p for p in lista if len(p["pdfs"]) > 0]
                        if len(pastas_com_arquivos) > 1:
                            # Se uma tem ateste e outra tem coletum
                            tem_at = any(p["tem_ateste"] for p in pastas_com_arquivos)
                            tem_col = any(p["tem_coletum"] for p in pastas_com_arquivos)

                            if tem_at and tem_col:
                                # Escolhe a melhor pasta de destino:
                                # Prioriza a pasta que tem o Coletum (geralmente tem a data original do formulário)
                                pasta_destino_info = next((p for p in pastas_com_arquivos if p["tem_coletum"]), pastas_com_arquivos[0])
                                pasta_origem_info = next((p for p in pastas_com_arquivos if p != pasta_destino_info), None)

                                if pasta_origem_info:
                                    total_mesclados += 1
                                    dest_dir = pasta_destino_info["pasta"]
                                    orig_dir = pasta_origem_info["pasta"]

                                    if executar:
                                        for f in orig_dir.glob("*.pdf"):
                                            f_dest = dest_dir / f.name
                                            if not f_dest.exists():
                                                shutil.move(str(f), str(f_dest))
                                                arquivos_movidos += 1
                                            else:
                                                # Se já existe com mesmo nome mas tamanhos diferentes
                                                if f.stat().st_size != f_dest.stat().st_size:
                                                    f_dest_alt = dest_dir / f"ATEST_{f.name}"
                                                    shutil.move(str(f), str(f_dest_alt))
                                                    arquivos_movidos += 1
                                                else:
                                                    f.unlink(missing_ok=True)
                                        
                                        # Remove pasta de origem agora vazia
                                        shutil.rmtree(str(orig_dir), ignore_errors=True)
                                        pastas_removidas += 1

    print(f"📊 Simulação/Execução: {total_mesclados} atividades mescladas, {arquivos_movidos} arquivos movidos, {pastas_removidas} pastas duplicadas removidas.")
    return total_mesclados

# Executa simulação
print("--- TESTE DE CONSOLIDAÇÃO ---")
consolidar_atividades_divididas(base, executar=False)
