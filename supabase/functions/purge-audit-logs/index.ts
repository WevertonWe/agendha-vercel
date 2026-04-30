// supabase/functions/purge-audit-logs/index.ts
//
// Edge Function Cron — Supabase
// Deleta automaticamente logs com mais de 7 dias da tabela `audit_logs`.
//
// Deploy:
//   supabase functions deploy purge-audit-logs --no-verify-jwt
//
// Agendar via Dashboard → Cron Jobs:
//   Schedule: 0 3 * * *   (todo dia às 03:00 UTC)
//   Function: purge-audit-logs
//
// Ou via SQL no Supabase (usando pg_cron):
//   SELECT cron.schedule(
//     'purge-audit-logs-daily',
//     '0 3 * * *',
//     $$
//       DELETE FROM audit_logs
//       WHERE timestamp < NOW() - INTERVAL '7 days';
//     $$
//   );

import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const TTL_DAYS = parseInt(Deno.env.get("AUDIT_LOG_TTL_DAYS") ?? "7", 10);

Deno.serve(async (req: Request) => {
  // Verificação de segurança: aceita apenas chamadas autorizadas
  const authHeader = req.headers.get("Authorization");
  if (authHeader !== `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`) {
    return new Response(JSON.stringify({ error: "Unauthorized" }), {
      status: 401,
      headers: { "Content-Type": "application/json" },
    });
  }

  const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);

  // Calcula o threshold de expiração
  const threshold = new Date();
  threshold.setDate(threshold.getDate() - TTL_DAYS);
  const thresholdISO = threshold.toISOString();

  try {
    // Conta registros antes da purga (para relatório)
    const { count: totalBefore } = await supabase
      .from("audit_logs")
      .select("id", { count: "exact", head: true })
      .lt("timestamp", thresholdISO);

    // Executa a purga
    const { error } = await supabase
      .from("audit_logs")
      .delete()
      .lt("timestamp", thresholdISO);

    if (error) {
      console.error("[purge-audit-logs] Erro ao purgar logs:", error);
      return new Response(
        JSON.stringify({ success: false, error: error.message }),
        { status: 500, headers: { "Content-Type": "application/json" } }
      );
    }

    const report = {
      success: true,
      purged_count: totalBefore ?? 0,
      ttl_days: TTL_DAYS,
      threshold: thresholdISO,
      executed_at: new Date().toISOString(),
    };

    console.log("[purge-audit-logs] Purga concluída:", report);

    return new Response(JSON.stringify(report), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  } catch (err) {
    console.error("[purge-audit-logs] Erro inesperado:", err);
    return new Response(
      JSON.stringify({ success: false, error: String(err) }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
});
