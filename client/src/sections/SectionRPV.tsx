import { dashboard, fmtBRL } from "@/data/helpers";
import { SectionHeader, ForensicCard } from "@/components/ForensicCard";
import { KpiGrid } from "@/components/KpiCard";
import { useFilters } from "@/contexts/FilterContext";
import { ForensicPie } from "@/components/Charts";

const TETO_RPV_AM = 30360.0;

export default function SectionRPV() {
  const sec = dashboard.rpv;
  const { allFaturas } = useFilters();

  const rpv = allFaturas.filter((f) => f.c1Num <= TETO_RPV_AM);
  const precatorio = allFaturas.filter((f) => f.c1Num > TETO_RPV_AM);

  const distribuicao = [
    { name: "RPV Candidatas (≤ R$ 30.360)", value: rpv.length },
    { name: "Precatório (> R$ 30.360)", value: precatorio.length },
  ];

  const valoresPorCategoria = [
    { name: "RPV — Valor C1", value: rpv.reduce((s, f) => s + f.c1Num, 0) },
    { name: "Precatório — Valor C1", value: precatorio.reduce((s, f) => s + f.c1Num, 0) },
  ];

  return (
    <div className="space-y-5">
      <SectionHeader title={sec.title} desc={sec.desc} />
      <KpiGrid kpis={sec.kpis} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ForensicCard title="Classificação por Volume" variant="highlight">
          <ForensicPie
            data={distribuicao}
            valueFormatter={(v) => `${v} faturas`}
            height={300}
          />
        </ForensicCard>
        <ForensicCard title="Classificação por Valor (C1 SELIC)">
          <ForensicPie data={valoresPorCategoria} valueFormatter={fmtBRL} height={300} />
        </ForensicCard>
      </div>

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
