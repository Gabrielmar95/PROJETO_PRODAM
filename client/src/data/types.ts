// Tipos de domínio — Dashboard DETRAN/AM
// Design: Noturno Forense | Brandão Ozores Advogados

export interface Kpi {
  label: string;
  value: string;
  detail: string;
  big?: boolean;
  green?: boolean;
}

export interface TableData {
  headers: string[];
  rows: string[][];
}

export interface CardData {
  title: string;
  text: string;
}

export interface SectionData {
  title: string;
  desc: string;
  kpis: Kpi[];
  tables: TableData[];
  cards: CardData[];
}

export type Dashboard = Record<string, SectionData>;

export interface Fatura {
  idx: number;
  nf: string;
  contrato: string;
  competencia: string;
  vencimento: string;
  meses: number;
  saldo: string;
  saldoNum: number;
  c1: string;
  c1Num: number;
  fator: string;
  regime: string;
  prescricao: string;
  procedencia: string;
  ano: number;
}

export interface NavItem {
  id: string;
  label: string;
  section: string;
  badge?: string;
}

export const NAV_SECTIONS: { group: string; items: NavItem[] }[] = [
  {
    group: "Painel Executivo",
    items: [
      { id: "painel", label: "Painel Geral", section: "painel", badge: "202" },
      { id: "cenarios", label: "Cenários C1 / C2 / C3", section: "cenarios", badge: "3" },
      { id: "score", label: "Score Forense 12D", section: "score", badge: "A+" },
    ],
  },
  {
    group: "Faturas",
    items: [
      { id: "faturas_todas", label: "Todas as Faturas", section: "faturas_todas", badge: "202" },
      { id: "faturas_contrato", label: "Por Contrato", section: "faturas_contrato", badge: "18" },
      { id: "faturas_regime", label: "Por Regime Jurídico", section: "faturas_regime", badge: "6" },
      { id: "faturas_ano", label: "Por Ano de Vencimento", section: "faturas_ano" },
      { id: "decomposicao", label: "Decomposição Top 10", section: "decomposicao" },
      { id: "faturas_detalhadas", label: "Análise Jurídica (149)", section: "faturas_detalhadas", badge: "149" },
    ],
  },
  {
    group: "Contratos",
    items: [
      { id: "contratos_todos", label: "Todos os Contratos", section: "contratos_todos", badge: "18" },
      { id: "contratos_detalhe", label: "Ficha por Contrato", section: "contratos_detalhe", badge: "18" },
      { id: "cadeia", label: "Cadeia Documental", section: "cadeia", badge: "86" },
    ],
  },
  {
    group: "Auditoria Forense",
    items: [
      { id: "empenhos", label: "Notas de Empenho", section: "empenhos", badge: "481" },
      { id: "cobrancas", label: "Cobranças Emitidas", section: "cobrancas", badge: "113" },
      { id: "marcos", label: "Marcos Interruptivos", section: "marcos", badge: "148" },
      { id: "inventario", label: "Inventário de Documentos", section: "inventario", badge: "100" },
    ],
  },
  {
    group: "Correção Monetária",
    items: [
      { id: "correcao_geral", label: "Metodologia e Regimes", section: "correcao_geral", badge: "6" },
    ],
  },
  {
    group: "Fundamentação Jurídica",
    items: [
      { id: "juridico", label: "Precedentes e Súmulas", section: "juridico", badge: "10" },
      { id: "prescricao", label: "Prescrição", section: "prescricao", badge: "201/202" },
      { id: "rpv", label: "RPV e Precatórios", section: "rpv", badge: "95" },
      { id: "risco", label: "Risco e Flags", section: "risco", badge: "17" },
    ],
  },
  {
    group: "Execução",
    items: [
      { id: "prontuario", label: "Prontuário de Execução", section: "prontuario", badge: "18" },
      { id: "plano_acao", label: "Plano de Ação", section: "plano_acao", badge: "5" },
      { id: "honorarios", label: "Honorários Sucumbenciais", section: "honorarios" },
    ],
  },
  {
    group: "Administração",
    items: [
      { id: "admin", label: "Edição Colaborativa", section: "admin", badge: "🔐" },
    ],
  },
];
