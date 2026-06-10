// SectionInventario — 100 documentos inventariados com OCR e tipologia
import { useMemo } from "react";
import { useAuditoria } from "@/contexts/AuditoriaContext";
import { SectionHeader, ForensicCard } from "@/components/ForensicCard";
import { KpiGrid } from "@/components/KpiCard";
import { ForensicTable } from "@/components/ForensicTable";
import { ForensicPie } from "@/components/Charts";

export default function SectionInventario() {
  const { inventarioDocs } = useAuditoria();

  const totais = useMemo(() => {
    const mb = inventarioDocs.reduce(
      (a, d) => a + parseFloat(d.tamanhoMb || "0"),
      0,
    );
    const chars = inventarioDocs.reduce((a, d) => a + (d.chars || 0), 0);
    const precisouOcr = inventarioDocs.filter((d) => d.precisouOcr === "SIM").length;
    return { total: inventarioDocs.length, mb, chars, precisouOcr };
  }, [inventarioDocs]);

  const porTipo = useMemo(() => {
    const map = new Map<string, number>();
    inventarioDocs.forEach((d) => {
      const k = d.tipoNovo || "Indefinido";
      map.set(k, (map.get(k) || 0) + 1);
    });
    return Array.from(map.entries())
      .sort((a, b) => b[1] - a[1])
      .map(([name, value]) => ({ name, value }));
  }, [inventarioDocs]);

  const tableRows = inventarioDocs.map((d) => [
    (d.arquivo || "—").split("/").pop() || d.arquivo || "—",
    d.tipoNovo || "—",
    d.tamanhoMb ? `${parseFloat(d.tamanhoMb).toFixed(2)} MB` : "—",
    d.chars ? d.chars.toLocaleString("pt-BR") : "—",
    d.precisouOcr || "—",
    d.qualidadeOcr || "—",
    d.nes || "—",
    d.nls || "—",
    d.nfs || "—",
  ]);

  return (
    <>
      <SectionHeader
        title="Inventário de Documentos · OCR + Tipologia"
        desc={`${inventarioDocs.length} documentos auditados do pendrive oficial, classificados e indexados`}
      />
      <KpiGrid
        kpis={[
          { label: "Documentos", value: `${totais.total}`, detail: "Arquivos inventariados", big: true },
          { label: "Volume Total", value: `${totais.mb.toFixed(1)} MB`, detail: "Tamanho consolidado" },
          { label: "Texto Extraído", value: `${(totais.chars / 1e6).toFixed(1)}M`, detail: "Caracteres via OCR+PDF" },
          { label: "OCR Aplicado", value: `${totais.precisouOcr}`, detail: "PDFs sem camada de texto" },
        ]}
      />

      <ForensicCard title="Distribuição por Tipo de Documento" className="mt-6">
        <ForensicPie data={porTipo} height={300} valueFormatter={(v: number) => `${v} docs`} />
      </ForensicCard>

      <ForensicCard title={`Inventário Completo (${inventarioDocs.length})`} className="mt-6">
        <ForensicTable
          table={{
            headers: ["Arquivo", "Tipo", "Tamanho", "Chars", "OCR?", "Qualidade", "NEs", "NLs", "NFs"],
            rows: tableRows,
          }}
          searchable
          showRowIndex
          maxHeight="600px"
        />
      </ForensicCard>
    </>
  );
}
