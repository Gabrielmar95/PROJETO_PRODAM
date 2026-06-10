/**
 * helpers.test.ts — Testes unitários para client/src/data/helpers.ts
 * Cobre parseBRL, fmtBRL, fmtNum, badgeTone, contratoBadgeLabel,
 * cellIsNumeric, isTotalRow, filterTableRows, hydrateDashboard.
 */
import { describe, it, expect } from "vitest";
import {
  parseBRL,
  fmtBRL,
  fmtNum,
  badgeTone,
  contratoBadgeLabel,
  cellIsNumeric,
  isTotalRow,
  filterTableRows,
  hydrateDashboard,
  dashboard,
} from "./helpers";
import type { TableData } from "./types";

// ─── parseBRL ─────────────────────────────────────────────────────────────────
describe("parseBRL", () => {
  it("retorna 0 para null", () => expect(parseBRL(null)).toBe(0));
  it("retorna 0 para undefined", () => expect(parseBRL(undefined)).toBe(0));
  it("retorna 0 para string vazia", () => expect(parseBRL("")).toBe(0));
  it("retorna 0 para NaN", () => expect(parseBRL(NaN)).toBe(0));
  it("retorna o número diretamente para number válido", () => expect(parseBRL(1234.56)).toBe(1234.56));
  it("parseia formato BR com ponto milhar e vírgula decimal", () =>
    expect(parseBRL("1.234.567,89")).toBeCloseTo(1234567.89));
  it("parseia formato com apenas vírgula decimal", () =>
    expect(parseBRL("1234,56")).toBeCloseTo(1234.56));
  it("parseia formato float com ponto decimal (1 ou 2 dígitos após ponto)", () =>
    expect(parseBRL("1234.56")).toBeCloseTo(1234.56));
  it("parseia formato milhar com múltiplos pontos", () =>
    expect(parseBRL("1.234.567")).toBe(1234567));
  it("remove prefixo R$", () =>
    expect(parseBRL("R$ 1.234,56")).toBeCloseTo(1234.56));
  it("retorna 0 para string não numérica", () =>
    expect(parseBRL("abc")).toBe(0));
  it("parseia número inteiro sem separadores", () =>
    expect(parseBRL("500")).toBe(500));
  it("parseia número com ponto como milhar (3 dígitos após ponto)", () =>
    expect(parseBRL("1.234")).toBe(1234));
});

// ─── fmtBRL ───────────────────────────────────────────────────────────────────
describe("fmtBRL", () => {
  it("formata número como moeda BRL", () => {
    const result = fmtBRL(1234.56);
    expect(result).toContain("1.234,56");
  });
  it("formata zero como R$ 0,00", () => {
    const result = fmtBRL(0);
    expect(result).toContain("0,00");
  });
});

// ─── fmtNum ───────────────────────────────────────────────────────────────────
describe("fmtNum", () => {
  it("formata número sem decimais por padrão", () => {
    const result = fmtNum(1234);
    expect(result).toContain("1.234");
  });
  it("formata número com 2 decimais quando digits=2", () => {
    const result = fmtNum(1234.5, 2);
    expect(result).toContain("1.234,50");
  });
  it("formata zero", () => {
    expect(fmtNum(0)).toBe("0");
  });
});

// ─── badgeTone ────────────────────────────────────────────────────────────────
describe("badgeTone", () => {
  it("retorna 'ok' para 'OFICIAL'", () => expect(badgeTone("OFICIAL")).toBe("ok"));
  it("retorna 'ok' para 'oficial' (case insensitive)", () => expect(badgeTone("oficial")).toBe("ok"));
  it("retorna 'warn' para 'pdf_pendente'", () => expect(badgeTone("pdf_pendente")).toBe("warn"));
  it("retorna 'warn' para 'PDF PENDENTE'", () => expect(badgeTone("PDF PENDENTE")).toBe("warn"));
  it("retorna 'purple' para 'sem_contrato'", () => expect(badgeTone("sem_contrato")).toBe("purple"));
  it("retorna 'purple' para 'sem contrato'", () => expect(badgeTone("sem contrato")).toBe("purple"));
  it("retorna 'ok' para texto contendo 'vigente'", () => expect(badgeTone("contrato vigente")).toBe("ok"));
  it("retorna 'ok' para texto contendo 'p1-doc'", () => expect(badgeTone("p1-doc ok")).toBe("ok"));
  it("retorna 'ok' para texto contendo 'aprovad'", () => expect(badgeTone("aprovado")).toBe("ok"));
  it("retorna 'err' para texto contendo 'prescrit'", () => expect(badgeTone("prescrito")).toBe("err"));
  it("retorna 'err' para texto contendo 'pendente'", () => expect(badgeTone("pendente")).toBe("err"));
  it("retorna 'err' para texto contendo 'erro'", () => expect(badgeTone("com erro")).toBe("err"));
  it("retorna 'err' para texto contendo 'flag'", () => expect(badgeTone("flag")).toBe("err"));
  it("retorna 'warn' para texto contendo 'p2-parcial'", () => expect(badgeTone("p2-parcial")).toBe("warn"));
  it("retorna 'warn' para texto contendo 'alerta'", () => expect(badgeTone("alerta")).toBe("warn"));
  it("retorna 'warn' para texto contendo 'atenção'", () => expect(badgeTone("atenção")).toBe("warn"));
  it("retorna 'info' para texto contendo 'p3-'", () => expect(badgeTone("p3-info")).toBe("info"));
  it("retorna 'info' para texto contendo 'info'", () => expect(badgeTone("info")).toBe("info"));
  it("retorna 'purple' para texto contendo 'precatorio'", () => expect(badgeTone("precatorio")).toBe("purple"));
  it("retorna 'purple' para texto contendo 'precatório'", () => expect(badgeTone("precatório")).toBe("purple"));
  it("retorna 'cyan' para texto contendo 'rpv'", () => expect(badgeTone("rpv")).toBe("cyan"));
  it("retorna 'gold' para texto desconhecido", () => expect(badgeTone("desconhecido")).toBe("gold"));
  it("retorna 'gold' para string vazia", () => expect(badgeTone("")).toBe("gold"));
});

// ─── contratoBadgeLabel ───────────────────────────────────────────────────────
describe("contratoBadgeLabel", () => {
  it("retorna 'OFICIAL' para 'OFICIAL'", () => expect(contratoBadgeLabel("OFICIAL")).toBe("OFICIAL"));
  it("retorna 'OFICIAL' para 'oficial' (case insensitive)", () => expect(contratoBadgeLabel("oficial")).toBe("OFICIAL"));
  it("retorna 'PDF pendente' para 'PDF_PENDENTE'", () => expect(contratoBadgeLabel("PDF_PENDENTE")).toBe("PDF pendente"));
  it("retorna 'sem contrato' para 'SEM_CONTRATO'", () => expect(contratoBadgeLabel("SEM_CONTRATO")).toBe("sem contrato"));
  it("retorna o valor original para outros valores", () => expect(contratoBadgeLabel("OUTRO")).toBe("OUTRO"));
  it("retorna string vazia para string vazia", () => expect(contratoBadgeLabel("")).toBe(""));
});

// ─── cellIsNumeric ────────────────────────────────────────────────────────────
describe("cellIsNumeric", () => {
  it("retorna false para string vazia", () => expect(cellIsNumeric("")).toBe(false));
  it("retorna true para número inteiro", () => expect(cellIsNumeric("123")).toBe(true));
  it("retorna true para número com vírgula", () => expect(cellIsNumeric("1.234,56")).toBe(true));
  it("retorna true para valor monetário com R$", () => expect(cellIsNumeric("R$ 1.234,56")).toBe(true));
  it("retorna true para número com sufixo %", () => expect(cellIsNumeric("12,5%")).toBe(true));
  it("retorna true para número com sufixo 'x'", () => expect(cellIsNumeric("2x")).toBe(true));
  it("retorna true para número com sufixo ' meses'", () => expect(cellIsNumeric("12 meses")).toBe(true));
  it("retorna false para texto puro", () => expect(cellIsNumeric("Contrato")).toBe(false));
  it("retorna false para texto misto", () => expect(cellIsNumeric("Contrato 10/2021")).toBe(false));
});

// ─── isTotalRow ───────────────────────────────────────────────────────────────
describe("isTotalRow", () => {
  it("retorna true para primeira célula 'total'", () =>
    expect(isTotalRow(["total", "100", "200"])).toBe(true));
  it("retorna true para primeira célula 'TOTAL' (case insensitive)", () =>
    expect(isTotalRow(["TOTAL", "100"])).toBe(true));
  it("retorna true para primeira célula 'Total Geral'", () =>
    expect(isTotalRow(["Total Geral", "100"])).toBe(true));
  it("retorna false para linha normal", () =>
    expect(isTotalRow(["Contrato 10/2021", "100"])).toBe(false));
  it("retorna false para array vazio", () =>
    expect(isTotalRow([])).toBe(false));
});

// ─── filterTableRows ──────────────────────────────────────────────────────────
describe("filterTableRows", () => {
  const table: TableData = {
    headers: ["NF", "Contrato", "Valor"],
    rows: [
      ["001", "10/2021", "R$ 1.000"],
      ["002", "11/2021", "R$ 2.000"],
      ["003", "10/2021", "R$ 3.000"],
    ],
  };

  it("retorna tabela completa quando query está vazia", () => {
    const result = filterTableRows(table, "");
    expect(result.rows).toHaveLength(3);
  });

  it("retorna tabela completa quando query é apenas espaços", () => {
    const result = filterTableRows(table, "   ");
    expect(result.rows).toHaveLength(3);
  });

  it("filtra linhas que contêm a query (case insensitive)", () => {
    const result = filterTableRows(table, "10/2021");
    expect(result.rows).toHaveLength(2);
  });

  it("retorna array vazio quando nenhuma linha corresponde", () => {
    const result = filterTableRows(table, "99/9999");
    expect(result.rows).toHaveLength(0);
  });

  it("mantém os headers inalterados", () => {
    const result = filterTableRows(table, "001");
    expect(result.headers).toEqual(["NF", "Contrato", "Valor"]);
  });
});

// ─── hydrateDashboard ─────────────────────────────────────────────────────────
describe("hydrateDashboard", () => {
  it("atualiza o singleton dashboard com novos dados", () => {
    const newData = {
      painel: { title: "Painel Teste", desc: "Desc", kpis: [], tables: [], cards: [] },
    } as any;
    hydrateDashboard(newData);
    expect((dashboard as any).painel.title).toBe("Painel Teste");
  });

  it("mantém outras chaves após hidratação parcial", () => {
    const newData = {
      cenarios: { title: "Cenários Teste", desc: "", kpis: [], tables: [], cards: [] },
    } as any;
    hydrateDashboard(newData);
    expect((dashboard as any).cenarios.title).toBe("Cenários Teste");
    // painel ainda existe do teste anterior
    expect((dashboard as any).painel).toBeDefined();
  });
});
