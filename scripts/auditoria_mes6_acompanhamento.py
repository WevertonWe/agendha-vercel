import json
import re
import sys
from collections import defaultdict, Counter
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# Caminho das pastas de técnicos
BASE_TECNICOS = Path(r"C:\Users\CLIENTE\Desktop\BAHIA_SEM_FOME\weverton\técnicos")

def carregar_dados():
    with open('temp/coletum_37226_respostas.json', 'r', encoding='utf-8') as f:
        respostas = json.load(f)

    mes_6_registros = []
    for r in respostas:
        ans = r.get('answer', {})
        dados_exec = ans.get('dados_de_execucao861972', {})
        dt = dados_exec.get('data_da_realizacao_da_atividade861976', '')
        if dt and ('-06-' in dt or '/06/' in dt):
            ans_id = r.get('id')
            tec = dados_exec.get('nome_doa_tecnicoa_responsavel861974', '')
            mun = dados_exec.get('municipio861979', '')
            com = dados_exec.get('comunidade861980', '')
            
            # Identificação do beneficiário
            id_fam = ans.get('cpf_responsavel_para_identificacao_do_grupo_familiar861985', {})
            nome = id_fam.get('nome861986', '')
            cpf = id_fam.get('cpf_do_titular__do_grupo_familiar861987', '')
            
            rec_ant = dados_exec.get('resultado_das_recomendacoes_tecnicas_anteriores861981', {})
            visita_n = rec_ant.get('visita_n861982', '')

            # Converte data para DD/MM/AAAA
            dt_parts = dt.split('T')[0].split('-')
            data_formatada = f"{dt_parts[2]}/{dt_parts[1]}/{dt_parts[0]}" if len(dt_parts) == 3 else dt

            mes_6_registros.append({
                'coletum_id': ans_id,
                'tecnico': tec.strip(),
                'beneficiario': (nome or '').strip(),
                'cpf': (cpf or '').strip(),
                'municipio': mun.strip(),
                'comunidade': com.strip(),
                'data': data_formatada,
                'data_iso': dt.split('T')[0],
                'visita_n': visita_n
            })
    return mes_6_registros

def auditar():
    registros = carregar_dados()
    print("=" * 80)
    print(f"📊 CONFERÊNCIA: ACOMPANHAMENTO PLANO PRODUTIVO - BAHIA SEM FOME (MÊS 6 - JUNHO/2026)")
    print(f"Formulário Coletum ID 37226 | Total de cadastros no mês: {len(registros)}")
    print("=" * 80)

    # 1. Total por Técnico
    por_tec = defaultdict(list)
    for r in registros:
        por_tec[r['tecnico']].append(r)

    print("\n1️⃣ DISTRIBUIÇÃO POR TÉCNICO:")
    for tec, lista in sorted(por_tec.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  • {tec}: {len(lista)} registros")

    # 2. Total por Município
    por_mun = defaultdict(list)
    for r in registros:
        por_mun[r['municipio']].append(r)

    print("\n2️⃣ DISTRIBUIÇÃO POR MUNICÍPIO:")
    for mun, lista in sorted(por_mun.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  • {mun}: {len(lista)} registros")

    # 3. Análise de Duplicidades no Coletum
    por_cpf = defaultdict(list)
    sem_cpf = []
    for r in registros:
        cpf_num = re.sub(r'\D', '', r['cpf'])
        if cpf_num:
            por_cpf[cpf_num].append(r)
        else:
            sem_cpf.append(r)

    duplicados_cpf = {k: v for k, v in por_cpf.items() if len(v) > 1}
    print("\n3️⃣ ANÁLISE DE DUPLICIDADES NO COLETUM:")
    if duplicados_cpf:
        print(f"  ⚠️ Encontrados {len(duplicados_cpf)} beneficiários com mais de 1 envio em Junho/2026:")
        for cpf, lista in duplicados_cpf.items():
            print(f"    - Beneficiário: {lista[0]['beneficiario']} (CPF: {lista[0]['cpf']})")
            for item in lista:
                print(f"      ID Coletum: {item['coletum_id']} | Data: {item['data']} | Téc: {item['tecnico']} | Com: {item['comunidade']}")
    else:
        print("  ✅ Nenhuma duplicidade de CPF encontrada nos 164 registros.")

    if sem_cpf:
        print(f"  ⚠️ {len(sem_cpf)} registros sem CPF preenchido:")
        for sc in sem_cpf:
            print(f"    - ID: {sc['coletum_id']} | Beneficiário: {sc['beneficiario']} | Téc: {sc['tecnico']}")

    # 4. Cruzamento com Pastas Locais dos Técnicos
    print("\n4️⃣ CONFERÊNCIA COM PASTAS LOCAIS (TESTE DE ARQUIVOS ATESTE & COLETUM):")
    
    # Mapeamento técnico para subpasta
    tec_map = {
        'WANDISSON': 'Wandisson',
        'ESTELLA': 'estella',
        'LUIZ ANTONIEL': 'tony',
        'TONY': 'tony',
        'CAROLINE': 'caroline',
        'JOSEFA CRISTINA': 'cristina',
        'CRISTINA': 'cristina'
    }

    status_pastas = {
        'COMPLETO': [], # Tem pasta, ateste e coletum
        'FALTA_ATESTE': [],
        'FALTA_COLETUM': [],
        'PASTA_NAO_ENCONTRADA': []
    }

    def norm(txt):
        if not txt:
            return ""
        import unicodedata
        nfkd = unicodedata.normalize('NFKD', txt)
        return "".join([c for c in nfkd if not unicodedata.combining(c)]).upper().strip()

    # Indexa todas as pastas de beneficiários existentes
    pastas_beneficiarios = defaultdict(list)
    for tec_dir in BASE_TECNICOS.iterdir():
        if not tec_dir.is_dir() or tec_dir.name.upper() in {'ATESTES', 'ATIVIDADES BAIXADAS', 'TEMP', 'UPLOADS'}:
            continue
        doc_ativ = tec_dir / 'documentos-atividades'
        target = doc_ativ if doc_ativ.exists() else tec_dir
        for com_dir in target.iterdir():
            if not com_dir.is_dir() or 'ATIVIDADE COLETIVA' in com_dir.name.upper():
                continue
            for ben_dir in com_dir.iterdir():
                if ben_dir.is_dir():
                    pastas_beneficiarios[norm(ben_dir.name)].append((tec_dir.name, com_dir.name, ben_dir))

    encontrados_local = 0
    nao_encontrados_local = 0
    com_ateste = 0
    com_coletum_pdf = 0

    detalhes_cruzamento = []

    for reg in registros:
        b_norm = norm(reg['beneficiario'])
        candidatos = pastas_beneficiarios.get(b_norm, [])
        if not candidatos:
            # Tenta busca parcial
            for k, val in pastas_beneficiarios.items():
                if b_norm in k or k in b_norm:
                    candidatos = val
                    break

        if not candidatos:
            nao_encontrados_local += 1
            status_pastas['PASTA_NAO_ENCONTRADA'].append(reg)
            detalhes_cruzamento.append({**reg, 'status_local': 'SEM_PASTA', 'detalhe': 'Pasta do beneficiário não localizada'})
            continue

        encontrados_local += 1
        # Procura a pasta da atividade no mês 06/2026
        # Pode ser "30.06.2026 - VISITA", "22.06.2026 - VISITA TECNICA", "ACOMPANHAMENTO", etc.
        achou_atividade = False
        tem_at = False
        tem_col = False
        pasta_ativ_nome = ""

        _, _, ben_path = candidatos[0]
        for sub in ben_path.iterdir():
            if sub.is_dir():
                nome_sub = sub.name
                # Verifica se a data é de junho de 2026 (.06.2026 ou /06/2026 ou -06-2026)
                if '06.2026' in nome_sub or '06/2026' in nome_sub or '06-2026' in nome_sub or 'ACOMP' in nome_sub.upper():
                    achou_atividade = True
                    pasta_ativ_nome = nome_sub
                    pdfs = list(sub.glob('*.pdf'))
                    if any('ATEST' in f.name.upper() for f in pdfs):
                        tem_at = True
                    if any('COL' in f.name.upper() for f in pdfs):
                        tem_col = True
                    break

        if achou_atividade:
            if tem_at:
                com_ateste += 1
            if tem_col:
                com_coletum_pdf += 1

            if tem_at and tem_col:
                st = 'COMPLETO'
                status_pastas['COMPLETO'].append(reg)
            elif tem_col and not tem_at:
                st = 'FALTA_ATESTE'
                status_pastas['FALTA_ATESTE'].append(reg)
            elif tem_at and not tem_col:
                st = 'FALTA_COLETUM'
                status_pastas['FALTA_COLETUM'].append(reg)
            else:
                st = 'SEM_ARQUIVOS'
                status_pastas['FALTA_ATESTE'].append(reg)
            detalhes_cruzamento.append({**reg, 'status_local': st, 'pasta_ativ': pasta_ativ_nome, 'tem_ateste': tem_at, 'tem_coletum_pdf': tem_col})
        else:
            status_pastas['PASTA_NAO_ENCONTRADA'].append(reg)
            detalhes_cruzamento.append({**reg, 'status_local': 'SEM_PASTA_ATIVIDADE_MES6', 'detalhe': f'Beneficiário tem pasta, mas sem pasta de atividade em 06/2026 em {ben_path.name}'})

    print(f"  • Beneficiários com pasta no computador: {encontrados_local}/{len(registros)}")
    print(f"  • Pastas com ATESTE escaneado presente: {com_ateste}")
    print(f"  • Pastas com PDF do COLETUM presente: {com_coletum_pdf}")
    print(f"  • Documentação 100% Completa (Ateste + Coletum): {len(status_pastas['COMPLETO'])}")
    print(f"  • Falta Ateste Físico Escaneado: {len(status_pastas['FALTA_ATESTE'])}")
    print(f"  • Falta PDF do Coletum na pasta: {len(status_pastas['FALTA_COLETUM'])}")
    print(f"  • Sem pasta de atividade do mês 6 localizada: {len(status_pastas['PASTA_NAO_ENCONTRADA'])}")

    # Detalhamento por técnico da situação das pastas locais
    print("\n📊 SITUAÇÃO LOCAL POR TÉCNICO:")
    status_por_tec = defaultdict(lambda: Counter())
    for r in detalhes_cruzamento:
        status_por_tec[r['tecnico']][r.get('status_local', 'OUTRO')] += 1
    for tec, contadores in status_por_tec.items():
        print(f"  • {tec}:")
        for st, c in contadores.items():
            print(f"      {st}: {c}")

    # Salva relatório consolidado em JSON
    with open('temp/conferencia_mes6_plano_produtivo.json', 'w', encoding='utf-8') as f:
        json.dump({
            'total_coletum': len(registros),
            'resumo_tecnicos': {k: len(v) for k, v in por_tec.items()},
            'resumo_municipios': {k: len(v) for k, v in por_mun.items()},
            'duplicidades': duplicados_cpf,
            'status_pastas_resumo': {
                'completo': len(status_pastas['COMPLETO']),
                'falta_ateste': len(status_pastas['FALTA_ATESTE']),
                'falta_coletum': len(status_pastas['FALTA_COLETUM']),
                'sem_pasta': len(status_pastas['PASTA_NAO_ENCONTRADA'])
            },
            'registros': detalhes_cruzamento
        }, f, ensure_ascii=False, indent=2)
    print("\n✅ Relatório completo salvo em temp/conferencia_mes6_plano_produtivo.json")

if __name__ == '__main__':
    auditar()
