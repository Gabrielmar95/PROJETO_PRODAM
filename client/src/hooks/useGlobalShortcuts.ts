/**
 * S3-M13 — Atalhos globais de teclado.
 *
 * Convenção: todos os atalhos são prefixados com Alt (Option no macOS) para
 * não conflitar com atalhos do navegador (Ctrl+T, Ctrl+E, Ctrl+D já são
 * usados para nova aba, favorito e barra de endereço).
 *
 *   Alt+D  → cicla densidade (compact → comfort → detailed)
 *   Alt+T  → cicla tema dossier (dossier → day → print)  [já em ThemeSwitcher.tsx]
 *   Alt+E  → dispara export CSV da seção atual
 *   Alt+?  → mostra toast com lista de atalhos
 *
 * Os atalhos são desabilitados quando:
 *   - O foco está em <input>, <textarea> ou contentEditable (digitação real do usuário)
 *   - Algum modal/dialog está aberto (detectado via [role="dialog"][aria-modal="true"])
 */
import { useEffect } from "react";
import { toast } from "sonner";
import { useDensity, DENSITY_LABEL } from "@/contexts/DensityContext";

export interface GlobalShortcutsOptions {
  /** Callback disparado quando Alt+E é pressionado. */
  onExport?: () => void;
  /** Callback disparado quando Alt+P é pressionado (impressão). */
  onPrint?: () => void;
  /** Desabilita todos os atalhos (útil em telas modais). */
  disabled?: boolean;
}

function isTypingTarget(target: EventTarget | null): boolean {
  if (!(target instanceof HTMLElement)) return false;
  const tag = target.tagName;
  if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return true;
  if (target.isContentEditable) return true;
  return false;
}

function hasOpenModal(): boolean {
  if (typeof document === "undefined") return false;
  return !!document.querySelector('[role="dialog"][aria-modal="true"]');
}

export function useGlobalShortcuts({
  onExport,
  onPrint,
  disabled = false,
}: GlobalShortcutsOptions = {}) {
  const { density, cycleDensity } = useDensity();

  useEffect(() => {
    if (disabled) return;

    function onKey(e: KeyboardEvent) {
      if (!e.altKey) return;
      if (isTypingTarget(e.target)) return;
      if (hasOpenModal()) return;

      const key = e.key.toLowerCase();

      switch (key) {
        case "d": {
          e.preventDefault();
          cycleDensity();
          // Le um tick depois para mostrar o NOVO estado, não o anterior
          requestAnimationFrame(() => {
            const next = document.documentElement.getAttribute("data-density") || density;
            toast.success(
              `Densidade: ${DENSITY_LABEL[next as keyof typeof DENSITY_LABEL] ?? next}`,
              { duration: 1500 },
            );
          });
          break;
        }
        case "e": {
          if (onExport) {
            e.preventDefault();
            onExport();
          }
          break;
        }
        case "p": {
          if (onPrint) {
            e.preventDefault();
            onPrint();
          }
          break;
        }
        case "?":
        case "/": {
          // Alt+? em layouts US é Alt+Shift+/, mas alguns reportam só "?"
          e.preventDefault();
          toast.info("Atalhos: Alt+D densidade · Alt+T tema · Alt+E export · Alt+P imprimir", {
            duration: 4000,
          });
          break;
        }
        default:
          break;
      }
    }

    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [cycleDensity, density, onExport, onPrint, disabled]);
}
