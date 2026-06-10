// SectionScore — Score Forense 12 Dimensões (A+ 93.4/100)
// Pontuação composta das dimensões analíticas da auditoria DETRAN/AM
import { useAuditoria } from "@/contexts/AuditoriaContext";
import { SectionHeader, ForensicCard } from "@/components/ForensicCard";
import { KpiGrid } from "@/components/KpiCard";
import { fmtNum, fmtBRL, parseBRL } from "@/data/helpers";
import { CheckCircle2, Award } from "lucide-react";

export default function SectionScore() {
  const { scoreDimensoes, meta } = useAuditoria();

  const scoreFinal = parseFloat(meta.score_final || "94");
  const conceito = meta.score_conceito || "A+ (EXCEPCIONAL)";
  const evValor = parseBRL(meta.ev_valor_esperado || "0");
  const evHonorarios = parseBRL(meta.ev_honorarios || "0");
  const monteCarlo = parseBRL(meta.monte_carlo_p50 || "0");
  const pRec = parseFloat(meta.p_recuperacao || "0.95") * 100;

  // Dados para o panorama de dimensões (ordenado por score)
  const chartData = [...scoreDimensoes]
    .sort((a, b) => parseFloat(b.score || "0") - parseFloat(a.score || "0"))
    .map((d) => ({
      name: d.dimensao,
      value: parseFloat(d.score || "0"),
      peso: parseFloat(d.pesoPct || "0"),
    }));

  const kpis = [
    { label: "Score Final", value: fmtNum(scoreFinal, 1), detail: conceito, big: true, green: true },
    { label: "Prob. Recuperação", value: `${pRec.toFixed(0)}%`, detail: "Probabilidade Bayesiana" },
    { label: "EV Valor Esperado", value: fmtBRL(evValor), detail: "Expectativa ajustada ao risco" },
    { label: "Monte Carlo P50", value: fmtBRL(monteCarlo), detail: "Mediana da simulação" },
    { label: "Honorários Esperados", value: fmtBRL(evHonorarios), detail: "Contrato 002/2026 · 20%" },
    { label: "Dimensões Auditadas", value: `${scoreDimensoes.length}`, detail: "Critérios independentes" },
  ];

  return (
    <>
      <SectionHeader
        title="Score Forense 12 Dimensões"
        desc={`Pontuação composta · ${conceito} · Auditoria v10 consolidada em ${meta.atualizacao_data || "16/04/2026"}`}
      />
      <KpiGrid kpis={kpis} />

      <ForensicCard title="Panorama das Dimensões" className="mt-6">
        <div className="space-y-2.5">
          {chartData.map((d) => {
            const nivel = d.value >= 95 ? "ok" : d.value >= 85 ? "warn" : "err";
            const color =
              nivel === "ok"
                ? "bg-emerald-400/80"
                : nivel === "warn"
                  ? "bg-amber-400/80"
                  : "bg-red-400/80";
            const textColor =
              nivel === "ok"
                ? "text-emerald-400"
                : nivel === "warn"
                  ? "text-amber-400"
                  : "text-red-400";
            return (
              <div key={d.name} className="flex items-center gap-3">
                <div className="w-48 md:w-56 shrink-0 text-[11px] font-sans text-foreground/90 truncate text-right tracking-tight">
                  {d.name}
                  <span className="ml-1.5 text-[9px] font-mono text-muted-foreground">
                    {d.peso.toFixed(0)}%
                  </span>
                </div>
                <div className="flex-1 h-6 bg-muted/30 rounded-sm overflow-hidden relative border border-border/40">
                  <div
                    className={`h-full ${color} transition-all duration-500`}
                    style={{ width: `${Math.min(100, d.value)}%` }}
                  />
                  <div className="absolute inset-0 flex items-center px-2">
                    <div className="w-full flex justify-end">
                      <span className={`text-[11px] font-mono font-semibold tabular-nums ${textColor}`}>
                        {d.value.toFixed(1)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
        <div className="mt-4 pt-3 border-t border-border/40 flex items-center justify-between text-[10px] font-mono text-muted-foreground">
          <span>12 critérios independentes · ordenado por performance</span>
          <span className="flex items-center gap-3">
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-sm bg-emerald-400/80" />≥ 95</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-sm bg-amber-400/80" />85–95</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-sm bg-red-400/80" />&lt; 85</span>
          </span>
        </div>
      </ForensicCard>

      <div className="mt-6 grid gap-3 md:grid-cols-2">
        {scoreDimensoes.map((d) => {
          const score = parseFloat(d.score || "0");
          const peso = parseFloat(d.pesoPct || "0");
          const contrib = parseFloat(d.contribuicao || "0");
          const nivel = score >= 95 ? "ok" : score >= 85 ? "warn" : "err";
          return (
            <div
              key={d.id}
              className="bg-card border border-border p-4 rounded"
            >
              <div className="flex items-start justify-between gap-3 mb-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <Award className="h-4 w-4 text-primary" />
                    <h4 className="font-display text-base text-foreground font-semibold">
                      {d.dimensao}
                    </h4>
                  </div>
                  <div className="text-[10px] font-mono text-muted-foreground mt-1">
                    peso {peso.toFixed(0)}% · contribuição {contrib.toFixed(1)} pts
                  </div>
                </div>
                <div className="text-right">
                  <div
                    className={
                      "font-display text-2xl font-bold " +
                      (nivel === "ok"
                        ? "text-emerald-400"
                        : nivel === "warn"
                          ? "text-amber-400"
                          : "text-red-400")
                    }
                  >
                    {score.toFixed(1)}
                  </div>
                  <div className="text-[9px] uppercase tracking-wider text-muted-foreground">
                    / 100
                  </div>
                </div>
              </div>
              {/* Barra de progresso */}
              <div className="w-full h-1.5 bg-muted/40 rounded overflow-hidden mb-3">
                <div
                  className={
                    "h-full transition-all " +
                    (nivel === "ok"
                      ? "bg-emerald-400"
                      : nivel === "warn"
                        ? "bg-amber-400"
                        : "bg-red-400")
                  }
                  style={{ width: `${Math.min(100, score)}%` }}
                />
              </div>
              {/* Detalhes */}
              {Array.isArray(d.detalhes) && d.detalhes.length > 0 && (
                <ul className="space-y-1 text-[11px] text-muted-foreground">
                  {(d.detalhes as string[]).slice(0, 6).map((item, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <CheckCircle2 className="h-3 w-3 text-primary/70 flex-shrink-0 mt-0.5" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          );
        })}
      </div>
    </>
  );
}
