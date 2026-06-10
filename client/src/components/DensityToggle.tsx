/**
 * DensityToggle — Sprint 2 Estrutural S2
 *
 * Controle segmentado de densidade (Compacto / Conforto / Detalhado).
 * Renderizado no ForensicHeader ao lado dos atalhos de busca e exportação.
 *
 * Design:
 *  - Segmented control vertical em mobile (<sm) e horizontal em desktop;
 *  - Indicador dourado no item ativo com halo sutil;
 *  - Ícones dos 3 níveis: linha fina (compact), linha média (comfort), linha espaçada (detailed);
 *  - Tooltips com descrição completa do comportamento.
 */
import { useDensity, type Density, DENSITY_LABEL, DENSITY_DESCRIPTION } from "@/contexts/DensityContext";
import { cn } from "@/lib/utils";
import { Rows4, Rows3, Rows2 } from "lucide-react";

const OPTIONS: Array<{ value: Density; Icon: typeof Rows4 }> = [
  { value: "compact", Icon: Rows4 },
  { value: "comfort", Icon: Rows3 },
  { value: "detailed", Icon: Rows2 },
];

export function DensityToggle({ className }: { className?: string }) {
  const { density, setDensity } = useDensity();

  return (
    <div
      role="radiogroup"
      aria-label="Densidade visual do dashboard"
      className={cn(
        "inline-flex items-center gap-0.5 rounded-full border line-default",
        "surface-overlay px-1 py-1",
        className,
      )}
      style={{ boxShadow: "var(--shadow-xs)" }}
    >
      {OPTIONS.map(({ value, Icon }) => {
        const active = value === density;
        return (
          <button
            key={value}
            role="radio"
            aria-checked={active}
            onClick={() => setDensity(value)}
            title={`${DENSITY_LABEL[value]} — ${DENSITY_DESCRIPTION[value]}`}
            className={cn(
              "group inline-flex items-center gap-1.5 rounded-full transition-all",
              "px-2 py-1 text-[10px] tracking-wide uppercase",
              active
                ? "bg-[color:var(--gold)] text-[color:var(--color-ink-onbrand)] shadow-[var(--shadow-gold-halo)]"
                : "text-[color:var(--color-ink-tertiary)] hover:text-[color:var(--color-ink-brand)]",
            )}
          >
            <Icon className="w-3.5 h-3.5" strokeWidth={active ? 2.25 : 1.75} />
            <span className="hidden md:inline font-mono">{DENSITY_LABEL[value].slice(0, 3)}</span>
          </button>
        );
      })}
    </div>
  );
}
