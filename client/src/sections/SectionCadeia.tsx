// SectionCadeia — Cadeia documental completa por contrato
// NE → NL → NF → Aceite → Recibo (defensabilidade probatória)
import { useMemo } from "react";
import { useAuditoria } from "@/contexts/AuditoriaContext";
import { SectionHeader, ForensicCard } from "@/components/ForensicCard";
import { KpiGrid } from "@/components/KpiCard";
import { ForensicTable } from "@/components/ForensicTable";
import { ForensicPie } from "@/components/Charts";
import { Link2 } from "lucide-react";

export default function SectionCadeia() {
  const { cadeiaContratos } = useAuditoria();

  const totais = useMemo(() => {
    const completa = cadeiaContratos.filter((c) => c.cadeia === "COMPLETA").length;
    const forte = cadeiaContratos.filter((c) => c.cadeia === "FORTE").length;
    const parcial = cadeiaContratos.filter((c) => c.cadeia === "PARCIAL").length;
    const nes = cadeiaContratos.reduce((a, c) => a + (c.nes || 0), 0);
    const nls = cadeiaContratos.reduce((a, c) => a + (c.nls || 0), 0);
    const nfs = cadeiaContratos.reduce((a, c) => a + (c.nfs || 0), 0);
    return { total: cadeiaContratos.length, completa, forte, parcial, nes, nls, nfs };
  }, [cadeiaContratos]);

  const porClasse = useMemo(
    () => [
      { name: "COMPLETA", value: totais.completa },
      { name: "FORTE", value: totais.forte },
      { name: "PARCIAL", value: totais.parcial },
    ],
    [totais],
  );

  const tableRows = cadeiaContratos.map((c) => [
    c.contrato || "—",
    c.ano || "—",
    c.cadeia || "—",
    String(c.nes || 0),
    String(c.nls || 0),
    String(c.nfs || 0),
    String(c.aceites || 0),
    String(c.docs || 0),
    c.primeira || "—",
    c.ultima || "—",
  ]);

  return (
    <>
      <SectionHeader
        title="Cadeia Documental · Defensabilidade Probatória"
        desc="Rastreabilidade NE → NL → NF → Aceite → Recibo por contrato, definindo a força probatória em ação de cobrança"
      />
      <KpiGrid
        kpis={[
          { label: "Cadeias", value: `${totais.total}`, detail: "Contratos/anos auditados", big: true },
          { label: "COMPLETAs", value: `${totais.completa}`, detail: "5 elos presentes", green: true },
          { label: "FORTEs", value: `${totais.forte}`, detail: "4 elos presentes" },
          { label: "PARCIAL", value: `${totais.parcial}`, detail: "≤3 elos" },
        ]}
      />

      <div className="mt-6 grid gap-4 md:grid-cols-3">
        <div className="bg-card border border-border p-4 rounded">
          <div className="text-[9px] uppercase tracking-wider text-muted-foreground font-mono mb-1">Notas de Empenho</div>
          <div className="font-display text-3xl text-primary">{totais.nes}</div>
        </div>
        <div className="bg-card border border-border p-4 rounded">
          <div className="text-[9px] uppercase tracking-wider text-muted-foreground font-mono mb-1">Notas de Liquidação</div>
          <div className="font-display text-3xl text-primary">{totais.nls}</div>
        </div>
        <div className="bg-card border border-border p-4 rounded">
          <div className="text-[9px] uppercase tracking-wider text-muted-foreground font-mono mb-1">Notas Fiscais</div>
          <div className="font-display text-3xl text-primary">{totais.nfs}</div>
        </div>
      </div>

      <ForensicCard title="Classificação da Cadeia" className="mt-6">
        <ForensicPie data={porClasse} height={260} valueFormatter={(v: number) => `${v} cadeias`} />
      </ForensicCard>

      <ForensicCard title={`Matriz por Contrato (${cadeiaContratos.length})`} className="mt-6">
        <ForensicTable
          table={{
            headers: ["Contrato", "Ano", "Cadeia", "NEs", "NLs", "NFs", "Aceites", "Docs", "Primeira", "Última"],
            rows: tableRows,
          }}
          searchable
          showRowIndex
          maxHeight="600px"
        />
      </ForensicCard>

      <div className="mt-4 p-4 border border-primary/30 bg-primary/5 rounded">
        <div className="flex items-start gap-2">
          <Link2 className="h-4 w-4 text-primary flex-shrink-0 mt-0.5" />
          <div className="text-[11px] text-foreground/90 leading-relaxed">
            <strong className="text-primary">Classificação probatória:</strong> <strong>COMPLETA</strong> (NE + NL + NF + Aceite + Recibo) —
            presunção máxima; <strong>FORTE</strong> (4 elos) — presunção relativa robusta; <strong>PARCIAL</strong> (≤3) — exige complementação.
            Art. 62 Lei 4.320/64 e Art. 63 Lei 8.666/93 sustentam a cadeia formal do reconhecimento do débito público.
          </div>
        </div>
      </div>
    </>
  );
}
