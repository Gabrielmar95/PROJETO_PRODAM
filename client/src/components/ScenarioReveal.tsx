/**
 * ScenarioReveal — Sprint 3 Aspiracional A3
 *
 * Storytelling scroll-driven dos 3 cenários (C1/C2/C3). Cada card revela-se
 * quando entra na viewport via IntersectionObserver, com:
 *   - Número principal animado (count-up com easing cubic-out)
 *   - Stagger sequencial interno (kicker → valor → narrativa → marker)
 *   - Delta em % sobre saldo original
 *   - Pull-quote entre cartões com aparição progressiva
 *
 * Design: cards editoriais com régua lateral dourada, tipografia contida,
 * narrativa curta (~2 linhas) e código da tese em pill.
 */
import { useInView, useCountUp } from "@/hooks/useReveal";
import { fmtBRL } from "@/data/helpers";

export interface Scenario {
  code: string;          // ex: "C1"
  label: string;         // ex: "SELIC"
  legalBasis: string;    // ex: "Lei AM 2.748/2002 · Art. 406 CC"
  total: number;         // valor C1/C2/C3
  narrative: string;     // narrativa curta
  pullQuote?: string;    // cota que aparece DEPOIS do card (opcional)
}

interface Props {
  saldoOriginal: number;
  scenarios: [Scenario, Scenario, Scenario];
}

export default function ScenarioReveal({ saldoOriginal, scenarios }: Props) {
  return (
    <div className="scenario-reveal-wrap">
      {scenarios.map((s, i) => (
        <div key={s.code}>
          <ScenarioCard scenario={s} saldoOriginal={saldoOriginal} idx={i} />
          {s.pullQuote && i < scenarios.length - 1 && (
            <PullQuote text={s.pullQuote} />
          )}
        </div>
      ))}
    </div>
  );
}

function ScenarioCard({
  scenario,
  saldoOriginal,
  idx,
}: {
  scenario: Scenario;
  saldoOriginal: number;
  idx: number;
}) {
  const [ref, inView] = useInView<HTMLDivElement>({ threshold: 0.25 });
  const animated = useCountUp(scenario.total, {
    enabled: inView,
    duration: 1600,
    delay: 180,
  });
  const delta =
    saldoOriginal > 0
      ? ((scenario.total / saldoOriginal - 1) * 100).toFixed(1).replace(".", ",")
      : "0,0";

  const positionalStyle = {
    "--idx": String(idx),
  } as React.CSSProperties;

  return (
    <article
      ref={ref}
      className={`scenario-card ${inView ? "is-visible" : ""}`}
      style={positionalStyle}
      data-scenario={scenario.code}
    >
      <aside className="scenario-rule" aria-hidden>
        <span className="scenario-rule-top" />
        <span className="scenario-rule-code">{scenario.code}</span>
        <span className="scenario-rule-bottom" />
      </aside>

      <div className="scenario-body">
        <header className="scenario-head">
          <span className="scenario-pill small-caps font-mono">
            {scenario.code} · {scenario.label}
          </span>
          <span className="scenario-basis font-mono">{scenario.legalBasis}</span>
        </header>

        <div className="scenario-value-wrap">
          <div className="scenario-value font-display tabular-nums">
            {fmtBRL(animated)}
          </div>
          <div className="scenario-delta small-caps">
            <span className="scenario-delta-arrow">▲</span>
            <span className="scenario-delta-pct">+{delta}%</span>
            <span className="scenario-delta-ref">sobre saldo original</span>
          </div>
        </div>

        <p className="scenario-narrative font-display italic">
          {scenario.narrative}
        </p>

        <footer className="scenario-marker">
          <span className="scenario-marker-dot" />
          <span className="small-caps font-mono text-[9px] tracking-[0.22em]">
            Cenário {idx + 1} de 3 · Tese {scenario.code}
          </span>
        </footer>
      </div>
    </article>
  );
}

function PullQuote({ text }: { text: string }) {
  const [ref, inView] = useInView<HTMLDivElement>({ threshold: 0.3 });
  return (
    <div
      ref={ref}
      className={`scenario-pullquote ${inView ? "is-visible" : ""}`}
      role="blockquote"
    >
      <span className="scenario-pullquote-mark" aria-hidden>❖</span>
      <p className="font-display italic">{text}</p>
    </div>
  );
}
