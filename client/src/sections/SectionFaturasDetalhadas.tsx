// SectionFaturasDetalhadas — 149 faturas com análise jurídica profunda
// Por fatura: prescrição, status SPCF, correção, juros, multa, elos da cadeia
import { useMemo } from "react";
import { useAuditoria } from "@/contexts/AuditoriaContext";
import { SectionHeader, ForensicCard } from "@/components/ForensicCard";
import { KpiGrid } from "@/components/KpiCard";
import { ForensicTable } from "@/components/ForensicTable";
import { fmtBRL, parseBRL } from "@/data/helpers";

export default function SectionFaturasDetalhadas() {
  const { faturasDetalhadas } = useAuditoria();

  const totais = useMemo(() => {
    const bruto = faturasDetalhadas.reduce((a, f) => a + parseBRL(f.valorBruto || "0"), 0);
    const atualizado = faturasDetalhadas.reduce((a, f) => a + parseBRL(f.valorAtualizado || "0"), 0);
    const correcao = faturasDetalhadas.reduce((a, f) => a + parseBRL(f.correcaoMonetaria || "0"), 0);
    const juros = faturasDetalhadas.reduce((a, f) => a + parseBRL(f.jurosMora || "0"), 0);
    const multa = faturasDetalhadas.reduce((a, f) => a + parseBRL(f.multa || "0"), 0);
    const vigentes = faturasDetalhadas.filter((f) =>
      (f.statusPrescricao || "").toLowerCase().includes("vigente"),
    ).length;
    return { total: faturasDetalhadas.length, bruto, atualizado, correcao, juros, multa, vigentes };
  }, [faturasDetalhadas]);

  const tableRows = faturasDetalhadas.map((f) => [
    f.nf || "—",
    f.contrato || "—",
    f.competencia || "—",
    f.dataVencimento || "—",
    f.dataPrescricao || "—",
    f.statusPrescricao || "—",
    f.situacaoSpcf || "—",
    f.valorBruto ? fmtBRL(parseBRL(f.valorBruto)) : "—",
    f.valorAtualizado ? fmtBRL(parseBRL(f.valorAtualizado)) : "—",
    f.fatorCorrecao || "—",
    f.cadeiaClasse || "—",
    f.numNesVinculadas ? `${f.numNesVinculadas} NEs` : "—",
  ]);

  return (
    <>
      <SectionHeader
        title="Faturas · Análise Jurídica Profunda"
        desc={`${faturasDetalhadas.length} faturas com metadados jurídicos completos: prescrição, status SPCF, decomposição monetária e elos da cadeia documental`}
      />

      <KpiGrid
        kpis={[
          { label: "Faturas Detalhadas", value: `${totais.total}`, detail: "Com análise completa", big: true },
          { label: "Prescrição Vigente", value: `${totais.vigentes}`, detail: "Juridicamente cobráveis", green: true },
          { label: "Valor Bruto", value: fmtBRL(totais.bruto), detail: "Sem correção" },
          { label: "Valor Atualizado", value: fmtBRL(totais.atualizado), detail: "Com C1 aplicado" },
          { label: "Correção Monetária", value: fmtBRL(totais.correcao), detail: "Diferença bruto → corrigido" },
          { label: "Juros + Multa", value: fmtBRL(totais.juros + totais.multa), detail: "Mora acumulada" },
        ]}
      />

      <ForensicCard title={`Detalhamento (${faturasDetalhadas.length} faturas)`} className="mt-6">
        <ForensicTable
          table={{
            headers: [
              "NF",
              "Contrato",
              "Competência",
              "Vencimento",
              "Prescrição",
              "Status",
              "SPCF",
              "Bruto",
              "Atualizado",
              "Fator",
              "Cadeia",
              "NEs",
            ],
            rows: tableRows,
          }}
          searchable
          showRowIndex
          maxHeight="680px"
        />
      </ForensicCard>
    </>
  );
}
