# 📊 Migration Status — Agendha Vercel

> Rastreamento da migração de SQLite → Supabase-native por módulo.

**Última atualização:** 2026-04-30  
**Progresso total estimado: ~90%**

---

## ✅ CORE — 100% [MIGRADO]

| Componente | Status | Observações |
|------------|--------|-------------|
| `app/core/auth/router.py` | ✅ [MIGRADO] | Login Supabase-native, lowercase forçado, erro genérico de segurança, auditoria VIP |
| `app/core/auth/services.py` | ✅ [MIGRADO] | `mudar_senha` via Supabase, SQLite removido |
| `app/core/auth/dependencies.py` | ✅ [MIGRADO] | Deps JWT sem SQLite |
| `app/core/database.py` | ✅ [MIGRADO] | `get_supabase()` como fonte única |
| `app/core/logging/services.py` | ✅ [MIGRADO] | `log_acao` + `audit_logs` 100% Supabase |

---

## ✅ BENEFICIÁRIOS — 100% [MIGRADO]

| Componente | Status | Observações |
|------------|--------|-------------|
| `app/routes/beneficiarios/router.py` | ✅ [MIGRADO] | CRUD Supabase |
| `app/routes/beneficiarios/services.py` | ✅ [MIGRADO] | Filtros e queries Supabase |

---

## 🔄 MÓDULOS OPERACIONAIS — ~80% [EM PROGRESSO]

| Módulo | Status | Próximo passo |
|--------|--------|---------------|
| Projetos / Água que Alimenta | 🔄 [PARCIAL] | Migrar queries de relatório |
| Financeiro | 🔄 [PARCIAL] | Migrar rotas de lançamento |
| Fornecedores | 🔄 [PARCIAL] | Migrar CRUD completo |
| Materiais | 🔄 [PARCIAL] | Migrar filtros e paginação |
| Pedreiros | 🔄 [PARCIAL] | Migrar CRUD |
| Bahia Sem Fome (BSF) | 🔄 [PARCIAL] | Migrar geração de atestes |
| OCR / IA | ✅ [MIGRADO] | Supabase Storage ativo |

---

## ⏳ PENDENTE — ~10%

| Item | Bloqueador |
|------|------------|
| Scripts `iniciar_sistema.bat` | Referência SQLite local — manter para dev local |
| `GET /api/users` (admin) | SQLite fallback removido, Supabase ativo |
| Módulo de Cronogramas | Novo — design em backlog |

---

## 🔒 Auditoria de Segurança — Resumo P3

| Verificação | Resultado |
|-------------|-----------|
| SQLite removido do Login | ✅ |
| SQLite removido de Senhas | ✅ |
| Erro genérico para falhas de auth | ✅ |
| Bypass de senha mestra removido | ✅ |
| Auditoria VIP `audit_logs` | ✅ |
| Cookie `httponly + samesite=lax` | ✅ |
| Username normalizado para lowercase | ✅ |

---

## 📈 Histórico de Progresso

| Data | Evento | % |
|------|--------|---|
| 2026-04-22 | Inventário inicial e planejamento cloud | 10% |
| 2026-04-27 | Migração auth básica + Vercel deploy | 40% |
| 2026-04-28 | Fix hashes Supabase + JWT estável | 55% |
| 2026-04-29 | Migração beneficiários + biomas | 70% |
| 2026-04-30 | Migração rotas beneficiários completa | 80% |
| 2026-04-30 | **P3: Purge SQLite Auth + Auditoria VIP** | **~90%** |
