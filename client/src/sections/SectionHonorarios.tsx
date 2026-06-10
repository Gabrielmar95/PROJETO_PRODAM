import { dashboard, parseBRL } from "@/data/helpers";
import { SectionHeader, ForensicCard } from "@/components/ForensicCard";
import { ForensicTable } from "@/components/ForensicTable";
import { ForensicBar } from "@/components/Charts";
import { KpiGrid } from "@/components/KpiCard";

export default function SectionHonorarios() {
  const sec = dashboard.honorarios;
  const table = sec.tables[0];

  // Supor que table tem colunas [Contrato, Regime, Faturas, Valor C1, Honorarios, ...]
  const chartData =
    table?.rows
      .filter((r) => !r[0].toLowerCase().startsWith("total"))
      .slice(0, 18)
      .map((r) => ({
        name: r[0],
        value: parseBRL(r[4] || r[r.length - 1]),
      })) || [];

  return (
    <div className="space-y-5">
      <SectionHeader title={sec.title} desc={sec.desc} />
      <KpiGrid kpis={sec.kpis} />

      {chartData.length > 0 && (
        <ForensicCard title="Honorários Sucumbenciais por Contrato" variant="highlight">
          <ForensicBar
            data={chartData}
            horizontal
            valueFormatter={(v) =>
              v >= 1_000_000 ? `R$ ${(v / 1_000_000).toFixed(2)}M` : `R$ ${(v / 1000).toFixed(0)}k`
            }
            height={Math.max(300, chartData.length * 24)}
          />
        </ForensicCard>
      )}

      {table && (
        <ForensicCard title="Quadro Detalhado">
          <ForensicTable table={table} maxHeight="600px" searchable />
        </ForensicCard>
      )}

      {sec.cards.map((c, i) => (
        <ForensicCard key={i} title={c.title} variant="default">
          <div className="text-[11.5px] text-[color:var(--t2)] leading-relaxed whitespace-pre-line">
            {c.text}
          </div>
        </ForensicCard>
      ))}
    </div>
  );
}
