import { dashboard, fmtBRL } from "@/data/helpers";
import { SectionHeader, ForensicCard } from "@/components/ForensicCard";
import { ForensicTable } from "@/components/ForensicTable";
import { ForensicBar } from "@/components/Charts";
import { useFilters } from "@/contexts/FilterContext";

export default function SectionFaturasContrato() {
  const sec = dashboard.faturas_contrato;
  const { filteredFaturas, filters, applyDrillDown } = useFilters();

  const porContrato = Object.values(
    filteredFaturas.reduce<Record<string, { name: string; value: number; count: number }>>((acc, f) => {
      if (!acc[f.contrato]) acc[f.contrato] = { name: f.contrato, value: 0, count: 0 };
      acc[f.contrato].value += f.c1Num;
      acc[f.contrato].count += 1;
      return acc;
    }, {})
  )
    .sort((a, b) => b.value - a.value)
    .slice(0, 18);

  return (
    <div className="space-y-5">
      <SectionHeader title={sec.title} desc={sec.desc} />

      <ForensicCard title="Top Contratos por Valor Atualizado (C1 SELIC)" variant="highlight">
        <div className="text-[10px] text-muted-foreground/80 mb-2 italic">
          Clique em uma barra para filtrar o dashboard inteiro por contrato.
        </div>
        <ForensicBar
          data={porContrato}
          horizontal
          valueFormatter={(v) =>
            v >= 1_000_000 ? `R$ ${(v / 1_000_000).toFixed(2)}M` : `R$ ${(v / 1000).toFixed(0)}k`
          }
          height={Math.max(300, porContrato.length * 24)}
          onBarClick={(name) => applyDrillDown("contrato", name)}
          activeName={filters.contrato !== "all" ? filters.contrato : undefined}
        />
      </ForensicCard>

      {sec.tables[0] && (
        <ForensicCard title="Quadro por Contrato">
          <ForensicTable table={sec.tables[0]} searchable searchPlaceholder="Buscar contrato..." maxHeight="700px" />
        </ForensicCard>
      )}
    </div>
  );
}

export { fmtBRL };
