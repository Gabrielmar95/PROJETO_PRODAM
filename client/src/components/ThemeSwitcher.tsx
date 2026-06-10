/**
 * ThemeSwitcher — Sprint 3 Aspiracional A1
 *
 * Controle visual dos 3 modos do dossiê: Dossiê (Moon), Dia (Sun), Print (Printer).
 * Integrado ao header via botões segmentados com ícones Lucide. Acessível via
 * atalho Alt+T (cicla entre modos) para uso de teclado.
 */
import { useEffect } from "react";
import { Moon, Sun, Printer } from "lucide-react";
import { useDossierTheme, type DossierTheme } from "@/contexts/DossierThemeContext";

const OPTIONS: Array<{ value: DossierTheme; label: string; title: string; Icon: typeof Moon }> = [
  { value: "dossier", label: "DOS", title: "Modo Dossiê — noturno institucional", Icon: Moon },
  { value: "day", label: "DIA", title: "Modo Dia — editorial claro", Icon: Sun },
  { value: "print", label: "IMP", title: "Preview de impressão", Icon: Printer },
];

export default function ThemeSwitcher() {
  const { theme, setTheme, cycleTheme } = useDossierTheme();

  // Atalho Alt+T para ciclar entre modos
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.altKey && (e.key === "t" || e.key === "T")) {
        e.preventDefault();
        cycleTheme();
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [cycleTheme]);

  return (
    <div
      className="theme-switcher inline-flex items-center gap-0 rounded-md border border-[color:var(--line-subtle)] bg-[color:var(--surface-1)] p-[2px] print-hide"
      role="tablist"
      aria-label="Alterar tema do dossiê"
      title="Alt+T para alternar"
    >
      {OPTIONS.map(({ value, label, title, Icon }) => {
        const active = theme === value;
        return (
          <button
            key={value}
            role="tab"
            aria-selected={active}
            onClick={() => setTheme(value)}
            title={title}
            className={[
              "inline-flex items-center gap-1 px-2 py-[5px] text-[10px] font-mono tracking-[0.1em] rounded-[4px] transition-colors",
              active
                ? "bg-[color:var(--gold)] text-[color:var(--surface-1)] font-semibold"
                : "text-[color:var(--ink-3)] hover:text-[color:var(--ink-1)] hover:bg-[color:var(--surface-2)]",
            ].join(" ")}
          >
            <Icon size={11} strokeWidth={active ? 2.2 : 1.6} />
            <span>{label}</span>
          </button>
        );
      })}
    </div>
  );
}
