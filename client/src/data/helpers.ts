import type { Fatura, TableData, Dashboard } from "./types";

// Holder mutável: será preenchido pelo DashboardProvider assim que o fetch tRPC
// retornar. Antes disso, é um shell vazio com shape compatível.
// O Provider garante que nenhum componente é montado antes de `dashboard` estar
// preenchido (bloqueia com loading screen).
const emptySection = {
  title: "",
  desc: "",
  kpis: [],
  tables: [],
  cards: [],
};

const defaultDashboard: Dashboard = {
  painel: { ...emptySection },
  cenarios: { ...emptySection },
  faturas_todas: { ...emptySection },
  faturas_contrato: { ...emptySection },
  faturas_regime: { ...emptySection },
  faturas_ano: { ...emptySection },
  decomposicao: { ...emptySection },
  contratos_todos: { ...emptySection },
  contratos_detalhe: { ...emptySection },
  correcao_geral: { ...emptySection },
  juridico: { ...emptySection },
  prescricao: { ...emptySection },
  rpv: { ...emptySection },
  risco: { ...emptySection },
  honorarios: { ...emptySection },
  prontuario: { ...emptySection },
} as unknown as Dashboard;

/** Singleton mutável referenciado pelas seções. */
export const dashboard: Dashboard = defaultDashboard;

/** Chamado pelo Provider para hidratar o dashboard com dados do backend. */
export function hydrateDashboard(data: Dashboard) {
  Object.assign(dashboard, data);
}

// ============================================================================
// HELPERS — parsing/formatação BR
// ============================================================================
export function parseBRL(s: string | number | null | undefined): number {
  if (s === null || s === undefined) return 0;
  if (typeof s === "number") return isNaN(s) ? 0 : s;
  const raw = String(s).trim();
  if (!raw) return 0;
  // Remove R$, espaços e caracteres não numéricos exceto , . -
  const stripped = raw.replace(/R\$\s?/g, "").replace(/[^\d.,-]/g, "");
  const hasComma = stripped.includes(",");
  const hasDot = stripped.includes(".");
  let clean: string;
  if (hasComma && hasDot) {
    // Formato BR: "1.234.567,89" → pontos são milhar, vírgula decimal
    clean = stripped.replace(/\./g, "").replace(/,/g, ".");
  } else if (hasComma) {
    // Só vírgula → decimal BR: "1234,56"
    clean = stripped.replace(/,/g, ".");
  } else if (hasDot) {
    // Só ponto: decidir entre float ("1234.56") e milhar ("1.234")
    // Se o último bloco após o último ponto tem 1-2 dígitos → decimal float
    const lastDot = stripped.lastIndexOf(".");
    const after = stripped.slice(lastDot + 1);
    const dotCount = (stripped.match(/\./g) || []).length;
    if (dotCount === 1 && after.length <= 2) {
      // Float decimal: "1234.5" ou "1234.56" → mantém
      clean = stripped;
    } else {
      // Milhares: "1.234.567" → remove pontos
      clean = stripped.replace(/\./g, "");
    }
  } else {
    clean = stripped;
  }
  const n = parseFloat(clean);
  return isNaN(n) ? 0 : n;
}

export function fmtBRL(n: number): string {
  return n.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

export function fmtNum(n: number, digits = 0): string {
  return n.toLocaleString("pt-BR", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

export function parseFaturas(): Fatura[] {
  const tbl = dashboard.faturas_todas?.tables?.[0];
  if (!tbl) return [];
  return tbl.rows.map((r) => {
    const [
      idx,
      nf,
      contrato,
      competencia,
      vencimento,
      meses,
      saldo,
      c1,
      fator,
      regime,
      prescricao,
      procedencia,
    ] = r;
    const ano = vencimento?.includes("/")
      ? parseInt(vencimento.split("/").pop() || "0", 10)
      : 0;
    return {
      idx: parseInt(idx, 10) || 0,
      nf,
      contrato,
      competencia,
      vencimento,
      meses: parseInt(meses, 10) || 0,
      saldo,
      saldoNum: parseBRL(saldo),
      c1,
      c1Num: parseBRL(c1),
      fator,
      regime,
      prescricao,
      procedencia,
      ano,
    };
  });
}

export function badgeTone(txt: string): string {
  const t = (txt || "").toLowerCase();
  // Badges de classificação de contrato (Seed v3)
  if (t === "oficial") return "ok";
  if (t === "pdf_pendente" || t === "pdf pendente") return "warn";
  if (t === "sem_contrato" || t === "sem contrato") return "purple";
  if (
    t.includes("vigente") ||
    t.includes("p1-doc") ||
    t.includes("ok") ||
    t.includes("aprovad")
  )
    return "ok";
  if (
    t.includes("prescrit") ||
    t.includes("pendente") ||
    t.includes("erro") ||
    t.includes("flag")
  )
    return "err";
  if (
    t.includes("p2-parcial") ||
    t.includes("alerta") ||
    t.includes("atencao") ||
    t.includes("atenção")
  )
    return "warn";
  if (t.includes("p3-") || t.includes("info")) return "info";
  if (t.includes("precatorio") || t.includes("precatório")) return "purple";
  if (t.includes("rpv")) return "cyan";
  return "gold";
}

/** Rotula badge de contrato para exibição (OFICIAL → OFICIAL, PDF_PENDENTE → PDF pendente, SEM_CONTRATO → sem contrato). */
export function contratoBadgeLabel(raw: string): string {
  const t = (raw || "").toUpperCase();
  if (t === "OFICIAL") return "OFICIAL";
  if (t === "PDF_PENDENTE") return "PDF pendente";
  if (t === "SEM_CONTRATO") return "sem contrato";
  return raw;
}

export function cellIsNumeric(s: string): boolean {
  if (!s) return false;
  return (
    /^(R\$\s?)?[\d.,]+(x| %| meses)?$/i.test(s.trim()) ||
    /^[-+]?\d+([.,]\d+)?%?$/.test(s.trim())
  );
}

export function isTotalRow(row: string[]): boolean {
  const first = (row[0] || "").toLowerCase();
  return first === "total" || first.startsWith("total");
}

export function filterTableRows(table: TableData, query: string): TableData {
  if (!query.trim()) return table;
  const q = query.toLowerCase();
  return {
    headers: table.headers,
    rows: table.rows.filter((row) =>
      row.some((c) => c.toLowerCase().includes(q)),
    ),
  };
}
