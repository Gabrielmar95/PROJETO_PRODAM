import { dashboard, fmtBRL } from "@/data/helpers";
import { SectionHeader, ForensicCard } from "@/components/ForensicCard";
import { KpiGrid } from "@/components/KpiCard";
import { useFilters } from "@/contexts/FilterContext";

export default function SectionDecomposicao() {
  const sec = dashboard.decomposicao;
  const { allFaturas } = useFilters();

  const top10 = [...allFaturas].sort((a, b) => b.c1Num - a.c1Num).slice(0, 10);

  return (
    <div className="space-y-5">
      <SectionHeader title={sec.title} desc={sec.desc} />
      <KpiGrid kpis={sec.kpis} />

      <ForensicCard title="Decomposição: Saldo + Encargos = C1 SELIC" variant="highlight">
        <div className="text-[11px] text-muted-foreground mb-3">
          Top 10 faturas ordenadas por valor atualizado. Barra verde = Saldo Original · Barra dourada = Encargos (Correção + Juros SELIC).
        </div>
        <div className="space-y-3">
          {top10.map((f, i) => {
            const encargos = f.c1Num - f.saldoNum;
            const totalPct = (f.saldoNum / f.c1Num) * 100;
            return (
              <div key={f.idx} className="grid grid-cols-12 gap-3 items-center text-[11px]">
                <div className="col-span-1 text-primary font-mono text-[10px] text-right">#{i + 1}</div>
                <div className="col-span-2 font-mono text-[10px] text-[color:var(--t2)]">
                  NF {f.nf}
                  <div className="text-[9px] text-[color:var(--t4)]">{f.contrato}</div>
                </div>
                <div className="col-span-6">
                  <div className="relative h-6 rounded overflow-hidden bg-[color:var(--bg-3)] border border-border">
                    <div
                      className="absolute inset-y-0 left-0 bg-[color:var(--ok)]/60"
                      style={{ width: `${totalPct}%` }}
                    >
                      <span className="absolute inset-0 flex items-center justify-end pr-2 text-[9px] font-mono text-background font-semibold">
                        {fmtBRL(f.saldoNum)}
                      </span>
                    </div>
                    <div
                      className="absolute inset-y-0 bg-primary/70"
                      style={{ left: `${totalPct}%`, right: 0 }}
                    >
                      <span className="absolute inset-0 flex items-center justify-start pl-2 text-[9px] font-mono text-background font-semibold">
                        +{fmtBRL(encargos)}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="col-span-3 text-right">
                  <div className="font-mono text-[11px] text-primary font-semibold">{fmtBRL(f.c1Num)}</div>
                  <div className="text-[9px] text-[color:var(--t4)]">{f.fator}</div>
                </div>
              </div>
            );
          })}
        </div>

        <div className="flex items-center gap-4 mt-5 pt-3 border-t border-border/50 text-[10px]">
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-sm bg-[color:var(--ok)]/60 border border-[color:var(--ok)]" />
            <span className="text-muted-foreground">Saldo Original</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-sm bg-primary/70 border border-primary" />
            <span className="text-muted-foreground">Encargos (Correção + Juros SELIC)</span>
          </div>
        </div>
      </ForensicCard>
    </div>
  );
}

export { fmtBRL };
