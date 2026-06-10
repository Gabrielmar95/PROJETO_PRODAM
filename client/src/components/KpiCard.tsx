import { cn } from "@/lib/utils";
import type { Kpi } from "@/data/types";

export function KpiCard({ kpi, idx = 0 }: { kpi: Kpi; idx?: number }) {
  // Stagger orquestrado: cada KPI entra com 60ms de delay relativo ao anterior
  // Limitado a 12 para evitar atrasos perceptíveis em grids muito longas
  const delay = Math.min(idx, 12) * 60;
  return (
    <div
      className={cn(
        "kpi-card lift-on-hover relative overflow-hidden",
        kpi.big && "kpi-big",
        kpi.green && "kpi-green"
      )}
      style={{ animationDelay: `${delay}ms` }}
    >
      {kpi.big && (
        <span
          aria-hidden
          className="pointer-events-none absolute -right-4 -top-4 w-14 h-14 rounded-full border border-[color:var(--gold)]/20"
        />
      )}
      <div className="small-caps text-[10px] text-[color:var(--t3)] font-semibold">
        {kpi.label}
      </div>
      <div
        className={cn(
          "font-display font-semibold leading-[1.05] mt-1.5 tabular-nums",
          kpi.big ? "text-[26px] sm:text-[32px] lg:text-[36px] whitespace-nowrap" : "text-[21px]",
          kpi.green ? "text-[color:var(--ok)]" : "text-primary"
        )}
        style={{ fontFeatureSettings: '"onum", "tnum"' }}
      >
        {kpi.value}
      </div>
      {kpi.detail && (
        <div className="text-[10px] text-[color:var(--t2)] mt-1 leading-snug">
          {kpi.detail}
        </div>
      )}
    </div>
  );
}

export function KpiGrid({ kpis }: { kpis: Kpi[] }) {
  if (!kpis.length) return null;
  return (
    <div className="kpi-grid stagger grid gap-3 grid-cols-[repeat(auto-fit,minmax(180px,1fr))] mb-6">
      {kpis.map((kpi, i) => (
        <KpiCard key={i} kpi={kpi} idx={i} />
      ))}
    </div>
  );
}

export function Badge({ tone, children }: { tone: string; children: React.ReactNode }) {
  const toneMap: Record<string, string> = {
    gold: "bg-primary/15 text-primary",
    ok: "bg-[color:var(--ok)]/15 text-[color:var(--ok)]",
    warn: "bg-[color:var(--warn)]/15 text-[color:var(--warn)]",
    err: "bg-[color:var(--err)]/15 text-[color:var(--err)]",
    info: "bg-[color:var(--info)]/15 text-[color:var(--info)]",
    purple: "bg-[color:var(--purple)]/15 text-[color:var(--purple)]",
    cyan: "bg-[color:var(--cyan)]/15 text-[color:var(--cyan)]",
  };
  return (
    <span className={cn("badge-forense", toneMap[tone] || toneMap.gold)}>
      {children}
    </span>
  );
}
