// Todas as 202 Faturas — tabela principal com filtros globais
import { dashboard, fmtBRL } from "@/data/helpers";
import { SectionHeader } from "@/components/ForensicCard";
import { ForensicTable } from "@/components/ForensicTable";
import FilterBar from "@/components/FilterBar";
import { useFilters } from "@/contexts/FilterContext";
import { Badge } from "@/components/KpiCard";
import { badgeTone } from "@/data/helpers";
import { cn } from "@/lib/utils";
import { useMemo, useState } from "react";
import { ChevronDown, ChevronUp, ChevronsUpDown } from "lucide-react";

type SortKey = "idx" | "nf" | "contrato" | "vencimento" | "meses" | "saldoNum" | "c1Num" | "regime";

export default function SectionFaturasTodas() {
  const sec = dashboard.faturas_todas;
  const { filteredFaturas } = useFilters();
  const [sortKey, setSortKey] = useState<SortKey>("c1Num");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  const sorted = useMemo(() => {
    const copy = [...filteredFaturas];
    const dir = sortDir === "asc" ? 1 : -1;
    copy.sort((a, b) => {
      const av = a[sortKey];
      const bv = b[sortKey];
      if (typeof av === "number" && typeof bv === "number") return (av - bv) * dir;
      return String(av).localeCompare(String(bv), "pt-BR") * dir;
    });
    return copy;
  }, [filteredFaturas, sortKey, sortDir]);

  const toggleSort = (k: SortKey) => {
    if (sortKey === k) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else {
      setSortKey(k);
      setSortDir("desc");
    }
  };

  const totalSaldo = sorted.reduce((s, f) => s + f.saldoNum, 0);
  const totalC1 = sorted.reduce((s, f) => s + f.c1Num, 0);

  const Header = ({ k, label, align = "left" }: { k: SortKey; label: string; align?: "left" | "right" }) => (
    <th
      onClick={() => toggleSort(k)}
      className={cn(
        "sticky top-0 z-10 bg-[color:var(--bg-4)] text-primary font-semibold py-2.5 px-3 border-b-2 border-primary/40 text-[10px] uppercase tracking-wider cursor-pointer select-none hover:bg-[color:var(--bg-3)]",
        align === "right" ? "text-right" : "text-left"
      )}
    >
      <span className={cn("inline-flex items-center gap-1", align === "right" && "flex-row-reverse")}>
        {label}
        {sortKey === k ? (
          sortDir === "asc" ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />
        ) : (
          <ChevronsUpDown className="h-3 w-3 opacity-30" />
        )}
      </span>
    </th>
  );

  return (
    <div className="space-y-4">
      <SectionHeader title={sec.title} desc={sec.desc} />
      <FilterBar />

      <div className="forensic-card">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-display text-[15px] font-semibold text-primary">
            Universo Auditado · {sorted.length} faturas
          </h3>
          <div className="text-[10px] font-mono text-muted-foreground">
            Σ Saldo: <span className="text-primary">{fmtBRL(totalSaldo)}</span>
            {" · "}Σ C1: <span className="text-primary">{fmtBRL(totalC1)}</span>
          </div>
        </div>

        <div className="border border-border rounded overflow-auto" style={{ maxHeight: "70vh" }}>
          <table className="w-full text-[11px] border-collapse">
            <thead>
              <tr>
                <Header k="idx" label="#" />
                <Header k="nf" label="NF" />
                <Header k="contrato" label="Contrato" />
                <th className="sticky top-0 z-10 bg-[color:var(--bg-4)] text-primary font-semibold py-2.5 px-3 text-left border-b-2 border-primary/40 text-[10px] uppercase tracking-wider">
                  Comp.
                </th>
                <Header k="vencimento" label="Vencimento" />
                <Header k="meses" label="Meses" align="right" />
                <Header k="saldoNum" label="Saldo" align="right" />
                <Header k="c1Num" label="Valor C1 (SELIC)" align="right" />
                <th className="sticky top-0 z-10 bg-[color:var(--bg-4)] text-primary font-semibold py-2.5 px-3 text-right border-b-2 border-primary/40 text-[10px] uppercase tracking-wider">
                  Fator
                </th>
                <Header k="regime" label="Regime" />
                <th className="sticky top-0 z-10 bg-[color:var(--bg-4)] text-primary font-semibold py-2.5 px-3 text-left border-b-2 border-primary/40 text-[10px] uppercase tracking-wider">
                  Prescrição
                </th>
                <th className="sticky top-0 z-10 bg-[color:var(--bg-4)] text-primary font-semibold py-2.5 px-3 text-left border-b-2 border-primary/40 text-[10px] uppercase tracking-wider">
                  Procedência
                </th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((f, i) => (
                <tr key={f.idx + "-" + i} className="hover:bg-primary/5 transition-colors">
                  <td className="py-1.5 px-3 border-b border-border/40 text-primary font-mono text-[10px]">
                    {f.idx}
                  </td>
                  <td className="py-1.5 px-3 border-b border-border/40 font-mono text-[10px] text-[color:var(--t2)]">
                    {f.nf}
                  </td>
                  <td className="py-1.5 px-3 border-b border-border/40 font-mono text-[10px] text-[color:var(--t2)]">
                    {f.contrato}
                  </td>
                  <td className="py-1.5 px-3 border-b border-border/40 text-[10.5px] text-[color:var(--t2)]">
                    {f.competencia}
                  </td>
                  <td className="py-1.5 px-3 border-b border-border/40 font-mono text-[10px] text-[color:var(--t2)]">
                    {f.vencimento}
                  </td>
                  <td className="py-1.5 px-3 border-b border-border/40 text-right font-mono text-[10.5px] tabular-nums text-[color:var(--t2)]">
                    {f.meses}
                  </td>
                  <td className="py-1.5 px-3 border-b border-border/40 text-right font-mono text-[10.5px] tabular-nums text-[color:var(--t2)]">
                    {f.saldo}
                  </td>
                  <td className="py-1.5 px-3 border-b border-border/40 text-right font-mono text-[10.5px] tabular-nums text-primary font-semibold">
                    {f.c1}
                  </td>
                  <td className="py-1.5 px-3 border-b border-border/40 text-right font-mono text-[10px] text-[color:var(--t3)]">
                    {f.fator}
                  </td>
                  <td className="py-1.5 px-3 border-b border-border/40 text-[10.5px] text-[color:var(--t2)]">
                    {f.regime}
                  </td>
                  <td className="py-1.5 px-3 border-b border-border/40">
                    <Badge tone={badgeTone(f.prescricao)}>{f.prescricao}</Badge>
                  </td>
                  <td className="py-1.5 px-3 border-b border-border/40">
                    <Badge tone={badgeTone(f.procedencia)}>{f.procedencia}</Badge>
                  </td>
                </tr>
              ))}
              {sorted.length === 0 && (
                <tr>
                  <td colSpan={12} className="py-12 text-center text-muted-foreground text-[11px]">
                    Nenhuma fatura corresponde aos filtros aplicados.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
