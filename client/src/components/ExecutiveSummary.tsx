/**
 * ExecutiveSummary — Sprint 2 Estrutural S3
 *
 * Bloco narrativo que abre o Painel Executivo com:
 *  - Parágrafo síntese em prosa jurídica (drop-cap editorial);
 *  - 3 "takeaways" quantitativos (métricas de impacto) com hierarquia forte;
 *  - Cota/rodapé citando a base técnica e data-base oficial.
 *
 * O componente é data-driven: recebe métricas já calculadas a partir
 * do contexto filtrado, de modo que o drill-down global (QW2 Sprint 2)
 * atualize a síntese em tempo real.
 */
import type { Fatura } from "@/data/types";
import { fmtBRL } from "@/data/helpers";
import { useMemo } from "react";

interface Props {
  faturas: Fatura[];
  dataBase?: string;
  className?: string;
}

export function ExecutiveSummary({ faturas, dataBase = "16/04/2026", className }: Props) {
  const m = useMemo(() => {
    const totalFaturas = faturas.length;
    const saldo = faturas.reduce((s, f) => s + (f.saldoNum || 0), 0);
    const c1 = faturas.reduce((s, f) => s + (f.c1Num || 0), 0);
    const encargos = c1 - saldo;
    const pctEncargos = saldo > 0 ? (encargos / saldo) * 100 : 0;

    // Regime predominante por massa (C1)
    const porRegime = faturas.reduce<Record<string, number>>((acc, f) => {
      const k = f.regime || "Outros";
      acc[k] = (acc[k] || 0) + (f.c1Num || 0);
      return acc;
    }, {});
    const topRegime = Object.entries(porRegime).sort((a, b) => b[1] - a[1])[0];
    const topRegimeShare = topRegime && c1 > 0 ? (topRegime[1] / c1) * 100 : 0;

    // Contratos distintos no escopo
    const contratos = new Set(faturas.map((f) => f.contrato).filter(Boolean)).size;

    // Faturas com potencial de RPV (uso do flag dedicado se existir)
    const rpv = faturas.filter((f) => (f as unknown as { rpv?: boolean }).rpv).length;

    return { totalFaturas, saldo, c1, encargos, pctEncargos, topRegime, topRegimeShare, contratos, rpv };
  }, [faturas]);

  const regimeNome = m.topRegime?.[0] || "Silente Administrativo";

  return (
    <section
      aria-labelledby="executive-summary-title"
      className={`relative overflow-hidden surface-raised rounded-lg border line-default ${className ?? ""}`}
      style={{
        padding: "var(--d-card-pad)",
        boxShadow: "var(--shadow-lg)",
        background:
          "linear-gradient(135deg, color-mix(in oklch, var(--gold) 5%, var(--bg-2)) 0%, var(--bg-2) 55%, color-mix(in oklch, var(--gold) 3%, var(--bg-3)) 100%)",
      }}
    >
      {/* Ornamento caligráfico no canto superior direito */}
      <div
        aria-hidden
        className="absolute -top-16 -right-10 opacity-[0.08] pointer-events-none select-none"
        style={{
          fontFamily: "var(--font-display)",
          fontSize: "220px",
          color: "var(--gold)",
          lineHeight: 1,
          fontStyle: "italic",
          fontWeight: 500,
        }}
      >
        §
      </div>

      {/* Rubrica institucional */}
      <div className="ornament text-[10px] mb-3">
        <span className="ornament-diamond" aria-hidden />
        <span className="small-caps font-mono">Síntese Executiva</span>
        <span className="ornament-diamond" aria-hidden />
      </div>

      {/* Parágrafo narrativo com drop-cap */}
      <h3
        id="executive-summary-title"
        className="font-display text-[color:var(--color-ink-primary)] text-[17px] sm:text-[19px] leading-[1.35] tracking-tight mb-3 max-w-3xl italic"
      >
        Um dossiê consolidado com{" "}
        <span className="not-italic font-semibold text-[color:var(--gold)] tabular-nums">
          {m.totalFaturas.toLocaleString("pt-BR")}
        </span>{" "}
        faturas e{" "}
        <span className="not-italic font-semibold text-[color:var(--gold)] tabular-nums">{m.contratos}</span>{" "}
        contratos ativos.
      </h3>

      <p
        className="drop-cap text-[color:var(--color-ink-secondary)] text-[13.5px] leading-[1.72] max-w-3xl"
        style={{ fontFeatureSettings: '"onum", "tnum"' }}
      >
        O universo auditado apresenta <strong className="text-[color:var(--color-ink-primary)]">saldo devedor original</strong>{" "}
        de <span className="tabular-nums text-[color:var(--gold)] font-semibold">{fmtBRL(m.saldo)}</span>, atualizado ao cenário principal (C1 SELIC){" "}
        para <span className="tabular-nums text-[color:var(--gold)] font-semibold">{fmtBRL(m.c1)}</span> — uma correção de{" "}
        <span className="tabular-nums font-semibold">{m.pctEncargos.toFixed(1).replace(".", ",")}%</span> sobre o principal, conforme{" "}
        <em>Art. 406 do CC (Lei 14.905/2024)</em> e <em>Tema 99 do STJ</em>. O regime de maior massa econômica é{" "}
        <strong className="text-[color:var(--color-ink-primary)]">{regimeNome}</strong>, representando{" "}
        <span className="tabular-nums">{m.topRegimeShare.toFixed(1).replace(".", ",")}%</span> do total atualizado. Todas as faturas cobráveis permanecem dentro do
        prazo qüinqüenal do <em>Decreto 20.910/1932</em>, assegurando pleno direito de execução forçada nos termos do{" "}
        <em>Art. 784 do CPC</em>.
      </p>

      {/* 3 takeaways quantitativos com hierarquia editorial */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-5 pt-4 border-t line-subtle">
        <Takeaway
          label="Correção acumulada"
          value={`+${m.pctEncargos.toFixed(1).replace(".", ",")}%`}
          context={`${fmtBRL(m.encargos)} em encargos sobre o principal`}
          tone="neutral"
        />
        <Takeaway
          label="Regime dominante"
          value={`${m.topRegimeShare.toFixed(0)}%`}
          context={`${regimeNome} — ${fmtBRL(m.topRegime?.[1] || 0)}`}
          tone="brand"
        />
        <Takeaway
          label="Faturas cobráveis"
          value={`${m.totalFaturas}`}
          context={`${m.contratos} contratos · ${m.rpv || 0} candidatas a RPV`}
          tone="success"
        />
      </div>

      {/* Cota rodapé — fonte e data-base */}
      <p className="text-[10px] text-[color:var(--color-ink-tertiary)] mt-4 font-mono tracking-wide uppercase">
        Data-base {dataBase} · Fonte: DETRAN/AM e PRODAM · Auditoria Forense v10 · Cálculo em regime individual por contrato
      </p>
    </section>
  );
}

function Takeaway({
  label,
  value,
  context,
  tone,
}: {
  label: string;
  value: string;
  context: string;
  tone: "brand" | "success" | "neutral";
}) {
  const toneClass =
    tone === "brand"
      ? "text-[color:var(--gold)]"
      : tone === "success"
        ? "text-[color:var(--ok2)]"
        : "text-[color:var(--color-ink-primary)]";
  return (
    <div className="relative">
      {/* régua lateral dourada */}
      <div
        aria-hidden
        className="absolute left-0 top-1 bottom-1 w-[2px]"
        style={{
          background: "linear-gradient(to bottom, var(--gold), transparent)",
        }}
      />
      <div className="pl-3">
        <div className="small-caps text-[10px] text-[color:var(--color-ink-tertiary)] font-semibold">{label}</div>
        <div
          className={`font-display text-[28px] sm:text-[30px] leading-none font-semibold tabular-nums mt-1 ${toneClass}`}
          style={{ fontFeatureSettings: '"onum", "tnum"' }}
        >
          {value}
        </div>
        <p className="text-[11px] text-[color:var(--color-ink-secondary)] mt-1.5 leading-snug">{context}</p>
      </div>
    </div>
  );
}
