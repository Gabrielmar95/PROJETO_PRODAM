/**
 * S3-M15 — Indicador de "última atualização" dos dados do dashboard.
 *
 * Lê `updatedAt` do DashboardContext (timestamp ISO do TiDB) e mostra
 * tempo relativo + cor de estado:
 *   - verde:  até 24h
 *   - âmbar:  24h–7 dias
 *   - vermelho: > 7 dias
 *
 * Atualiza a cada 60s automaticamente.
 */
import { useEffect, useMemo, useState } from "react";
import { Clock, AlertTriangle, CheckCircle2 } from "lucide-react";
import { useDashboardMeta } from "@/contexts/DashboardContext";

type Freshness = "fresh" | "stale" | "old";

function classify(updatedAt: string): { kind: Freshness; ageHours: number } {
  const t = Date.parse(updatedAt);
  if (Number.isNaN(t)) return { kind: "old", ageHours: Infinity };
  const ageMs = Date.now() - t;
  const ageHours = ageMs / (1000 * 60 * 60);
  if (ageHours < 24) return { kind: "fresh", ageHours };
  if (ageHours < 24 * 7) return { kind: "stale", ageHours };
  return { kind: "old", ageHours };
}

function relative(ageHours: number): string {
  if (ageHours < 1) {
    const m = Math.max(1, Math.floor(ageHours * 60));
    return `há ${m} min`;
  }
  if (ageHours < 24) {
    const h = Math.floor(ageHours);
    return `há ${h}h`;
  }
  const d = Math.floor(ageHours / 24);
  if (d < 30) return `há ${d}d`;
  const months = Math.floor(d / 30);
  return `há ${months} mês${months > 1 ? "es" : ""}`;
}

export interface FreshnessIndicatorProps {
  /** Variante visual: chip (compacto, header) ou inline (linha de texto). */
  variant?: "chip" | "inline";
  /** Esconde o texto "Atualizado", deixando só ícone+tempo. */
  iconOnly?: boolean;
}

export function FreshnessIndicator({
  variant = "chip",
  iconOnly = false,
}: FreshnessIndicatorProps) {
  const { updatedAt } = useDashboardMeta();
  const [, setTick] = useState(0);

  // Re-render a cada 60s
  useEffect(() => {
    const id = window.setInterval(() => setTick((t) => t + 1), 60_000);
    return () => window.clearInterval(id);
  }, []);

  const { kind, ageHours } = useMemo(() => classify(updatedAt), [updatedAt]);
  const label = useMemo(() => relative(ageHours), [ageHours]);
  const absolute = useMemo(() => {
    try {
      return new Date(updatedAt).toLocaleString("pt-BR", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return updatedAt;
    }
  }, [updatedAt]);

  const Icon =
    kind === "fresh" ? CheckCircle2 : kind === "stale" ? Clock : AlertTriangle;

  const colorClass =
    kind === "fresh"
      ? "text-emerald-700 border-emerald-300/60 bg-emerald-50/60 dark:text-emerald-300 dark:border-emerald-700/40 dark:bg-emerald-950/30"
      : kind === "stale"
        ? "text-amber-800 border-amber-300/60 bg-amber-50/60 dark:text-amber-200 dark:border-amber-700/40 dark:bg-amber-950/30"
        : "text-red-800 border-red-300/60 bg-red-50/60 dark:text-red-200 dark:border-red-700/40 dark:bg-red-950/30";

  const titleAttr = `Última atualização: ${absolute}`;

  if (variant === "inline") {
    return (
      <span
        title={titleAttr}
        aria-label={`Dados atualizados ${label}`}
        className={`inline-flex items-center gap-1 text-[10px] font-mono ${
          kind === "fresh"
            ? "text-emerald-700 dark:text-emerald-300"
            : kind === "stale"
              ? "text-amber-700 dark:text-amber-300"
              : "text-red-700 dark:text-red-300"
        }`}
        data-testid="freshness-inline"
        data-freshness={kind}
      >
        <Icon size={10} strokeWidth={1.8} />
        {!iconOnly && <span className="uppercase tracking-[0.08em]">Atualizado</span>}
        <span>{label}</span>
      </span>
    );
  }

  return (
    <span
      title={titleAttr}
      aria-label={`Dados atualizados ${label}`}
      className={`inline-flex items-center gap-1.5 px-2 py-[3px] rounded-[4px] border text-[10px] font-mono ${colorClass} print-hide`}
      data-testid="freshness-chip"
      data-freshness={kind}
    >
      <Icon size={11} strokeWidth={1.8} />
      {!iconOnly && (
        <span className="uppercase tracking-[0.08em]">Atualizado</span>
      )}
      <span className="font-semibold">{label}</span>
    </span>
  );
}
