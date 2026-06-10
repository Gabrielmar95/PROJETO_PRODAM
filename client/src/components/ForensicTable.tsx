// Tabela forense — Noturno Forense
// Suporta ordenação, busca inline, highlight de linha TOTAL, badges automáticos.

import { useMemo, useState, Fragment } from "react";
import { ChevronDown, ChevronUp, ChevronsUpDown, Search, ChevronRight } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Badge } from "./KpiCard";
import { cn } from "@/lib/utils";
import { badgeTone, isTotalRow, parseBRL, contratoBadgeLabel } from "@/data/helpers";
import type { TableData } from "@/data/types";

interface Props {
  table: TableData;
  searchable?: boolean;
  searchPlaceholder?: string;
  maxHeight?: string;
  compact?: boolean;
  title?: string;
  showRowIndex?: boolean;
  // columns that contain status/badge values (by index); if not passed, auto-detected for common patterns
  badgeCols?: number[];
  // se passado, exibe somente esses índices de coluna na visualização principal;
  // demais colunas vão para uma linha de detalhe expandível (acordão)
  priorityCols?: number[];
}

const BADGE_PATTERNS = /VIGENTE|PRESCRIT|P1-DOC|P2-PARCIAL|P3-|RPV|PRECAT|ALERTA|APROVAD|PENDENTE|FLAG|OK|ERRO|OFICIAL|PDF_PENDENTE|SEM_CONTRATO/i;

function isNumericCell(v: string): boolean {
  if (!v) return false;
  return /^(R\$\s?)?-?[\d.,]+(x| %| meses)?$/.test(v.trim()) || /^-?\d+([.,]\d+)?\s?%$/.test(v.trim());
}

export function ForensicTable({
  table,
  searchable = false,
  searchPlaceholder = "Buscar nesta tabela...",
  maxHeight = "600px",
  compact = false,
  title,
  showRowIndex = false,
  badgeCols,
  priorityCols,
}: Props) {
  const [query, setQuery] = useState("");
  const [sortCol, setSortCol] = useState<number | null>(null);
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set());
  const hasPriority = !!priorityCols && priorityCols.length > 0;
  const detailColIdx = useMemo(() => {
    if (!hasPriority) return [] as number[];
    return table.headers.map((_, i) => i).filter((i) => !priorityCols!.includes(i));
  }, [hasPriority, priorityCols, table.headers]);
  const visibleHeaders = hasPriority
    ? priorityCols!.map((i) => ({ idx: i, label: table.headers[i] || "" }))
    : table.headers.map((h, i) => ({ idx: i, label: h }));

  const detectedBadgeCols = useMemo(() => {
    if (badgeCols) return badgeCols;
    if (!table.rows.length) return [];
    const out: number[] = [];
    const firstDataRow = table.rows.find((r) => !isTotalRow(r)) || table.rows[0];
    firstDataRow.forEach((c, i) => {
      if (BADGE_PATTERNS.test(c)) out.push(i);
    });
    return out;
  }, [badgeCols, table.rows]);

  const filtered = useMemo(() => {
    if (!query.trim()) return table.rows;
    const q = query.toLowerCase();
    return table.rows.filter((r) => r.some((c) => c.toLowerCase().includes(q)));
  }, [query, table.rows]);

  const sorted = useMemo(() => {
    if (sortCol === null) return filtered;
    const totals = filtered.filter(isTotalRow);
    const data = filtered.filter((r) => !isTotalRow(r));
    const dir = sortDir === "asc" ? 1 : -1;
    const copy = [...data].sort((a, b) => {
      const av = a[sortCol] || "";
      const bv = b[sortCol] || "";
      if (isNumericCell(av) && isNumericCell(bv)) {
        return (parseBRL(av) - parseBRL(bv)) * dir;
      }
      return av.localeCompare(bv, "pt-BR") * dir;
    });
    return [...copy, ...totals];
  }, [filtered, sortCol, sortDir]);

  const handleSort = (i: number) => {
    if (sortCol === i) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortCol(i);
      setSortDir("desc");
    }
  };

  return (
    <div className="space-y-2">
      {(title || searchable) && (
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-2">
          {title && (
            <h4 className="font-display text-[14px] font-semibold text-primary">
              {title}
            </h4>
          )}
          {searchable && (
            <div className="relative md:w-72">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
              <Input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder={searchPlaceholder}
                className="pl-9 h-8 text-[11px] bg-background/60 border-border focus-visible:border-primary focus-visible:ring-0"
              />
            </div>
          )}
        </div>
      )}

      <div
        className="border border-border rounded overflow-auto scroll-shadows-x"
        style={{ maxHeight }}
      >
        <table className="w-full text-[11px] border-collapse">
          {table.headers.length > 0 && (
            <thead>
              <tr>
                {hasPriority && (
                  <th className="sticky top-0 z-10 bg-[color:var(--bg-4)] py-2.5 px-2 border-b-2 border-primary/40 w-7" />
                )}
                {showRowIndex && (
                  <th className="sticky top-0 z-10 bg-[color:var(--bg-4)] text-primary font-semibold py-2.5 px-3 text-left border-b-2 border-primary/40 text-[10px] uppercase tracking-wider">
                    #
                  </th>
                )}
                {visibleHeaders.map(({ idx, label }) => (
                  <th
                    key={idx}
                    onClick={() => handleSort(showRowIndex ? idx + 1 : idx)}
                    className="sticky top-0 z-10 bg-[color:var(--bg-4)] text-primary font-semibold py-2.5 px-3 text-left border-b-2 border-primary/40 text-[10px] uppercase tracking-wider cursor-pointer select-none hover:bg-[color:var(--bg-3)]"
                  >
                    <span className="inline-flex items-center gap-1">
                      {label}
                      {(() => {
                        const targetCol = showRowIndex ? idx + 1 : idx;
                        if (sortCol === targetCol) {
                          return sortDir === "asc" ? (
                            <ChevronUp className="h-3 w-3" />
                          ) : (
                            <ChevronDown className="h-3 w-3" />
                          );
                        }
                        return <ChevronsUpDown className="h-3 w-3 opacity-30" />;
                      })()}
                    </span>
                  </th>
                ))}
              </tr>
            </thead>
          )}
          <tbody>
            {sorted.map((row, ri) => {
              const isTotal = isTotalRow(row);
              const expanded = expandedRows.has(ri);
              const renderCells = hasPriority ? priorityCols! : row.map((_, i) => i);
              const totalSpan = renderCells.length + (showRowIndex ? 1 : 0) + (hasPriority ? 1 : 0);
              return (
                <Fragment key={ri}>
                  <tr
                    className={cn(
                      "transition-colors",
                      isTotal
                        ? "bg-[color:var(--bg-4)] font-semibold"
                        : "hover:bg-primary/5",
                      hasPriority && !isTotal && "cursor-pointer"
                    )}
                    onClick={() => {
                      if (!hasPriority || isTotal) return;
                      setExpandedRows((prev) => {
                        const next = new Set(prev);
                        if (next.has(ri)) next.delete(ri);
                        else next.add(ri);
                        return next;
                      });
                    }}
                  >
                    {hasPriority && (
                      <td className="py-2 pl-2 pr-1 border-b border-border/40 text-[color:var(--t3)] w-7">
                        {!isTotal && (
                          <ChevronRight
                            className={cn(
                              "h-3.5 w-3.5 transition-transform",
                              expanded && "rotate-90"
                            )}
                          />
                        )}
                      </td>
                    )}
                    {showRowIndex && (
                      <td className="py-2 px-3 border-b border-border/40 text-primary font-mono text-[10px]">
                        {ri + 1}
                      </td>
                    )}
                    {renderCells.map((ci) => {
                      const cell = row[ci] || "";
                      const isBadge = detectedBadgeCols.includes(ci);
                      const isNum = isNumericCell(cell) && !isBadge;
                      return (
                        <td
                          key={ci}
                          className={cn(
                            "py-2 px-3 border-b border-border/40",
                            compact && "py-1.5",
                            isNum && "text-right font-mono text-[10.5px] tabular-nums",
                            isTotal && isNum && "text-primary",
                            isTotal && ci === 0 && "text-primary",
                            !isBadge && !isNum && "text-[color:var(--t2)]"
                          )}
                        >
                          {isBadge && cell ? (
                            <Badge tone={badgeTone(cell)}>{contratoBadgeLabel(cell)}</Badge>
                          ) : (
                            cell || <span className="text-[color:var(--t4)]">—</span>
                          )}
                        </td>
                      );
                    })}
                  </tr>
                  {hasPriority && expanded && !isTotal && detailColIdx.length > 0 && (
                    <tr className="bg-[color:var(--bg-2)]/40">
                      <td colSpan={totalSpan} className="px-4 py-3 border-b border-primary/20">
                        <dl className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-x-6 gap-y-2 text-[10.5px]">
                          {detailColIdx.map((ci) => (
                            <div key={ci} className="flex flex-col">
                              <dt className="small-caps text-[9.5px] text-[color:var(--t3)] font-semibold mb-0.5">
                                {table.headers[ci]}
                              </dt>
                              <dd className="text-[color:var(--t1)] font-mono tabular-nums">
                                {row[ci] || <span className="text-[color:var(--t4)]">—</span>}
                              </dd>
                            </div>
                          ))}
                        </dl>
                      </td>
                    </tr>
                  )}
                </Fragment>
              );
            })}
            {sorted.length === 0 && (
              <tr>
                <td
                  colSpan={(visibleHeaders.length || 1) + (showRowIndex ? 1 : 0) + (hasPriority ? 1 : 0)}
                  className="py-8 text-center text-muted-foreground text-[11px]"
                >
                  Nenhum registro encontrado.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {searchable && query && (
        <p className="text-[10px] text-muted-foreground font-mono">
          {sorted.length} de {table.rows.length} registros
        </p>
      )}
    </div>
  );
}
