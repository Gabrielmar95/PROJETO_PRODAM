// SectionCobrancas — 113 cobranças emitidas no SPCF
import { useMemo } from "react";
import { useAuditoria } from "@/contexts/AuditoriaContext";
import { SectionHeader, ForensicCard } from "@/components/ForensicCard";
import { KpiGrid } from "@/components/KpiCard";
import { ForensicTable } from "@/components/ForensicTable";
import { ForensicPie } from "@/components/Charts";
import { fmtBRL, parseBRL } from "@/data/helpers";
import { ExternalLink } from "lucide-react";

export default function SectionCobrancas() {
  const { cobrancas } = useAuditoria();

  const totais = useMemo(() => {
    const bruto = cobrancas.reduce((a, c) => a + parseBRL(c.valor || "0"), 0);
    const corrigido = cobrancas.reduce(
      (a, c) => a + parseBRL(c.valorCorrigido || "0"),
      0,
    );
    const vencidas = cobrancas.filter((c) => (c.diasAtraso || 0) > 0).length;
    return { total: cobrancas.length, bruto, corrigido, vencidas };
  }, [cobrancas]);

  const porStatus = useMemo(() => {
    const map = new Map<string, number>();
    cobrancas.forEach((c) => {
      const k = c.status || "Sem status";
      map.set(k, (map.get(k) || 0) + 1);
    });
    return Array.from(map.entries()).map(([name, value]) => ({ name, value }));
  }, [cobrancas]);

  const tableRows = cobrancas.slice(0, 113).map((c) => [
    c.numero || "—",
    c.contrato || "—",
    c.competencia || "—",
    (c.servicos || "").slice(0, 40),
    c.valor ? fmtBRL(parseBRL(c.valor)) : "—",
    c.valorCorrigido ? fmtBRL(parseBRL(c.valorCorrigido)) : "—",
    c.diasAtraso ? `${c.diasAtraso} dias` : "—",
    c.status || "—",
  ]);

  return (
    <>
      <SectionHeader
        title="Cobranças Emitidas · Sistema SPCF"
        desc={`${cobrancas.length} eventos de cobrança formal registrados · base do fato gerador das NEs`}
      />
      <KpiGrid
        kpis={[
          { label: "Cobranças", value: `${totais.total}`, detail: "Emitidas no SPCF", big: true },
          { label: "Valor Bruto", value: fmtBRL(totais.bruto), detail: "Sem correção" },
          { label: "Valor Corrigido", value: fmtBRL(totais.corrigido), detail: "C1 SELIC · data-base 16/04/2026", green: true },
          { label: "Em Atraso", value: `${totais.vencidas}`, detail: "Dias > 0" },
        ]}
      />

      <ForensicCard title="Distribuição por Status" className="mt-6">
        <ForensicPie data={porStatus} height={260} valueFormatter={(v: number) => `${v} cobranças`} />
      </ForensicCard>

      <ForensicCard title={`Detalhamento (${cobrancas.length} cobranças)`} className="mt-6">
        <ForensicTable
          table={{
            headers: ["Número", "Contrato", "Competência", "Serviços", "Valor", "Corrigido", "Atraso", "Status"],
            rows: tableRows,
          }}
          searchable
          showRowIndex
          maxHeight="600px"
        />
      </ForensicCard>

      <div className="mt-4 flex items-center gap-2 text-[10px] text-muted-foreground font-mono">
        <ExternalLink className="h-3 w-3" />
        <span>
          Fonte: Sistema Prodam · SPCF · base auditada em 16/04/2026
        </span>
      </div>
    </>
  );
}
