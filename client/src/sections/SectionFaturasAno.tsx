import { dashboard, fmtBRL, parseBRL } from "@/data/helpers";
import { SectionHeader, ForensicCard } from "@/components/ForensicCard";
import { ForensicTable } from "@/components/ForensicTable";
import { ForensicBar, ForensicLine } from "@/components/Charts";
import { useFilters } from "@/contexts/FilterContext";

export default function SectionFaturasAno() {
  const sec = dashboard.faturas_ano;
  const table = sec.tables[0];
  const { filters, applyDrillDown } = useFilters();

  const chartData =
    table?.rows
      .filter((r) => !r[0].toLowerCase().startsWith("total"))
      .map((r) => ({
        name: r[0],
        faturas: parseInt(r[1], 10) || 0,
        saldo: parseBRL(r[2]),
        c1: parseBRL(r[3]),
      })) || [];

  return (
    <div className="space-y-5">
      <SectionHeader title={sec.title} desc={sec.desc} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ForensicCard title="Valor C1 (SELIC) por Ano de Vencimento" variant="highlight">
          <div className="text-[10px] text-muted-foreground/80 mb-2 italic">
            Clique em uma barra para filtrar por ano de vencimento.
          </div>
          <ForensicBar
            data={chartData.map((d) => ({ name: d.name, value: d.c1 }))}
            valueFormatter={(v) =>
              v >= 1_000_000 ? `R$ ${(v / 1_000_000).toFixed(1)}M` : `R$ ${(v / 1000).toFixed(0)}k`
            }
            height={300}
            onBarClick={(name) => applyDrillDown("ano", name)}
            activeName={filters.ano !== "all" ? filters.ano : undefined}
          />
        </ForensicCard>
        <ForensicCard title="Evolução Saldo vs C1">
          <ForensicLine
            data={chartData}
            lines={[
              { key: "saldo", name: "Saldo Original", color: "#6B8FA8" },
              { key: "c1", name: "C1 SELIC", color: "#C5A55A" },
            ]}
            valueFormatter={(v) =>
              v >= 1_000_000 ? `R$ ${(v / 1_000_000).toFixed(1)}M` : `R$ ${(v / 1000).toFixed(0)}k`
            }
            height={300}
          />
        </ForensicCard>
      </div>

      {table && (
        <ForensicCard title="Distribuição Temporal">
          <ForensicTable table={table} maxHeight="400px" />
        </ForensicCard>
      )}
    </div>
  );
}

export { fmtBRL };
