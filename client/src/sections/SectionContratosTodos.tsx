import { dashboard } from "@/data/helpers";
import { SectionHeader, ForensicCard } from "@/components/ForensicCard";
import { ForensicTable } from "@/components/ForensicTable";

export default function SectionContratosTodos() {
  const sec = dashboard.contratos_todos;
  return (
    <div className="space-y-5">
      <SectionHeader title={sec.title} desc={sec.desc} />
      {sec.tables[0] && (
        <ForensicCard title="Quadro Geral · 18 Contratos" variant="highlight">
          <ForensicTable
            table={sec.tables[0]}
            searchable
            searchPlaceholder="Buscar contrato, objeto, regime..."
            maxHeight="75vh"
          />
        </ForensicCard>
      )}
    </div>
  );
}
