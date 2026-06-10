// SectionMarcos — 148 marcos interruptivos da prescrição
// Art. 202 VI CC: "ato inequívoco do devedor que importe reconhecimento"
import { useMemo } from "react";
import { useAuditoria } from "@/contexts/AuditoriaContext";
import { SectionHeader, ForensicCard } from "@/components/ForensicCard";
import { KpiGrid } from "@/components/KpiCard";
import { ForensicTable } from "@/components/ForensicTable";
import { ForensicBar } from "@/components/Charts";
import { fmtBRL, parseBRL } from "@/data/helpers";
import { ShieldCheck } from "lucide-react";
import TimelineMarcos from "@/components/TimelineMarcos";

export default function SectionMarcos() {
  const { marcosInterruptivos } = useAuditoria();

  const totais = useMemo(() => {
    const vigentes = marcosInterruptivos.filter((m) =>
      (m.prescricao || "").toLowerCase().includes("vigente"),
    ).length;
    const prescritos = marcosInterruptivos.filter((m) =>
      (m.prescricao || "").toLowerCase().includes("prescrit"),
    ).length;
    const cadeiaForte = marcosInterruptivos.filter(
      (m) => m.cadeia === "FORTE" || m.cadeia === "COMPLETA",
    ).length;
    const soma = marcosInterruptivos.reduce(
      (a, m) => a + parseBRL(m.valor || "0"),
      0,
    );
    return { total: marcosInterruptivos.length, vigentes, prescritos, cadeiaForte, soma };
  }, [marcosInterruptivos]);

  const porAno = useMemo(() => {
    const map = new Map<string, number>();
    marcosInterruptivos.forEach((m) => {
      const k = m.ano || "—";
      map.set(k, (map.get(k) || 0) + 1);
    });
    return Array.from(map.entries())
      .sort((a, b) => a[0].localeCompare(b[0]))
      .map(([name, value]) => ({ name, value }));
  }, [marcosInterruptivos]);

  const tableRows = marcosInterruptivos.map((m) => [
    m.ne || "—",
    m.ano || "—",
    m.prescricao || "—",
    m.cadeia || "—",
    m.valor ? fmtBRL(parseBRL(m.valor)) : "—",
    m.dataUltima || "—",
    m.docs ? `${m.docs} docs` : "—",
  ]);

  return (
    <>
      <SectionHeader
        title="Marcos Interruptivos · Art. 202 VI CC"
        desc="Atos inequívocos do DETRAN/AM que importam reconhecimento do débito e reiniciam a prescrição quinquenal"
      />
      <KpiGrid
        kpis={[
          { label: "Marcos Auditados", value: `${totais.total}`, detail: "Total consolidado", big: true },
          { label: "Prescrição Vigente", value: `${totais.vigentes}`, detail: "Cobrança juridicamente viável", green: true },
          { label: "Cadeia Forte/Completa", value: `${totais.cadeiaForte}`, detail: "Defensabilidade máxima" },
          { label: "Valor Atingido", value: fmtBRL(totais.soma), detail: "Montante protegido por marcos" },
        ]}
      />

      <ForensicCard title="Timeline · Cronologia dos Marcos (Art. 202 VI CC)" className="mt-6">
        <TimelineMarcos marcos={marcosInterruptivos} />
      </ForensicCard>

      <ForensicCard title="Distribuição por Ano" className="mt-6">
        <ForensicBar data={porAno} height={260} valueFormatter={(v: number) => `${v} marcos`} />
      </ForensicCard>

      <ForensicCard
        title={`Todos os Marcos (${marcosInterruptivos.length})`}
        className="mt-6"
      >
        <ForensicTable
          table={{
            headers: ["NE", "Ano", "Prescrição", "Cadeia", "Valor", "Última Atualização", "Docs"],
            rows: tableRows,
          }}
          searchable
          showRowIndex
          maxHeight="600px"
        />
      </ForensicCard>

      <div className="mt-4 p-4 border border-primary/30 bg-primary/5 rounded">
        <div className="flex items-start gap-2">
          <ShieldCheck className="h-4 w-4 text-primary flex-shrink-0 mt-0.5" />
          <div className="text-[11px] text-foreground/90 leading-relaxed">
            <strong className="text-primary">Fundamento jurídico:</strong> O Art. 202, VI do Código Civil prevê que
            "qualquer ato inequívoco, ainda que extrajudicial, que importe reconhecimento do direito pelo devedor"
            interrompe a prescrição. Cada NE emitida pelo DETRAN/AM constitui ato de reconhecimento formal, reiniciando
            o prazo prescricional quinquenal a partir da sua data. Súmula 106/STJ complementa impedindo prescrição
            durante demora imputável ao serviço judiciário ou administrativo.
          </div>
        </div>
      </div>
    </>
  );
}
