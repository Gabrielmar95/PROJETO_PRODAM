/**
 * DossierThemeContext — Sprint 3 Aspiracional A1
 *
 * Três modos institucionais para o Dossiê DETRAN/AM, independentes do
 * ThemeContext shadcn (light/dark):
 *   - "dossier"  : noturno institucional (padrão; gold sobre preto)
 *   - "day"      : editorial claro para leitura prolongada ou apresentações
 *   - "print"    : preview em tela do dossiê impresso (papel off-white)
 *
 * Preferência salva em localStorage; respeita prefers-color-scheme no primeiro mount.
 * Aplica atributo data-dossier-theme no <html> via useLayoutEffect para evitar FOUC.
 */
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useLayoutEffect,
  useState,
  type ReactNode,
} from "react";

export type DossierTheme = "dossier" | "day" | "print";
export const DOSSIER_THEMES: DossierTheme[] = ["dossier", "day", "print"];
const STORAGE_KEY = "detran_dossier_theme_v1";

interface Ctx {
  theme: DossierTheme;
  setTheme: (t: DossierTheme) => void;
  cycleTheme: () => void;
}

const DossierThemeCtx = createContext<Ctx | null>(null);

function detectInitial(): DossierTheme {
  if (typeof window === "undefined") return "dossier";
  try {
    const saved = window.localStorage.getItem(STORAGE_KEY);
    if (saved && DOSSIER_THEMES.includes(saved as DossierTheme)) return saved as DossierTheme;
  } catch {
    // localStorage indisponível
  }
  if (window.matchMedia?.("(prefers-color-scheme: light)").matches) return "day";
  return "dossier";
}

export function DossierThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<DossierTheme>(() => detectInitial());

  useLayoutEffect(() => {
    if (typeof document === "undefined") return;
    document.documentElement.setAttribute("data-dossier-theme", theme);
  }, [theme]);

  useEffect(() => {
    try {
      window.localStorage.setItem(STORAGE_KEY, theme);
    } catch {
      // ignora
    }
  }, [theme]);

  const setTheme = useCallback((t: DossierTheme) => setThemeState(t), []);
  const cycleTheme = useCallback(() => {
    setThemeState((cur) => {
      const idx = DOSSIER_THEMES.indexOf(cur);
      return DOSSIER_THEMES[(idx + 1) % DOSSIER_THEMES.length];
    });
  }, []);

  return (
    <DossierThemeCtx.Provider value={{ theme, setTheme, cycleTheme }}>
      {children}
    </DossierThemeCtx.Provider>
  );
}

export function useDossierTheme(): Ctx {
  const ctx = useContext(DossierThemeCtx);
  if (!ctx) throw new Error("useDossierTheme must be used within <DossierThemeProvider>");
  return ctx;
}
