// Calculadora Interativa — altera data-base e taxas para recalcular C1/C2/C3
import { useState, useMemo } from "react";
import { ForensicCard } from "@/components/ForensicCard";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Slider } from "@/components/ui/slider";
import { useFilters } from "@/contexts/FilterContext";
import { fmtBRL } from "@/data/helpers";
import { Calculator as CalcIcon, RotateCcw, TrendingUp, TrendingDown } from "lucide-react";
import { toast } from "sonner";

interface Props {
  baselineC1: number; // valor atual na data oficial
  baselineC2: number;
  baselineC3: number;
  baselineDate?: string; // "2026-04-16"
}

// Taxas anuais padrão (podem ser ajustadas)
const DEFAULT_SELIC = 10.5; // % a.a.
const DEFAULT_POUPANCA = 7.5; // % a.a.
const DEFAULT_C3 = 12.0; // 1% a.m. = 12% a.a.

export default function Calculator({
  baselineC1,
  baselineC2,
  baselineC3,
  baselineDate = "2026-04-16",
}: Props) {
  const { filteredFaturas } = useFilters();
  const [dataBase, setDataBase] = useState(baselineDate);
  const [selic, setSelic] = useState(DEFAULT_SELIC);
  const [poupanca, setPoupanca] = useState(DEFAULT_POUPANCA);
  const [c3Rate, setC3Rate] = useState(DEFAULT_C3);

  const baselineDt = useMemo(() => new Date(baselineDate), [baselineDate]);

  // Calcula diferença em meses entre data selecionada e baseline
  const monthsDiff = useMemo(() => {
    const selected = new Date(dataBase);
    if (isNaN(selected.getTime())) return 0;
    return (
      (selected.getFullYear() - baselineDt.getFullYear()) * 12 +
      (selected.getMonth() - baselineDt.getMonth())
    );
  }, [dataBase, baselineDt]);

  // Capitalização composta mensal: C1 × (1 + taxa_mensal)^meses
  const projections = useMemo(() => {
    const factor = (annualPct: number) =>
      Math.pow(1 + annualPct / 100 / 12, monthsDiff);

    return {
      c1: baselineC1 * factor(selic),
      c2: baselineC2 * factor(poupanca),
      c3: baselineC3 * factor(c3Rate),
    };
  }, [baselineC1, baselineC2, baselineC3, selic, poupanca, c3Rate, monthsDiff]);

  const delta = {
    c1: projections.c1 - baselineC1,
    c2: projections.c2 - baselineC2,
    c3: projections.c3 - baselineC3,
  };

  const reset = () => {
    setDataBase(baselineDate);
    setSelic(DEFAULT_SELIC);
    setPoupanca(DEFAULT_POUPANCA);
    setC3Rate(DEFAULT_C3);
    toast.info("Calculadora restaurada aos valores oficiais");
  };

  const hasChange = monthsDiff !== 0;
  const filteredCount = filteredFaturas.length;

  return (
    <ForensicCard title="Calculadora Interativa · Cenários" variant="highlight">
      <div className="flex items-start gap-2 mb-4 pb-3 border-b border-border/40">
        <CalcIcon className="h-4 w-4 text-primary mt-0.5" />
        <div className="flex-1">
          <p className="text-[11.5px] text-foreground/85 leading-relaxed">
            Simule a evolução dos três cenários alterando a data-base e as taxas.
            Projeção baseada em capitalização composta mensal aplicada sobre os
            valores consolidados.
          </p>
          <p className="text-[10px] text-muted-foreground mt-1 font-mono">
            Baseline: {fmtBRL(baselineC1)} C1 · {filteredCount} faturas no escopo atual
          </p>
        </div>
        <Button
          size="sm"
          variant="ghost"
          onClick={reset}
          className="h-7 text-[10px] gap-1 text-muted-foreground hover:text-primary shrink-0"
        >
          <RotateCcw className="h-3 w-3" />
          Restaurar
        </Button>
      </div>

      {/* Controles */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-5">
        <div>
          <label className="small-caps text-[10px] text-muted-foreground block mb-1.5">
            Data-base da Simulação
          </label>
          <Input
            type="date"
            value={dataBase}
            onChange={(e) => setDataBase(e.target.value)}
            className="h-8 text-[11px] bg-background/60 border-border"
          />
          <p className="text-[9px] font-mono text-muted-foreground mt-1">
            {monthsDiff === 0
              ? "Data oficial"
              : monthsDiff > 0
                ? `+${monthsDiff} ${monthsDiff === 1 ? "mês" : "meses"} em relação à baseline`
                : `${monthsDiff} ${Math.abs(monthsDiff) === 1 ? "mês" : "meses"} antes da baseline`}
          </p>
        </div>
        <RateSlider
          label="SELIC anual (C1)"
          value={selic}
          onChange={setSelic}
          min={5}
          max={20}
          step={0.25}
          color="#C5A55A"
        />
        <RateSlider
          label="Poupança anual (C2)"
          value={poupanca}
          onChange={setPoupanca}
          min={3}
          max={15}
          step={0.25}
          color="#6B8FA8"
        />
        <RateSlider
          label="1% a.m. · equivalente anual (C3)"
          value={c3Rate}
          onChange={setC3Rate}
          min={6}
          max={18}
          step={0.5}
          color="#6BAF5E"
        />
      </div>

      {/* Resultados */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <ResultCard
          label="C1 · SELIC"
          baseline={baselineC1}
          projected={projections.c1}
          delta={delta.c1}
          color="#C5A55A"
          active={hasChange}
        />
        <ResultCard
          label="C2 · Poupança"
          baseline={baselineC2}
          projected={projections.c2}
          delta={delta.c2}
          color="#6B8FA8"
          active={hasChange}
        />
        <ResultCard
          label="C3 · 1% a.m."
          baseline={baselineC3}
          projected={projections.c3}
          delta={delta.c3}
          color="#6BAF5E"
          active={hasChange}
        />
      </div>

      <p className="text-[9px] text-muted-foreground/80 mt-4 font-mono italic">
        *Simulação de aproximação; cálculo oficial considera IGPM, correção proporcional por fatura
        e a cláusula 11.1 do CT 022/2014.
      </p>
    </ForensicCard>
  );
}

function RateSlider({
  label,
  value,
  onChange,
  min,
  max,
  step,
  color,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  min: number;
  max: number;
  step: number;
  color: string;
}) {
  return (
    <div>
      <div className="flex items-center justify-between mb-1.5">
        <label className="small-caps text-[10px] text-muted-foreground">{label}</label>
        <span
          className="font-mono text-[11px] font-semibold tabular-nums"
          style={{ color }}
        >
          {value.toFixed(2)}%
        </span>
      </div>
      <Slider
        value={[value]}
        onValueChange={(v) => onChange(v[0])}
        min={min}
        max={max}
        step={step}
      />
      <div className="flex justify-between text-[8px] font-mono text-muted-foreground mt-1">
        <span>{min}%</span>
        <span>{max}%</span>
      </div>
    </div>
  );
}

function ResultCard({
  label,
  baseline,
  projected,
  delta,
  color,
  active,
}: {
  label: string;
  baseline: number;
  projected: number;
  delta: number;
  color: string;
  active: boolean;
}) {
  const pct = baseline > 0 ? (delta / baseline) * 100 : 0;
  const isPositive = delta > 0;
  const isZero = Math.abs(delta) < 1;

  return (
    <div
      className="relative rounded-sm border p-3 transition-all"
      style={{
        borderColor: active ? color : "var(--border)",
        background: active
          ? `linear-gradient(135deg, color-mix(in oklch, ${color} 8%, var(--bg-2)), var(--bg-2))`
          : "var(--bg-2)",
      }}
    >
      <div className="small-caps text-[10px] font-semibold mb-1" style={{ color }}>
        {label}
      </div>
      <div
        className="font-display text-[22px] leading-[1.1] font-semibold tabular-nums"
        style={{ color: active ? "var(--t1)" : "var(--t2)" }}
      >
        {fmtBRL(projected)}
      </div>
      {active && !isZero && (
        <div className="flex items-center gap-1.5 mt-1.5 text-[10px] font-mono">
          {isPositive ? (
            <TrendingUp className="h-3 w-3 text-emerald-400" />
          ) : (
            <TrendingDown className="h-3 w-3 text-red-400" />
          )}
          <span
            className={isPositive ? "text-emerald-400" : "text-red-400"}
          >
            {isPositive ? "+" : ""}
            {fmtBRL(delta)} ({isPositive ? "+" : ""}
            {pct.toFixed(2)}%)
          </span>
        </div>
      )}
      {!active && (
        <div className="text-[10px] text-muted-foreground font-mono mt-1.5">
          Baseline oficial
        </div>
      )}
    </div>
  );
}
