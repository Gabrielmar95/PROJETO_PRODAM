// WaterfallChart — gráfico em cascata dos 3 cenários (C1 SELIC / C2 Poupança / C3 1% a.m.)
// Mostra visualmente: Saldo Inicial → Correção/Juros → Valor Total
import { fmtBRL } from "@/data/helpers";

type Step = {
  label: string;
  value: number;
  type: "base" | "delta" | "total";
};

type Scenario = {
  name: string;
  code: string;
  total: number;
  color: string;
};

export default function WaterfallChart({
  saldo,
  scenarios,
}: {
  saldo: number;
  scenarios: Scenario[];
}) {
  const maxTotal = Math.max(...scenarios.map((s) => s.total));

  return (
    <div className="space-y-6">
      {scenarios.map((sc) => {
        const delta = sc.total - saldo;
        const steps: Step[] = [
          { label: "Saldo Original", value: saldo, type: "base" },
          { label: `Correção ${sc.code}`, value: delta, type: "delta" },
          { label: `Total ${sc.code}`, value: sc.total, type: "total" },
        ];

        const saldoPct = (saldo / maxTotal) * 100;
        const deltaPct = (delta / maxTotal) * 100;
        const totalPct = (sc.total / maxTotal) * 100;

        return (
          <div key={sc.code} className="border border-border/50 rounded p-4 bg-card/30 lift-on-hover">
            {/* Header do cenário */}
            <div className="flex items-baseline justify-between mb-4">
              <div>
                <div className="text-[10px] font-mono tracking-[0.2em] uppercase text-muted-foreground">
                  {sc.name}
                </div>
                <div className="font-display text-lg text-primary mt-0.5">
                  Cenário <span className="italic">{sc.code}</span>
                </div>
              </div>
              <div className="text-right">
                <div className="font-display text-2xl font-semibold text-primary tabular-nums">
                  {fmtBRL(sc.total)}
                </div>
                <div className="text-[10px] font-mono text-muted-foreground">
                  +{((delta / saldo) * 100).toFixed(1)}% sobre saldo original
                </div>
              </div>
            </div>

            {/* Cascata */}
            <div className="relative space-y-2">
              {/* Saldo base */}
              <div className="flex items-center gap-3">
                <div className="w-32 text-[10px] font-mono text-muted-foreground text-right">
                  {steps[0].label}
                </div>
                <div className="flex-1 relative h-8 bg-muted/10 rounded-sm overflow-hidden">
                  <div
                    className="absolute inset-y-0 left-0 bg-[color:var(--gold-deep)]/60 border-r-2 border-[color:var(--gold)]"
                    style={{ width: `${saldoPct}%` }}
                  />
                  <span className="absolute inset-0 flex items-center px-3 text-[10.5px] font-mono tabular-nums text-primary-foreground mix-blend-difference">
                    {fmtBRL(saldo)}
                  </span>
                </div>
                <div className="w-6 text-right text-[10px] font-mono text-primary">1.00x</div>
              </div>

              {/* Delta (correção) */}
              <div className="flex items-center gap-3">
                <div className="w-32 text-[10px] font-mono text-muted-foreground text-right">
                  + {steps[1].label}
                </div>
                <div className="flex-1 relative h-8 bg-muted/10 rounded-sm overflow-hidden">
                  {/* Pula para depois do saldo */}
                  <div
                    className="absolute inset-y-0 border-r border-dashed border-[color:var(--gold)]/40"
                    style={{ left: `${saldoPct}%`, width: `${deltaPct}%`, backgroundColor: sc.color + "88" }}
                  />
                  <span
                    className="absolute inset-y-0 flex items-center text-[10.5px] font-mono tabular-nums text-primary"
                    style={{ left: `calc(${saldoPct}% + 8px)` }}
                  >
                    + {fmtBRL(delta)}
                  </span>
                </div>
                <div className="w-6 text-right text-[10px] font-mono" style={{ color: sc.color }}>
                  +{((delta / saldo) * 100).toFixed(0)}%
                </div>
              </div>

              {/* Total */}
              <div className="flex items-center gap-3 pt-2 border-t border-primary/20">
                <div className="w-32 text-[10px] font-mono text-primary font-semibold text-right">
                  = {steps[2].label}
                </div>
                <div className="flex-1 relative h-9 bg-background rounded-sm overflow-hidden border border-primary/40">
                  <div
                    className="absolute inset-y-0 left-0 bg-gradient-to-r from-[color:var(--gold-deep)] to-[color:var(--gold)]"
                    style={{ width: `${totalPct}%` }}
                  />
                  <span className="absolute inset-0 flex items-center justify-end pr-3 text-[11px] font-mono tabular-nums font-semibold text-black mix-blend-difference">
                    {fmtBRL(sc.total)}
                  </span>
                </div>
                <div className="w-6 text-right text-[10px] font-mono text-primary font-semibold">
                  {(sc.total / saldo).toFixed(2)}x
                </div>
              </div>
            </div>
          </div>
        );
      })}

      {/* Comparação final */}
      <div className="mt-6 p-4 border border-primary/30 bg-primary/5 rounded">
        <div className="text-[10px] font-mono tracking-[0.2em] uppercase text-primary mb-2">
          Comparação
        </div>
        <div className="grid grid-cols-3 gap-3 text-center">
          {scenarios.map((sc) => (
            <div key={sc.code}>
              <div className="text-[10px] font-mono text-muted-foreground uppercase">{sc.code}</div>
              <div className="font-display text-lg text-primary tabular-nums mt-1">
                {fmtBRL(sc.total)}
              </div>
              <div
                className="h-1 mt-2 rounded-full"
                style={{ backgroundColor: sc.color, width: `${(sc.total / maxTotal) * 100}%`, marginInline: "auto" }}
              />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
