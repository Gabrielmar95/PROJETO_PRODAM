import { createContext, useContext, useMemo, useState, useCallback, type ReactNode } from "react";
import type { Fatura } from "@/data/types";
import { parseFaturas } from "@/data/helpers";
import { toast } from "sonner";

export interface FilterState {
  search: string;
  regime: string; // "all" or regime name
  contrato: string;
  ano: string;
  prescricao: string; // VIGENTE / PRESCRITA / all
  procedencia: string; // P1-DOC / P2-PARCIAL / P3-... / all
}

export interface ActiveFilter {
  key: keyof FilterState;
  label: string;
  value: string;
}

interface FilterContextValue {
  filters: FilterState;
  setFilter: <K extends keyof FilterState>(key: K, value: FilterState[K]) => void;
  resetFilters: () => void;
  resetFilter: (key: keyof FilterState) => void;
  applyDrillDown: (key: keyof FilterState, value: string, targetSection?: string) => void;
  allFaturas: Fatura[];
  filteredFaturas: Fatura[];
  activeFilters: ActiveFilter[];
  hasActive: boolean;
  regimes: string[];
  contratos: string[];
  anos: string[];
  prescricoes: string[];
  procedencias: string[];
}

const defaultFilters: FilterState = {
  search: "",
  regime: "all",
  contrato: "all",
  ano: "all",
  prescricao: "all",
  procedencia: "all",
};

const FILTER_LABELS: Record<keyof FilterState, string> = {
  search: "Busca",
  regime: "Regime",
  contrato: "Contrato",
  ano: "Ano",
  prescricao: "Prescrição",
  procedencia: "Procedência",
};

const FilterContext = createContext<FilterContextValue | null>(null);

export function FilterProvider({ children }: { children: ReactNode }) {
  const [filters, setFilters] = useState<FilterState>(defaultFilters);
  const allFaturas = useMemo(() => parseFaturas(), []);

  const setFilter = useCallback(
    <K extends keyof FilterState>(key: K, value: FilterState[K]) => {
      setFilters((prev) => ({ ...prev, [key]: value }));
    },
    []
  );

  const resetFilters = useCallback(() => {
    setFilters(defaultFilters);
    toast.info("Todos os filtros foram limpos");
  }, []);

  const resetFilter = useCallback((key: keyof FilterState) => {
    setFilters((prev) => ({ ...prev, [key]: defaultFilters[key] }));
  }, []);

  /**
   * Drill-down global: ativa um filtro a partir de um clique em qualquer
   * gráfico/tabela. Opcionalmente navega para uma seção-alvo via hash.
   */
  const applyDrillDown = useCallback(
    (key: keyof FilterState, value: string, targetSection?: string) => {
      setFilters((prev) => {
        // Toggle: se já está ativo com esse valor, limpa
        if (prev[key] === value) {
          toast.info(`Filtro "${FILTER_LABELS[key]}" removido`);
          return { ...prev, [key]: defaultFilters[key] };
        }
        toast.success(`Filtrando por ${FILTER_LABELS[key]}: ${value}`);
        return { ...prev, [key]: value };
      });
      if (targetSection) {
        // Adia a navegação para após o setState
        setTimeout(() => {
          window.location.hash = targetSection;
        }, 50);
      }
    },
    []
  );

  const regimes = useMemo(
    () => Array.from(new Set(allFaturas.map((f) => f.regime).filter(Boolean))).sort(),
    [allFaturas]
  );
  const contratos = useMemo(
    () => Array.from(new Set(allFaturas.map((f) => f.contrato).filter(Boolean))).sort(),
    [allFaturas]
  );
  const anos = useMemo(
    () =>
      Array.from(new Set(allFaturas.map((f) => String(f.ano)).filter((a) => a !== "0"))).sort(),
    [allFaturas]
  );
  const prescricoes = useMemo(
    () => Array.from(new Set(allFaturas.map((f) => f.prescricao).filter(Boolean))).sort(),
    [allFaturas]
  );
  const procedencias = useMemo(
    () => Array.from(new Set(allFaturas.map((f) => f.procedencia).filter(Boolean))).sort(),
    [allFaturas]
  );

  const filteredFaturas = useMemo(() => {
    const q = filters.search.trim().toLowerCase();
    return allFaturas.filter((f) => {
      if (filters.regime !== "all" && f.regime !== filters.regime) return false;
      if (filters.contrato !== "all" && f.contrato !== filters.contrato) return false;
      if (filters.ano !== "all" && String(f.ano) !== filters.ano) return false;
      if (filters.prescricao !== "all" && f.prescricao !== filters.prescricao) return false;
      if (filters.procedencia !== "all" && f.procedencia !== filters.procedencia) return false;
      if (q) {
        const hay = `${f.nf} ${f.contrato} ${f.regime} ${f.competencia} ${f.vencimento}`.toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });
  }, [allFaturas, filters]);

  const activeFilters = useMemo<ActiveFilter[]>(() => {
    const out: ActiveFilter[] = [];
    (Object.keys(filters) as (keyof FilterState)[]).forEach((k) => {
      const v = filters[k];
      if (!v) return;
      if (k !== "search" && v === "all") return;
      out.push({ key: k, label: FILTER_LABELS[k], value: v });
    });
    return out;
  }, [filters]);

  const hasActive = activeFilters.length > 0;

  return (
    <FilterContext.Provider
      value={{
        filters,
        setFilter,
        resetFilters,
        resetFilter,
        applyDrillDown,
        allFaturas,
        filteredFaturas,
        activeFilters,
        hasActive,
        regimes,
        contratos,
        anos,
        prescricoes,
        procedencias,
      }}
    >
      {children}
    </FilterContext.Provider>
  );
}

export function useFilters() {
  const ctx = useContext(FilterContext);
  if (!ctx) throw new Error("useFilters deve ser usado dentro de FilterProvider");
  return ctx;
}
