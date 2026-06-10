import { dashboard } from "@/data/helpers";
import { SectionHeader, ForensicCard } from "@/components/ForensicCard";
import { ForensicTable } from "@/components/ForensicTable";
import { KpiGrid } from "@/components/KpiCard";

export default function SectionCorrecaoGeral() {
  const sec = dashboard.correcao_geral;
  return (
    <div className="space-y-5">
      <SectionHeader title={sec.title} desc={sec.desc} />
      <KpiGrid kpis={sec.kpis} />

      {sec.tables[0] && (
        <ForensicCard title="Séries de Índices Utilizados" variant="highlight">
          <ForensicTable table={sec.tables[0]} maxHeight="400px" />
        </ForensicCard>
      )}

      {sec.cards.map((c, i) => (
        <ForensicCard key={i} title={c.title} variant={i === 0 ? "highlight" : "default"}>
          <div className="text-[11.5px] text-[color:var(--t2)] leading-relaxed whitespace-pre-line">
            {c.text}
          </div>
        </ForensicCard>
      ))}
    </div>
  );
}
