import { dashboard } from "@/data/helpers";
import { SectionHeader, ForensicCard } from "@/components/ForensicCard";
import { ForensicTable } from "@/components/ForensicTable";
import { ForensicPie } from "@/components/Charts";
import { useFilters } from "@/contexts/FilterContext";
import { fmtBRL } from "@/data/helpers";

export default function SectionFaturasRegime() {
  const sec = dashboard.faturas_regime;
  const { filteredFaturas, filters, applyDrillDown } = useFilters();

  const porRegime = Object.values(
    filteredFaturas.reduce<Record<string, { name: string; value: number; count: number }>>((acc, f) => {
      const k = f.regime || "Outros";
      if (!acc[k]) acc[k] = { name: k, value: 0, count: 0 };
      acc[k].value += f.c1Num;
      acc[k].count += 1;
      return acc;
    }, {})
  );

  return (
    <div className="space-y-5">
      <SectionHeader title={sec.title} desc={sec.desc} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ForensicCard title="Distribuição por Valor C1 (SELIC)">
          <div className="text-[10px] text-muted-foreground/80 mb-2 italic">
            Clique em uma fatia para aplicar filtro de regime.
          </div>
          <ForensicPie
            data={porRegime}
            valueFormatter={fmtBRL}
            height={320}
            onSliceClick={(name) => applyDrillDown("regime", name)}
            activeName={filters.regime !== "all" ? filters.regime : undefined}
          />
        </ForensicCard>
        <ForensicCard title="Distribuição por Quantidade de Faturas">
          <ForensicPie
            data={porRegime.map((r) => ({ name: r.name, value: r.count }))}
            valueFormatter={(v) => `${v} faturas`}
            height={320}
            onSliceClick={(name) => applyDrillDown("regime", name)}
            activeName={filters.regime !== "all" ? filters.regime : undefined}
          />
        </ForensicCard>
      </div>

      {sec.tables[0] && (
        <ForensicCard title="Quadro por Regime Jurídico">
          <ForensicTable table={sec.tables[0]} maxHeight="500px" />
        </ForensicCard>
      )}

      {sec.cards.map((c, i) => (
        <ForensicCard key={i} title={c.title} variant="default">
          <div className="text-[11.5px] text-[color:var(--t2)] leading-relaxed whitespace-pre-line">
            {c.text}
          </div>
          {sec.tables[i + 1] && (
            <div className="mt-3">
              <ForensicTable table={sec.tables[i + 1]} maxHeight="400px" />
            </div>
          )}
        </ForensicCard>
      ))}
    </div>
  );
}
