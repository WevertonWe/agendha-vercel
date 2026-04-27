"""
Migração: Unificação de Atividades BSF
- Unifica 'Cadastro Familiar' → 'Cadastro do Grupo Familiar'
- Unifica 'Reunião de Articulação' → 'Reunião de Articulação com os Parceiros'
- Remove: 'Implantação de Fomento', 'Monitoramento', 'Oficina de Capacitação'
"""
import sqlite3
import os
import shutil
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "agendha.db")

UNIFY_MAP = {
    "Cadastro Familiar": "Cadastro do Grupo Familiar",
    "Reunião de Articulação": "Reunião de Articulação com os Parceiros",
}

REMOVE_LIST = [
    "Implantação de Fomento",
    "Monitoramento",
    "Oficina de Capacitação",
]


def get_activity_id(cursor, nome):
    cursor.execute("SELECT id FROM bsf_atividades WHERE nome = ?", (nome,))
    row = cursor.fetchone()
    return row[0] if row else None


def migrate():
    print(f"📂 Banco: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("❌ Banco não encontrado!")
        return

    # Backup
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = DB_PATH.replace(".db", f"_backup_{ts}.db")
    shutil.copy2(DB_PATH, backup)
    print(f"💾 Backup: {backup}")

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = OFF")
    cursor = conn.cursor()

    # Snapshot antes
    cursor.execute("SELECT id, nome FROM bsf_atividades ORDER BY id")
    print("\n📋 Atividades ANTES:")
    for row in cursor.fetchall():
        print(f"   [{row[0]}] {row[1]}")

    # --- FASE 1: Unificar nomes ---
    print("\n🔄 FASE 1: Unificação de nomes...")
    total_migrated = 0

    for old_name, new_name in UNIFY_MAP.items():
        old_id = get_activity_id(cursor, old_name)
        new_id = get_activity_id(cursor, new_name)

        if not old_id:
            print(f"   ⏭ '{old_name}' não existe no banco — pulando")
            continue
        if not new_id:
            print(f"   ⚠ '{new_name}' não existe! Renomeando ID {old_id}...")
            cursor.execute("UPDATE bsf_atividades SET nome = ? WHERE id = ?", (new_name, old_id))
            print(f"   ✅ Renomeado ID {old_id}: '{old_name}' → '{new_name}'")
            continue

        # Ambos existem: migrar visitas do antigo para o novo
        cursor.execute(
            "UPDATE bsf_visitas SET atividade_id = ? WHERE atividade_id = ?",
            (new_id, old_id),
        )
        count_visitas = cursor.rowcount
        total_migrated += count_visitas
        print(f"   ✅ '{old_name}' (ID {old_id}) → '{new_name}' (ID {new_id}): {count_visitas} visitas migradas")

        # Migrar metas_composicao
        cursor.execute(
            "UPDATE bsf_metas_composicao SET atividade_id = ? WHERE atividade_id = ?",
            (new_id, old_id),
        )

        # Migrar metas_tecnicos
        cursor.execute(
            "UPDATE bsf_metas_tecnicos SET atividade_id = ? WHERE atividade_id = ?",
            (new_id, old_id),
        )

        # Remover metas_contrato duplicadas do ID antigo
        cursor.execute("DELETE FROM bsf_metas_contrato WHERE atividade_id = ?", (old_id,))

        # Remover atividade legado
        cursor.execute("DELETE FROM bsf_atividades WHERE id = ?", (old_id,))
        print(f"   🗑 Atividade legado ID {old_id} removida")

    # --- FASE 2: Remover atividades sem meta ---
    print(f"\n🗑 FASE 2: Removendo atividades sem meta...")  # noqa: F541
    total_removed = 0

    for nome in REMOVE_LIST:
        act_id = get_activity_id(cursor, nome)
        if not act_id:
            print(f"   ⏭ '{nome}' não existe — pulando")
            continue

        # Verificar visitas órfãs
        cursor.execute("SELECT COUNT(*) FROM bsf_visitas WHERE atividade_id = ?", (act_id,))
        orphan_count = cursor.fetchone()[0]
        if orphan_count > 0:
            print(f"   ⚠ '{nome}' tem {orphan_count} visitas — setando atividade_id para NULL")
            cursor.execute("UPDATE bsf_visitas SET atividade_id = NULL WHERE atividade_id = ?", (act_id,))

        # Limpar referências
        cursor.execute("DELETE FROM bsf_metas_contrato WHERE atividade_id = ?", (act_id,))
        cursor.execute("DELETE FROM bsf_metas_composicao WHERE atividade_id = ?", (act_id,))
        cursor.execute("DELETE FROM bsf_metas_tecnicos WHERE atividade_id = ?", (act_id,))

        # Remover atividade
        cursor.execute("DELETE FROM bsf_atividades WHERE id = ?", (act_id,))
        total_removed += 1
        print(f"   ✅ '{nome}' (ID {act_id}) removida")

    conn.commit()

    # Snapshot depois
    cursor.execute("SELECT id, nome FROM bsf_atividades ORDER BY id")
    remaining = cursor.fetchall()
    print(f"\n📋 Atividades DEPOIS ({len(remaining)} restantes):")
    for row in remaining:
        print(f"   [{row[0]}] {row[1]}")

    # Contagem de validação
    cursor.execute(
        "SELECT a.nome, COUNT(v.id) FROM bsf_atividades a "
        "LEFT JOIN bsf_visitas v ON v.atividade_id = a.id "
        "GROUP BY a.id ORDER BY COUNT(v.id) DESC"
    )
    print("\n📊 Contagem de visitas por atividade:")
    for nome, count in cursor.fetchall():
        print(f"   {nome}: {count}")

    conn.close()
    print(f"\n✅ Migração concluída! {total_migrated} visitas migradas, {total_removed} atividades removidas.")


if __name__ == "__main__":
    migrate()
