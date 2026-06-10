/**
 * DensityContext — Sprint 2 Estrutural S2
 *
 * Fornece um controle global de densidade visual do dashboard,
 * permitindo três níveis (Compacto / Conforto / Detalhado) e
 * sincronizando o estado com:
 *  1. localStorage (preferência do usuário);
 *  2. atributo data-density no <html> (CSS reage via :root[data-density="…"]).
 *
 * Pontos de atenção:
 *  - A leitura inicial do localStorage é feita apenas no primeiro render
 *    (useState com função inicializadora) para evitar FOUC.
 *  - O atributo é aplicado em useLayoutEffect para garantir que o
 *    primeiro paint já tenha a densidade correta.
 *  - O contexto é intencionalmente mínimo; componentes não precisam
 *    ler o valor — basta consumir as variáveis CSS --d-* via classes
 *    .pad-card / .gap-card / .py-row. Essa divisão mantém React e CSS
 *    desacoplados e permite fácil mudança sem re-render.
 */
import {
  createContext,
  useCallback,
  useContext,
  useLayoutEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

export type Density = "compact" | "comfort" | "detailed";

const STORAGE_KEY = "detran_density_v1";
const DEFAULT_DENSITY: Density = "comfort";

interface DensityContextValue {
  density: Density;
  setDensity: (d: Density) => void;
  cycleDensity: () => void;
}

const DensityContext = createContext<DensityContextValue | undefined>(undefined);

function readInitial(): Density {
  if (typeof window === "undefined") return DEFAULT_DENSITY;
  try {
    const saved = window.localStorage.getItem(STORAGE_KEY);
    if (saved === "compact" || saved === "comfort" || saved === "detailed") {
      return saved;
    }
  } catch {
    // localStorage bloqueado; fallback silencioso
  }
  return DEFAULT_DENSITY;
}

export function DensityProvider({ children }: { children: ReactNode }) {
  const [density, setDensityState] = useState<Density>(readInitial);

  useLayoutEffect(() => {
    if (typeof document === "undefined") return;
    document.documentElement.setAttribute("data-density", density);
    try {
      window.localStorage.setItem(STORAGE_KEY, density);
    } catch {
      // ignore
    }
  }, [density]);

  const setDensity = useCallback((d: Density) => {
    setDensityState(d);
  }, []);

  const cycleDensity = useCallback(() => {
    setDensityState((prev) => {
      if (prev === "compact") return "comfort";
      if (prev === "comfort") return "detailed";
      return "compact";
    });
  }, []);

  const value = useMemo<DensityContextValue>(
    () => ({ density, setDensity, cycleDensity }),
    [density, setDensity, cycleDensity],
  );

  return <DensityContext.Provider value={value}>{children}</DensityContext.Provider>;
}

export function useDensity(): DensityContextValue {
  const ctx = useContext(DensityContext);
  if (!ctx) {
    throw new Error("useDensity must be used within <DensityProvider>");
  }
  return ctx;
}

export const DENSITY_LABEL: Record<Density, string> = {
  compact: "Compacto",
  comfort: "Conforto",
  detailed: "Detalhado",
};

export const DENSITY_DESCRIPTION: Record<Density, string> = {
  compact: "Mais dados visíveis, espaçamento reduzido — ideal para revisão densa.",
  comfort: "Padrão institucional, equilíbrio entre densidade e legibilidade.",
  detailed: "Espaçamento ampliado e fontes maiores — apresentações e audiências.",
};
