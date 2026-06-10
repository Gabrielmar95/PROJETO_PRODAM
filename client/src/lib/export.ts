// Exportação CSV simples — Dashboard DETRAN/AM
import type { Fatura, TableData } from "@/data/types";

export function downloadCSV(filename: string, rows: (string | number)[][]) {
  const csv = rows
    .map((r) =>
      r
        .map((c) => {
          const s = String(c ?? "");
          if (s.includes(";") || s.includes('"') || s.includes("\n")) {
            return `"${s.replace(/"/g, '""')}"`;
          }
          return s;
        })
        .join(";")
    )
    .join("\n");

  const blob = new Blob(["\uFEFF" + csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export function exportFaturas(faturas: Fatura[], suffix = "") {
  const rows: (string | number)[][] = [
    [
      "#",
      "NF",
      "Contrato",
      "Competência",
      "Vencimento",
      "Meses",
      "Saldo (R$)",
      "Valor C1 (R$)",
      "Fator",
      "Regime",
      "Prescrição",
      "Procedência",
    ],
    ...faturas.map((f) => [
      f.idx,
      f.nf,
      f.contrato,
      f.competencia,
      f.vencimento,
      f.meses,
      f.saldoNum.toFixed(2).replace(".", ","),
      f.c1Num.toFixed(2).replace(".", ","),
      f.fator,
      f.regime,
      f.prescricao,
      f.procedencia,
    ]),
  ];
  const fname = `detran_faturas${suffix ? "_" + suffix : ""}_${new Date()
    .toISOString()
    .slice(0, 10)}.csv`;
  downloadCSV(fname, rows);
}

export function exportTable(table: TableData, name: string) {
  const rows: (string | number)[][] = [table.headers, ...table.rows];
  const fname = `detran_${name}_${new Date().toISOString().slice(0, 10)}.csv`;
  downloadCSV(fname, rows);
}
