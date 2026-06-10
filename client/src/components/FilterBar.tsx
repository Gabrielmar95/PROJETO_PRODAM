// Barra de filtros globais — aplicada em seções de faturas
import { Search, X } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useFilters } from "@/contexts/FilterContext";

export default function FilterBar({ showAll = true }: { showAll?: boolean }) {
  const {
    filters,
    setFilter,
    resetFilters,
    regimes,
    contratos,
    anos,
    prescricoes,
    procedencias,
    filteredFaturas,
    allFaturas,
  } = useFilters();

  const hasActive =
    filters.search ||
    filters.regime !== "all" ||
    filters.contrato !== "all" ||
    filters.ano !== "all" ||
    filters.prescricao !== "all" ||
    filters.procedencia !== "all";

  return (
    <div className="forensic-card mb-4">
      <div className="flex flex-col gap-3">
        <div className="flex flex-col md:flex-row gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
            <Input
              value={filters.search}
              onChange={(e) => setFilter("search", e.target.value)}
              placeholder="Buscar por NF, contrato, regime, competência..."
              className="pl-9 h-8 text-[11px] bg-background/60 border-border focus-visible:border-primary focus-visible:ring-0"
            />
          </div>
          {hasActive && (
            <Button
              variant="ghost"
              size="sm"
              onClick={resetFilters}
              className="h-8 text-[11px] gap-1.5 text-muted-foreground hover:text-primary"
            >
              <X className="h-3 w-3" />
              Limpar filtros
            </Button>
          )}
        </div>

        <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
          <FilterSelect
            label="Regime"
            value={filters.regime}
            onChange={(v) => setFilter("regime", v)}
            options={regimes}
          />
          <FilterSelect
            label="Contrato"
            value={filters.contrato}
            onChange={(v) => setFilter("contrato", v)}
            options={contratos}
          />
          <FilterSelect
            label="Ano"
            value={filters.ano}
            onChange={(v) => setFilter("ano", v)}
            options={anos}
          />
          <FilterSelect
            label="Prescrição"
            value={filters.prescricao}
            onChange={(v) => setFilter("prescricao", v)}
            options={prescricoes}
          />
          <FilterSelect
            label="Procedência"
            value={filters.procedencia}
            onChange={(v) => setFilter("procedencia", v)}
            options={procedencias}
          />
        </div>

        {showAll && (
          <div className="flex items-center justify-between text-[10px] font-mono text-muted-foreground pt-1 border-t border-border/50">
            <span>
              Exibindo{" "}
              <span className="text-primary font-semibold">
                {filteredFaturas.length}
              </span>{" "}
              de {allFaturas.length} faturas
            </span>
            <span>
              Σ C1 filtrado:{" "}
              <span className="text-primary font-semibold">
                {filteredFaturas
                  .reduce((s, f) => s + f.c1Num, 0)
                  .toLocaleString("pt-BR", {
                    style: "currency",
                    currency: "BRL",
                  })}
              </span>
            </span>
          </div>
        )}
      </div>
    </div>
  );
}

function FilterSelect({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  options: string[];
}) {
  return (
    <div>
      <label className="block text-[9px] uppercase tracking-[0.15em] text-muted-foreground font-semibold mb-1">
        {label}
      </label>
      <Select value={value} onValueChange={onChange}>
        <SelectTrigger className="h-8 text-[11px] bg-background/60 border-border">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all" className="text-[11px]">
            Todos
          </SelectItem>
          {options.map((o) => (
            <SelectItem key={o} value={o} className="text-[11px]">
              {o}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
