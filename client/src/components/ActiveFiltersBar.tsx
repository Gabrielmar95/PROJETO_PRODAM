// Barra de chips de filtros ativos — sempre visível quando há filtros
import { X, Filter } from "lucide-react";
import { useFilters } from "@/contexts/FilterContext";

export default function ActiveFiltersBar() {
  const { activeFilters, resetFilter, resetFilters, hasActive, filteredFaturas, allFaturas } =
    useFilters();

  if (!hasActive) return null;

  return (
    <div className="sticky top-0 z-30 -mx-5 lg:-mx-8 mb-4 px-5 lg:px-8 py-2.5 backdrop-blur-md bg-[color:var(--bg-2)]/85 border-b border-primary/20 print:hidden">
      <div className="flex flex-wrap items-center gap-2">
        <div className="flex items-center gap-1.5 shrink-0 pr-1">
          <Filter className="h-3 w-3 text-primary" />
          <span className="small-caps text-[10px] text-primary font-semibold">
            Filtros Ativos
          </span>
          <span className="text-[10px] font-mono text-muted-foreground">
            ({filteredFaturas.length}/{allFaturas.length})
          </span>
        </div>
        {activeFilters.map((f) => (
          <button
            key={f.key}
            onClick={() => resetFilter(f.key)}
            className="group flex items-center gap-1.5 px-2 py-1 rounded-sm border border-primary/40 bg-primary/10 text-[10px] text-primary hover:bg-primary/20 hover:border-primary transition-colors"
            title={`Remover filtro ${f.label}`}
          >
            <span className="font-mono text-[9px] opacity-70 uppercase tracking-wider">
              {f.label}:
            </span>
            <span className="font-semibold truncate max-w-[160px]">{f.value}</span>
            <X className="h-2.5 w-2.5 opacity-60 group-hover:opacity-100" />
          </button>
        ))}
        <button
          onClick={resetFilters}
          className="ml-auto text-[10px] text-muted-foreground hover:text-primary px-2 py-1 transition-colors"
        >
          Limpar todos
        </button>
      </div>
    </div>
  );
}
