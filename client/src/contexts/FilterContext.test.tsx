// @vitest-environment jsdom
import React, { type ReactNode } from "react";
import { describe, it, expect, beforeEach, vi } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { FilterProvider, useFilters } from "./FilterContext";

// Mock do sonner toast (não-essencial para testes lógicos)
vi.mock("sonner", () => ({
  toast: {
    info: vi.fn(),
    success: vi.fn(),
    error: vi.fn(),
    loading: vi.fn(),
  },
}));

// Mock do parseFaturas para evitar dependência de dados reais
vi.mock("@/data/helpers", () => ({
  parseFaturas: () => [
    {
      idx: 1,
      nf: "135059",
      contrato: "22/2014",
      competencia: "08/2022",
      vencimento: "20/09/2022",
      meses: 43,
      saldo: "R$ 100.000,00",
      saldoNum: 100000,
      c1: "R$ 140.000,00",
      c1Num: 140000,
      fator: "1.40",
      regime: "SELIC",
      prescricao: "VIGENTE",
      procedencia: "P1-DOC",
      ano: 2022,
    },
    {
      idx: 2,
      nf: "135060",
      contrato: "10/2021",
      competencia: "09/2023",
      vencimento: "10/10/2023",
      meses: 30,
      saldo: "R$ 50.000,00",
      saldoNum: 50000,
      c1: "R$ 60.000,00",
      c1Num: 60000,
      fator: "1.20",
      regime: "IPCA",
      prescricao: "VIGENTE",
      procedencia: "P2-PARCIAL",
      ano: 2023,
    },
  ],
}));

const wrapper = ({ children }: { children: ReactNode }) => (
  <FilterProvider>{children}</FilterProvider>
);

describe("FilterContext", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("inicia sem filtros ativos", () => {
    const { result } = renderHook(() => useFilters(), { wrapper });
    expect(result.current.hasActive).toBe(false);
    expect(result.current.activeFilters).toHaveLength(0);
    expect(result.current.allFaturas).toHaveLength(2);
    expect(result.current.filteredFaturas).toHaveLength(2);
  });

  it("aplica filtro de regime via setFilter", () => {
    const { result } = renderHook(() => useFilters(), { wrapper });
    act(() => {
      result.current.setFilter("regime", "SELIC");
    });
    expect(result.current.filters.regime).toBe("SELIC");
    expect(result.current.filteredFaturas).toHaveLength(1);
    expect(result.current.filteredFaturas[0].regime).toBe("SELIC");
    expect(result.current.hasActive).toBe(true);
  });

  it("applyDrillDown ativa um filtro", () => {
    const { result } = renderHook(() => useFilters(), { wrapper });
    act(() => {
      result.current.applyDrillDown("regime", "IPCA");
    });
    expect(result.current.filters.regime).toBe("IPCA");
    expect(result.current.filteredFaturas).toHaveLength(1);
    expect(result.current.filteredFaturas[0].regime).toBe("IPCA");
  });

  it("applyDrillDown faz toggle: clicar duas vezes no mesmo valor limpa", () => {
    const { result } = renderHook(() => useFilters(), { wrapper });
    act(() => {
      result.current.applyDrillDown("regime", "SELIC");
    });
    expect(result.current.filters.regime).toBe("SELIC");
    act(() => {
      result.current.applyDrillDown("regime", "SELIC");
    });
    expect(result.current.filters.regime).toBe("all");
    expect(result.current.hasActive).toBe(false);
  });

  it("resetFilters limpa tudo", () => {
    const { result } = renderHook(() => useFilters(), { wrapper });
    act(() => {
      result.current.setFilter("regime", "SELIC");
      result.current.setFilter("ano", "2022");
    });
    expect(result.current.activeFilters).toHaveLength(2);
    act(() => {
      result.current.resetFilters();
    });
    expect(result.current.hasActive).toBe(false);
    expect(result.current.filteredFaturas).toHaveLength(2);
  });

  it("resetFilter limpa apenas um filtro específico", () => {
    const { result } = renderHook(() => useFilters(), { wrapper });
    act(() => {
      result.current.setFilter("regime", "SELIC");
      result.current.setFilter("ano", "2022");
    });
    act(() => {
      result.current.resetFilter("regime");
    });
    expect(result.current.filters.regime).toBe("all");
    expect(result.current.filters.ano).toBe("2022");
    expect(result.current.activeFilters).toHaveLength(1);
  });

  it("combina múltiplos filtros (AND)", () => {
    const { result } = renderHook(() => useFilters(), { wrapper });
    act(() => {
      result.current.setFilter("regime", "SELIC");
      result.current.setFilter("ano", "2023"); // Nenhuma fatura SELIC+2023
    });
    expect(result.current.filteredFaturas).toHaveLength(0);
  });

  it("filtro de busca faz match em nf, contrato e regime", () => {
    const { result } = renderHook(() => useFilters(), { wrapper });
    act(() => {
      result.current.setFilter("search", "22/2014");
    });
    expect(result.current.filteredFaturas).toHaveLength(1);
    expect(result.current.filteredFaturas[0].contrato).toBe("22/2014");
  });
});
