// FreshnessSeal.tsx — selo de frescor exibindo versão profiles, data-base, sha256 e última sync
// Fonte: tabela `meta` do TiDB (populada pelo seed_v3.mjs)

import { useEffect, useState } from "react";
import { Database, CheckCircle2 } from "lucide-react";

interface Meta {
  profiles_version?: string;
  profiles_data_base?: string;
  profiles_sha256?: string;
  prodam_db_sha256?: string;
  seed_v3_executed_at?: string;
  valor_canonico?: string;
  forca_probatoria?: string;
}

export default function FreshnessSeal() {
  const [meta, setMeta] = useState<Meta | null>(null);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    fetch("/api/trpc/dashboard.get")
      .then((r) => r.json())
      .then((d) => {
        const raw = d?.result?.data?.json?.meta;
        if (raw) {
          setMeta({
            profiles_version: raw.profiles_version,
            profiles_data_base: raw.profiles_data_base,
            profiles_sha256: raw.profiles_sha256,
            prodam_db_sha256: raw.prodam_db_sha256,
            seed_v3_executed_at: raw.seed_v3_executed_at,
            valor_canonico: raw.valor_canonico,
            forca_probatoria: raw.forca_probatoria,
          });
        }
      })
      .catch(() => {});
  }, []);

  if (!meta?.profiles_version) return null;

  const syncDate = meta.seed_v3_executed_at
    ? new Date(meta.seed_v3_executed_at).toLocaleString("pt-BR", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      })
    : "—";

  const shortHash = (h?: string) => (h ? h.substring(0, 8) + "…" : "—");

  return (
    <div className="relative">
      <button
        onClick={() => setExpanded((v) => !v)}
        className="inline-flex items-center gap-1.5 px-2 py-1 rounded border border-[color:var(--ok)]/30 bg-[color:var(--ok)]/10 hover:bg-[color:var(--ok)]/15 transition-colors text-[10px] font-mono text-[color:var(--ok)]"
        title="Clique para ver detalhes de integridade"
      >
        <CheckCircle2 className="h-3 w-3" />
        <span className="small-caps font-semibold tracking-wider">Dados reais · v{meta.profiles_version}</span>
        <span className="text-[9px] opacity-70">|</span>
        <span className="text-[9px]">data-base {meta.profiles_data_base}</span>
      </button>

      {expanded && (
        <div className="absolute right-0 top-full mt-1 z-40 w-80 bg-[color:var(--bg-2)] border border-border rounded-md shadow-xl p-3 text-[10px] space-y-1.5">
          <div className="flex items-center gap-1.5 mb-2 pb-1.5 border-b border-border/50">
            <Database className="h-3 w-3 text-primary" />
            <span className="small-caps text-primary font-semibold tracking-wider">
              Integridade de Fontes
            </span>
          </div>
          <div className="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1">
            <span className="text-[color:var(--t3)]">profiles.json</span>
            <span className="font-mono text-[color:var(--ok)]">v{meta.profiles_version}</span>

            <span className="text-[color:var(--t3)]">data-base</span>
            <span className="font-mono">{meta.profiles_data_base}</span>

            <span className="text-[color:var(--t3)]">sha256 profiles</span>
            <span className="font-mono" title={meta.profiles_sha256}>
              {shortHash(meta.profiles_sha256)}
            </span>

            <span className="text-[color:var(--t3)]">sha256 prodam.db</span>
            <span className="font-mono" title={meta.prodam_db_sha256}>
              {shortHash(meta.prodam_db_sha256)}
            </span>

            <span className="text-[color:var(--t3)]">última sincronização</span>
            <span className="font-mono">{syncDate}</span>

            <span className="text-[color:var(--t3)]">valor canônico</span>
            <span className="font-mono text-primary">
              {meta.valor_canonico
                ? Number(meta.valor_canonico).toLocaleString("pt-BR", {
                    style: "currency",
                    currency: "BRL",
                  })
                : "—"}
            </span>

            <span className="text-[color:var(--t3)]">força probatória</span>
            <span className="font-mono text-[color:var(--ok)] font-semibold">
              {meta.forca_probatoria}
            </span>
          </div>
          <div className="pt-1.5 mt-2 border-t border-border/50 text-[9px] text-[color:var(--t4)] leading-tight">
            Fonte Nível 1: profiles.json (Gabrielmar95/PRODAM_DOCS). Nível 2: detran_master.json v11. Nível 3: prodam.db (read-only).
          </div>
        </div>
      )}
    </div>
  );
}
