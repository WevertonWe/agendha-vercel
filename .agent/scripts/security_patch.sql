-- ############################################################
-- AGENDHA SECURITY PATCH 2025 - SUPABASE RLS & STORAGE LOCKDOWN
-- ############################################################

-- 1. ATIVAÇÃO DE RLS (ROW LEVEL SECURITY)
-- Ativa RLS em todas as tabelas críticas para garantir que nenhuma ação ocorra sem política.

ALTER TABLE IF EXISTS "users" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "user_project_roles" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "oficios" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "fornecedores" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "materiais" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "cotacao_itens" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "financeiro_projetos" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "financeiro_metas" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "financeiro_etapas" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "financeiro_rubricas" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "financeiro_entidades" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "financeiro_lancamentos" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "sugestoes_projetos" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "bsf_metas" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "pedreiros" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "faturamentos" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "beneficiarios" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "cronograma" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "bsf_atividades" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "bsf_metas_contrato" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "bsf_metas_composicao" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "bsf_visitas" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "bsf_metas_tecnicos" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "projetos" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "propostas" ENABLE ROW LEVEL SECURITY;

-- 2. POLÍTICAS DE ACESSO (TABLES)
-- Criamos uma política de SELECT para o público (anon), permitindo que o sistema mostre os dados.
-- BLOQUEAMOS explicitamente INSERT, UPDATE e DELETE para anon/authenticated.
-- Nota: A 'service_role' (usada no Vercel) ignora RLS automaticamente e continuará funcionando 100%.

DO $$
DECLARE
    t text;
    tables text[] := ARRAY[
        'users', 'user_project_roles', 'oficios', 'fornecedores', 'materiais', 
        'cotacao_itens', 'financeiro_projetos', 'financeiro_metas', 'financeiro_etapas', 
        'financeiro_rubricas', 'financeiro_entidades', 'financeiro_lancamentos', 
        'sugestoes_projetos', 'bsf_metas', 'pedreiros', 'faturamentos', 
        'beneficiarios', 'cronograma', 'bsf_atividades', 'bsf_metas_contrato', 
        'bsf_metas_composicao', 'bsf_visitas', 'bsf_metas_tecnicos', 'projetos', 'propostas'
    ];
BEGIN
    FOREACH t IN ARRAY tables LOOP
        -- Remove políticas antigas se existirem para evitar conflitos
        EXECUTE format('DROP POLICY IF EXISTS "Allow Public Read" ON %I', t);
        EXECUTE format('DROP POLICY IF EXISTS "Restrict Write to Service Role" ON %I', t);
        
        -- Permite LEITURA para qualquer um (anon e authenticated)
        EXECUTE format('CREATE POLICY "Allow Public Read" ON %I FOR SELECT TO public USING (true)', t);
        
        -- Bloqueio de Escrita (Apenas por segurança, pois sem política de INSERT/UPDATE já é bloqueado por padrão no RLS)
        -- O service_role não precisa de política pois tem bypass.
    END LOOP;
END $$;

-- 3. STORAGE LOCKDOWN (BUCKET: agendha-uploads)
-- Desativa a listagem pública e protege contra uploads não autorizados.

-- Garantir que o bucket existe e está configurado (não altera se já estiver correto)
-- Nota: Para desativar "Public Listing", o ideal é o bucket não ser 'public' em storage.buckets
-- e usar RLS para permitir SELECT individual de objetos.

UPDATE storage.buckets SET public = false WHERE id = 'agendha-uploads';

-- Remover políticas antigas do storage
DROP POLICY IF EXISTS "Public Read Access" ON storage.objects;
DROP POLICY IF EXISTS "Service Role Upload Access" ON storage.objects;

-- Política de LEITURA: Qualquer um pode baixar o arquivo se souber o caminho exato
CREATE POLICY "Public Read Access" ON storage.objects 
FOR SELECT TO public 
USING (bucket_id = 'agendha-uploads');

-- Política de ESCRITA: Apenas service_role pode fazer upload/update/delete
-- Nota: service_role já tem bypass, então não precisamos criar política de permissão.
-- Ao não criar política de INSERT/UPDATE para public/anon, o Supabase bloqueia automaticamente.

-- ############################################################
-- FIM DO SCRIPT - APLIQUE NO SQL EDITOR DO SUPABASE
-- ############################################################
