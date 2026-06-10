// Ficha detalhada por contrato — 18 contratos com metadados e faturas
import { useState } from "react";
import { dashboard } from "@/data/helpers";
import { SectionHeader, ForensicCard } from "@/components/ForensicCard";
import { ForensicTable } from "@/components/ForensicTable";
import { ChevronDown, ChevronRight, FileText } from "lucide-react";
import { cn } from "@/lib/utils";

const BADGE_LABEL: Record<string, string> = {
  OFICIAL: "OFICIAL",
  PDF_PENDENTE: "PDF pendente",
  SEM_CONTRATO: "sem contrato",
};

function contractBadgeClass(badge?: string): string {
  switch (badge) {
    case "OFICIAL":
      return "bg-[color:var(--ok-15)] text-[color:var(--ok)] border-[color:var(--ok-40)]";
    case "PDF_PENDENTE":
      return "bg-[color:var(--warn-15)] text-[color:var(--warn)] border-[color:var(--warn-40)]";
    case "SEM_CONTRATO":
      return "bg-[color:var(--crit-15)] text-[color:var(--crit)] border-[color:var(--crit-40)]";
    default:
      return "bg-muted/40 text-muted-foreground border-border";
  }
}

export default function SectionContratosDetalhe() {
  const sec = dashboard.contratos_detalhe;
  const [open, setOpen] = useState<number | null>(0);

  return (
    <div className="space-y-4">
      <SectionHeader title={sec.title} desc={sec.desc} />

      <div className="space-y-2">
        {sec.cards.map((c, i) => {
          const metaTable = sec.tables[i * 2];
          const faturasTable = sec.tables[i * 2 + 1];
          const isOpen = open === i;
          return (
            <div
              key={i}
              className={cn(
                "forensic-card !p-0 overflow-hidden transition-all",
                isOpen && "highlight"
              )}
            >
              <button
                onClick={() => setOpen(isOpen ? null : i)}
                className="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-primary/5 transition-colors"
              >
                {isOpen ? (
                  <ChevronDown className="h-4 w-4 text-primary shrink-0" />
                ) : (
                  <ChevronRight className="h-4 w-4 text-primary shrink-0" />
                )}
                <FileText className="h-4 w-4 text-primary/70 shrink-0" />
                <span className="font-display text-[14px] font-semibold text-primary flex-1">
                  {c.title}
                </span>
                {(c as any).badge && (
                  <span
                    className={cn(
                      "px-2 py-0.5 rounded-full text-[9px] font-mono font-bold border tracking-wider uppercase shrink-0",
                      contractBadgeClass((c as any).badge)
                    )}
                  >
                    {BADGE_LABEL[(c as any).badge] ?? (c as any).badge}
                  </span>
                )}
                {faturasTable && (
                  <span className="text-[10px] font-mono text-muted-foreground shrink-0">
                    {faturasTable.rows.filter((r) => !r[0].toLowerCase().startsWith("total")).length} NFs
                  </span>
                )}
              </button>

              {isOpen && (
                <div className="px-4 pb-4 space-y-3 border-t border-border/40">
                  {metaTable && metaTable.rows.length > 0 && (
                    <div className="pt-3">
                      <div className="text-[10px] uppercase tracking-wider text-muted-foreground font-semibold mb-2">
                        Metadados do Contrato
                      </div>
                      <dl className="grid grid-cols-1 md:grid-cols-2 gap-x-4 gap-y-1 text-[11px]">
                        {metaTable.rows.map((row, ri) => (
                          <div key={ri} className="flex gap-2 py-1 border-b border-border/30 last:border-0">
                            <dt className="text-[color:var(--t3)] font-semibold min-w-[110px]">{row[0]}</dt>
                            <dd className="text-[color:var(--t1)] flex-1">{row[1]}</dd>
                          </div>
                        ))}
                      </dl>
                    </div>
                  )}

                  {faturasTable && faturasTable.rows.length > 0 && (
                    <div>
                      <div className="text-[10px] uppercase tracking-wider text-muted-foreground font-semibold mb-2">
                        Faturas deste Contrato
                      </div>
                      <ForensicTable
                        table={faturasTable}
                        maxHeight="500px"
                        searchable={faturasTable.rows.length > 8}
                        searchPlaceholder="Buscar NF, competência..."
                      />
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
