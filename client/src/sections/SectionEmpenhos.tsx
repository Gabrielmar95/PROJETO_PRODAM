// SectionEmpenhos — 481 Notas de Empenho (R$ 255,4M)
// Fonte: prodam.db + AFI/SPCF · detalhamento por fonte, órgão e contrato
import { useMemo, useState } from "react";
import { useAuditoria } from "@/contexts/AuditoriaContext";
import { SectionHeader, ForensicCard } from "@/components/ForensicCard";
import { KpiGrid } from "@/components/KpiCard";
import { ForensicTable } from "@/components/ForensicTable";
import { ForensicBar, ForensicPie } from "@/components/Charts";
import { fmtBRL, fmtNum, parseBRL } from "@/data/helpers";

export default function SectionEmpenhos() {
  const { notasEmpenho } = useAuditoria();
  const [contratoFiltro, setContratoFiltro] = useState<string>("__all__");

  const nes = useMemo(() => {
    if (contratoFiltro === "__all__") return notasEmpenho;
    return notasEmpenho.filter((n) => n.contrato === contratoFiltro);
  }, [notasEmpenho, contratoFiltro]);

  const totais = useMemo(() => {
    const valores = nes.map((n) => parseBRL(n.valor || "0"));
    const soma = valores.reduce((a, b) => a + b, 0);
    const fontes = new Set(nes.map((n) => n.fonteAfi).filter(Boolean));
    const orgaos = new Set(nes.map((n) => n.orgaoAfi).filter(Boolean));
    return { soma, fontes: fontes.size, orgaos: orgaos.size, total: nes.length };
  }, [nes]);

  const porAno = useMemo(() => {
    const map = new Map<string, number>();
    nes.forEach((n) => {
      const emissao = n.dataEmissao || "";
      const ano = emissao.includes("/")
        ? emissao.split("/").pop() || "?"
        : "?";
      map.set(ano, (map.get(ano) || 0) + parseBRL(n.valor || "0"));
    });
    return Array.from(map.entries())
      .filter(([k]) => k !== "?")
      .sort((a, b) => a[0].localeCompare(b[0]))
      .map(([name, value]) => ({ name, value }));
  }, [nes]);

  const porContrato = useMemo(() => {
    const map = new Map<string, number>();
    notasEmpenho.forEach((n) => {
      const k = n.contrato || "Não informado";
      map.set(k, (map.get(k) || 0) + parseBRL(n.valor || "0"));
    });
    return Array.from(map.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)
      .map(([name, value]) => ({ name, value }));
  }, [notasEmpenho]);

  const contratosLista = useMemo(() => {
    const set = new Set(notasEmpenho.map((n) => n.contrato).filter(Boolean));
    return Array.from(set).sort();
  }, [notasEmpenho]);

  const tableData = useMemo(
    () => ({
      headers: ["NE", "Contrato", "Valor", "Fonte AFI", "Órgão", "Emissão", "Descrição"],
      rows: nes.slice(0, 200).map((n) => [
        n.numero || "—",
        n.contrato || "—",
        n.valor ? fmtBRL(parseBRL(n.valor)) : "—",
        n.fonteAfi || "—",
        n.orgaoAfi || "—",
        n.dataEmissao || "—",
        (n.descricao || "").slice(0, 60),
      ]),
    }),
    [nes],
  );

  return (
    <>
      <SectionHeader
        title="Notas de Empenho · Auditoria AFI/SPCF"
        desc={`${notasEmpenho.length} NEs extraídas do sistema Prodam · corresponde às liquidações formais do DETRAN-AM`}
      />

      <KpiGrid
        kpis={[
          {
            label: "Total de NEs",
            value: fmtNum(totais.total),
            detail: "Notas de empenho auditadas",
            big: true,
          },
          {
            label: "Valor Global",
            value: fmtBRL(totais.soma),
            detail: "Soma consolidada",
            green: true,
          },
          {
            label: "Fontes AFI",
            value: `${totais.fontes}`,
            detail: "Códigos de fonte distintos",
          },
          {
            label: "Órgãos AFI",
            value: `${totais.orgaos}`,
            detail: "Órgãos executores",
          },
        ]}
      />

      <div className="mt-6 flex items-center gap-3">
        <label className="text-[10px] uppercase tracking-wider text-muted-foreground font-mono">
          Contrato:
        </label>
        <select
          value={contratoFiltro}
          onChange={(e) => setContratoFiltro(e.target.value)}
          className="bg-background border border-border px-3 py-1.5 text-[11px] rounded font-mono text-foreground"
        >
          <option value="__all__">Todos ({notasEmpenho.length})</option>
          {contratosLista.map((c) => (
            <option key={c as string} value={c as string}>
              {c}
            </option>
          ))}
        </select>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-2">
        <ForensicCard title="Valor Empenhado por Ano de Emissão">
          <ForensicBar
            data={porAno}
            height={280}
            valueFormatter={(v: number) =>
              v >= 1_000_000
                ? `R$ ${(v / 1_000_000).toFixed(1)}M`
                : `R$ ${(v / 1000).toFixed(0)}k`
            }
          />
        </ForensicCard>
        <ForensicCard title="Valor por Contrato (Top 10)">
          <ForensicPie data={porContrato} height={280} valueFormatter={(v: number) => fmtBRL(v)} />
        </ForensicCard>
      </div>

      <ForensicCard title="Detalhamento (primeiras 200 NEs)" className="mt-6">
        <ForensicTable table={tableData} searchable showRowIndex maxHeight="600px" />
      </ForensicCard>
    </>
  );
}
