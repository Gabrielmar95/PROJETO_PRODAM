import { dashboard } from "@/data/helpers";
import { SectionHeader, ForensicCard } from "@/components/ForensicCard";
import { ForensicTable } from "@/components/ForensicTable";
import { KpiGrid } from "@/components/KpiCard";

export default function SectionPrescricao() {
  const sec = dashboard.prescricao;
  return (
    <div className="space-y-5">
      <SectionHeader title={sec.title} desc={sec.desc} />
      <KpiGrid kpis={sec.kpis} />

      {sec.cards.map((c, i) => (
        <ForensicCard
          key={i}
          title={c.title}
          variant={c.title.toLowerCase().includes("prescrit") ? "alert" : i === 0 ? "highlight" : "default"}
        >
          <div className="text-[11.5px] text-[color:var(--t2)] leading-relaxed whitespace-pre-line">
            {c.text}
          </div>
          {sec.tables[i] && sec.tables[i].rows.length > 0 && (
            <div className="mt-3">
              <ForensicTable table={sec.tables[i]} maxHeight="400px" />
            </div>
          )}
        </ForensicCard>
      ))}
    </div>
  );
}
