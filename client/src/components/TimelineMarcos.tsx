/**
 * TimelineMarcos — Sprint 2 Estrutural S4
 *
 * Cronologia proporcional ao tempo (não a um grid de anos uniforme) dos
 * marcos interruptivos da prescrição (Art. 202 VI CC). Cada marco é
 * posicionado pelo offset normalizado entre minDate e maxDate do dossiê,
 * permitindo visualizar clusters e lacunas reais de atividade.
 *
 * Design:
 *  - Eixo horizontal com ticks de ano + labels;
 *  - Quando "Agrupar por contrato" está ativo, os marcos são distribuídos
 *    em faixas horizontais (swimlanes) por contrato; caso contrário,
 *    colapsam em uma única faixa central com jitter vertical sutil;
 *  - Tamanho da bolha ∝ valor da NE; cor por força da cadeia documental;
 *  - Tooltip rico (valor, cadeia, docs, prescrição, última atualização);
 *  - Chips para filtrar top-N contratos;
 *  - Legenda e escala no topo.
 */
import { useMemo, useState } from "react";
import { parseBRL, fmtBRL } from "@/data/helpers";

type Marco = {
  ne?: string | null;
  ano?: string | null;
  prescricao?: string | null;
  cadeia?: string | null;
  valor?: string | null;
  dataUltima?: string | null;
  docs?: number | null;
  contrato?: string | null;
};

const HEIGHT_SINGLE = 140;
const LANE_HEIGHT = 26;
const AXIS_PAD_X = 28;

// Converte "16/04/2022" ou "2022-04-16" em timestamp; retorna NaN se não parsear
function toTime(raw?: string | null): number {
  if (!raw) return NaN;
  // Pattern BR dd/mm/yyyy
  const br = raw.match(/^(\d{2})\/(\d{2})\/(\d{4})$/);
  if (br) return Date.UTC(+br[3], +br[2] - 1, +br[1]);
  // ISO
  const iso = Date.parse(raw);
  return Number.isFinite(iso) ? iso : NaN;
}

function niceDate(raw?: string | null): string {
  if (!raw) return "—";
  const t = toTime(raw);
  if (!Number.isFinite(t)) return raw;
  const d = new Date(t);
  return d.toLocaleDateString("pt-BR", { day: "2-digit", month: "short", year: "numeric" });
}

export default function TimelineMarcos({ marcos }: { marcos: Marco[] }) {
  const [groupByContract, setGroupByContract] = useState(false);
  const [hovered, setHovered] = useState<{ marco: Marco; x: number; y: number } | null>(null);
  const [contratoFocus, setContratoFocus] = useState<string | null>(null);

  // Pré-processa: extrai timestamp (usa dataUltima se houver; fallback 30/06 do ano)
  const enriched = useMemo(() => {
    return marcos
      .map((m) => {
        const tPref = toTime(m.dataUltima);
        const tFallback = m.ano ? Date.UTC(parseInt(m.ano, 10), 5, 30) : NaN;
        const t = Number.isFinite(tPref) ? tPref : tFallback;
        const v = parseBRL(m.valor || "0");
        return { m, t, v };
      })
      .filter((x) => Number.isFinite(x.t));
  }, [marcos]);

  const { minT, maxT, maxV } = useMemo(() => {
    if (enriched.length === 0) return { minT: 0, maxT: 1, maxV: 0 };
    const ts = enriched.map((x) => x.t);
    return {
      minT: Math.min(...ts),
      maxT: Math.max(...ts),
      maxV: Math.max(...enriched.map((x) => x.v)),
    };
  }, [enriched]);

  // Top-N contratos por valor agregado
  const topContratos = useMemo(() => {
    const agg = new Map<string, number>();
    enriched.forEach(({ m, v }) => {
      const c = m.contrato || "—";
      agg.set(c, (agg.get(c) || 0) + v);
    });
    return Array.from(agg.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 8)
      .map(([name]) => name);
  }, [enriched]);

  // Gera anos ticks
  const yearTicks = useMemo(() => {
    if (!Number.isFinite(minT) || !Number.isFinite(maxT) || minT === maxT) return [] as number[];
    const y0 = new Date(minT).getUTCFullYear();
    const y1 = new Date(maxT).getUTCFullYear();
    const arr: number[] = [];
    for (let y = y0; y <= y1; y++) arr.push(Date.UTC(y, 0, 1));
    return arr;
  }, [minT, maxT]);

  const span = Math.max(1, maxT - minT);
  const filtered = contratoFocus ? enriched.filter((e) => (e.m.contrato || "—") === contratoFocus) : enriched;

  // Em modo swimlanes, agrupa por contrato
  const lanes = useMemo(() => {
    if (!groupByContract) return [{ contrato: null as string | null, items: filtered }];
    const map = new Map<string, typeof enriched>();
    filtered.forEach((e) => {
      const c = e.m.contrato || "—";
      if (!map.has(c)) map.set(c, []);
      map.get(c)!.push(e);
    });
    return Array.from(map.entries())
      .sort((a, b) => b[1].length - a[1].length)
      .map(([contrato, items]) => ({ contrato, items }));
  }, [filtered, groupByContract]);

  const heightTotal = groupByContract ? Math.max(HEIGHT_SINGLE, lanes.length * LANE_HEIGHT + 40) : HEIGHT_SINGLE;

  if (enriched.length === 0) {
    return <div className="text-sm ink-tertiary italic">Sem marcos com datas válidas para cronologia.</div>;
  }

  return (
    <div className="relative">
      {/* Legenda + controles */}
      <div className="flex items-center flex-wrap gap-3 mb-4 text-[10px] font-mono tracking-wider ink-tertiary uppercase">
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-[color:var(--gold)] shadow-[0_0_6px_rgba(197,165,90,0.5)]" />
          Cadeia Forte/Completa
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full border border-[color:var(--gold-d)] bg-transparent" />
          Outros
        </span>
        <span className="flex items-center gap-1.5 ml-1">
          <span className="w-1 h-1 rounded-full bg-[color:var(--gold)]" />
          <span className="w-2.5 h-2.5 rounded-full bg-[color:var(--gold)]" />
          <span className="text-[9px] tracking-widest ink-tertiary">Tamanho ∝ Valor</span>
        </span>

        <div className="ml-auto flex items-center gap-2">
          <button
            onClick={() => setGroupByContract((v) => !v)}
            className={`px-2.5 py-1 rounded-full border transition-all ${
              groupByContract
                ? "bg-[color:var(--gold)] text-[color:var(--color-ink-onbrand)] border-transparent shadow-[var(--shadow-gold-halo)]"
                : "line-default text-[color:var(--color-ink-brand)] hover:bg-[color:var(--color-surface-brand)]"
            }`}
          >
            {groupByContract ? "Agrupado por contrato" : "Colapsar em faixa única"}
          </button>
          {contratoFocus && (
            <button
              onClick={() => setContratoFocus(null)}
              className="px-2 py-1 rounded-full border line-default ink-tertiary hover:ink-brand"
            >
              Limpar ×
            </button>
          )}
        </div>
      </div>

      {/* Chips de contratos top-N */}
      {topContratos.length > 1 && (
        <div className="flex items-center gap-1.5 flex-wrap mb-3">
          <span className="text-[9px] small-caps ink-tertiary tracking-widest">Focar contrato</span>
          {topContratos.map((c) => {
            const active = c === contratoFocus;
            return (
              <button
                key={c}
                onClick={() => setContratoFocus(active ? null : c)}
                className={`text-[10px] font-mono px-2 py-0.5 rounded-full border transition-all ${
                  active
                    ? "bg-[color:var(--gold)] text-[color:var(--color-ink-onbrand)] border-transparent"
                    : "line-subtle ink-secondary hover:ink-brand hover:line-default"
                }`}
              >
                {c}
              </button>
            );
          })}
        </div>
      )}

      {/* SVG cronologia */}
      <div className="relative rounded surface-overlay border line-subtle overflow-hidden" style={{ padding: "16px 4px 28px" }}>
        <svg
          role="img"
          aria-label="Cronologia proporcional dos marcos interruptivos"
          viewBox={`0 0 1000 ${heightTotal}`}
          preserveAspectRatio="none"
          className="w-full"
          style={{ height: heightTotal }}
        >
          <defs>
            <linearGradient id="tl-axis" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="var(--gold)" stopOpacity="0" />
              <stop offset="20%" stopColor="var(--gold)" stopOpacity="0.5" />
              <stop offset="80%" stopColor="var(--gold)" stopOpacity="0.5" />
              <stop offset="100%" stopColor="var(--gold)" stopOpacity="0" />
            </linearGradient>
            <radialGradient id="tl-forte" cx="0.5" cy="0.5" r="0.5">
              <stop offset="0%" stopColor="var(--gold-l)" />
              <stop offset="100%" stopColor="var(--gold-d)" />
            </radialGradient>
          </defs>

          {/* Eixo horizontal */}
          <line
            x1={AXIS_PAD_X}
            x2={1000 - AXIS_PAD_X}
            y1={heightTotal - 22}
            y2={heightTotal - 22}
            stroke="url(#tl-axis)"
            strokeWidth={1}
          />

          {/* Year ticks + labels */}
          {yearTicks.map((t) => {
            const x = AXIS_PAD_X + ((t - minT) / span) * (1000 - 2 * AXIS_PAD_X);
            const y = new Date(t).getUTCFullYear();
            return (
              <g key={t}>
                <line x1={x} x2={x} y1={heightTotal - 22} y2={heightTotal - 18} stroke="var(--gold-d)" strokeOpacity={0.5} />
                <text
                  x={x}
                  y={heightTotal - 6}
                  textAnchor="middle"
                  fontSize={10}
                  fill="var(--color-ink-tertiary)"
                  fontFamily="var(--font-mono)"
                  letterSpacing="0.1em"
                >
                  {y}
                </text>
              </g>
            );
          })}

          {/* Lanes (ou faixa única) */}
          {lanes.map((lane, laneIdx) => {
            const baseY = groupByContract
              ? 18 + laneIdx * LANE_HEIGHT + LANE_HEIGHT / 2
              : heightTotal / 2 - 10;

            return (
              <g key={lane.contrato ?? "single"}>
                {groupByContract && (
                  <>
                    <line
                      x1={AXIS_PAD_X}
                      x2={1000 - AXIS_PAD_X}
                      y1={baseY}
                      y2={baseY}
                      stroke="var(--color-line-subtle)"
                      strokeDasharray="2 3"
                    />
                    <text
                      x={AXIS_PAD_X - 2}
                      y={baseY + 3}
                      textAnchor="end"
                      fontSize={9}
                      fill="var(--color-ink-tertiary)"
                      fontFamily="var(--font-mono)"
                    >
                      {lane.contrato}
                    </text>
                  </>
                )}
                {lane.items.map(({ m, t, v }, i) => {
                  const x = AXIS_PAD_X + ((t - minT) / span) * (1000 - 2 * AXIS_PAD_X);
                  const sizePx = maxV > 0 ? Math.max(3, Math.min(10, (v / maxV) * 10 + 3)) : 5;
                  // jitter vertical leve apenas quando colapsado para reduzir oclusão
                  const jitter = groupByContract ? 0 : ((i * 37) % 13) - 6;
                  const y = baseY + jitter;
                  const isForte = m.cadeia === "FORTE" || m.cadeia === "COMPLETA";
                  return (
                    <circle
                      key={`${lane.contrato ?? "s"}-${i}`}
                      cx={x}
                      cy={y}
                      r={sizePx}
                      fill={isForte ? "url(#tl-forte)" : "transparent"}
                      stroke="var(--gold)"
                      strokeWidth={isForte ? 0 : 1}
                      opacity={0.88}
                      className="cursor-pointer transition-transform duration-150 hover:scale-125"
                      onMouseEnter={(e) => {
                        const r = (e.target as SVGCircleElement).getBoundingClientRect();
                        setHovered({ marco: m, x: r.left + r.width / 2, y: r.top });
                      }}
                      onMouseLeave={() => setHovered(null)}
                      aria-label={`NE ${m.ne} · ${fmtBRL(v)}`}
                      tabIndex={0}
                    />
                  );
                })}
              </g>
            );
          })}
        </svg>

        {/* Indicadores das extremidades */}
        <div className="pointer-events-none absolute top-2 left-4 text-[9px] font-mono ink-tertiary tracking-widest">
          {niceDate(new Date(minT).toISOString())}
        </div>
        <div className="pointer-events-none absolute top-2 right-4 text-[9px] font-mono ink-tertiary tracking-widest">
          {niceDate(new Date(maxT).toISOString())}
        </div>
      </div>

      {/* Contador sumário abaixo */}
      <div className="flex items-center gap-4 text-[10px] font-mono ink-tertiary mt-2">
        <span>
          {filtered.length} marcos plotados {contratoFocus && <>· foco em <strong className="ink-brand">{contratoFocus}</strong></>}
        </span>
        <span className="ml-auto">{groupByContract ? `${lanes.length} contratos em faixas` : "faixa única"}</span>
      </div>

      {/* Tooltip flutuante rico */}
      {hovered && (
        <div
          className="fixed z-50 pointer-events-none surface-overlay border line-default rounded shadow-institutional-lg px-3 py-2 text-[10.5px] font-mono max-w-[320px]"
          style={{ left: hovered.x + 12, top: hovered.y + 12 }}
          role="tooltip"
        >
          <div className="flex items-baseline gap-2 mb-1">
            <span className="ink-brand font-semibold">NE {hovered.marco.ne}</span>
            {hovered.marco.contrato && (
              <span className="text-[9px] ink-tertiary">· CT {hovered.marco.contrato}</span>
            )}
          </div>
          {hovered.marco.valor && (
            <div className="ink-primary tabular-nums">{fmtBRL(parseBRL(hovered.marco.valor))}</div>
          )}
          <div className="grid grid-cols-2 gap-x-2 gap-y-0.5 mt-1 text-[10px]">
            {hovered.marco.ano && (
              <>
                <span className="ink-tertiary">Ano</span>
                <span className="ink-secondary">{hovered.marco.ano}</span>
              </>
            )}
            {hovered.marco.cadeia && (
              <>
                <span className="ink-tertiary">Cadeia</span>
                <span className="ink-brand">{hovered.marco.cadeia}</span>
              </>
            )}
            {hovered.marco.docs != null && (
              <>
                <span className="ink-tertiary">Documentos</span>
                <span className="ink-secondary">{hovered.marco.docs}</span>
              </>
            )}
            {hovered.marco.dataUltima && (
              <>
                <span className="ink-tertiary">Últ. atualização</span>
                <span className="ink-secondary">{niceDate(hovered.marco.dataUltima)}</span>
              </>
            )}
          </div>
          {hovered.marco.prescricao && (
            <div className="mt-1.5 pt-1.5 border-t line-subtle text-[9.5px] ink-secondary italic">
              {hovered.marco.prescricao}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
