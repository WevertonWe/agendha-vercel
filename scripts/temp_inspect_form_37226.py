import asyncio
import json
import sys
from collections import Counter
import httpx

sys.stdout.reconfigure(encoding='utf-8')

from app.services.coletum_service import COLETUM_TOKEN, BASE_URL_V2, buscar_respostas_formulario

async def inspect_all_answers():
    print("Buscando respostas do form 37226 (Acompanhamento Plano Produtivo - Bahia sem Fome)...")
    respostas = await buscar_respostas_formulario("37226", limit=5000)
    print(f"Total de respostas recuperadas: {len(respostas)}")
    
    # Salvar em json para análise rápida offline
    with open("temp/coletum_37226_respostas.json", "w", encoding="utf-8") as f:
        json.dump(respostas, f, ensure_ascii=False, indent=2)
    print("Salvo em temp/coletum_37226_respostas.json")

    datas = Counter()
    meses_ano = Counter()
    tecnicos = Counter()
    visita_nums = Counter()
    
    for r in respostas:
        ans = r.get("answer", {})
        # dados de execucao
        dados_exec = ans.get("dados_de_execucao861972", {})
        data_ativ = dados_exec.get("data_da_realizacao_da_atividade861976", "")
        tec = dados_exec.get("nome_doa_tecnicoa_responsavel861974", "")
        rec_ant = dados_exec.get("resultado_das_recomendacoes_tecnicas_anteriores861981", {})
        visita_n = rec_ant.get("visita_n861982")
        
        if data_ativ:
            # Ex: 2026-09-09T00:00:00-03:00 -> 2026-09-09
            dt_curta = data_ativ.split("T")[0]
            datas[dt_curta] += 1
            if len(dt_curta.split("-")) == 3:
                ano, mes, _ = dt_curta.split("-")
                meses_ano[f"{mes}/{ano}"] += 1
        else:
            datas["SEM_DATA"] += 1
            
        tecnicos[tec or "SEM_TECNICO"] += 1
        visita_nums[str(visita_n)] += 1

    print("\n--- DISTRIBUIÇÃO POR MÊS/ANO ---")
    for m, c in sorted(meses_ano.items()):
        print(f"  {m}: {c} respostas")

    print("\n--- NÚMERO DE VISITA (visita_n) ---")
    for v, c in sorted(visita_nums.items()):
        print(f"  Visita Nº {v}: {c}")

    print("\n--- TÉCNICOS RESPONSÁVEIS ---")
    for t, c in tecnicos.most_common():
        print(f"  {t}: {c}")

if __name__ == "__main__":
    asyncio.run(inspect_all_answers())
