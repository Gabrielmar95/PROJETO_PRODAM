/**
 * EditorialHero — Sprint 3 Aspiracional A2
 *
 * Capa de revista no topo do Painel quando o usuário entra no dashboard pela
 * primeira vez ou volta ao topo. Tipografia mega (Cormorant 96-120pt),
 * ornamentos diamante, cota jurídica em itálico e CTA "Explorar o dossiê"
 * com scroll suave para a Síntese Executiva.
 *
 * Design refs: covers do New York Times Magazine, Harper's, The Atlantic.
 * Micro-interações: parallax sutil, fade-in escalonado por elemento.
 */
import { useEffect, useRef, useState } from "react";
import { ChevronDown } from "lucide-react";

interface Props {
  /** ID âncora para o CTA fazer scroll */
  ctaTargetId?: string;
  /** Métricas a exibir (opcional) */
  metrics?: {
    saldo: string;
    faturas: string;
    contratos: string;
    correcao: string;
  };
}

export default function EditorialHero({
  ctaTargetId = "executive-summary",
  metrics = {
    saldo: "R$ 21.434.211,45",
    faturas: "202",
    contratos: "18",
    correcao: "+31,9%",
  },
}: Props) {
  const rootRef = useRef<HTMLDivElement | null>(null);
  const [scrollY, setScrollY] = useState(0);

  // Parallax leve ao scroll (apenas nos primeiros 400px)
  useEffect(() => {
    const onScroll = () => {
      const y = window.scrollY;
      if (y < 500) setScrollY(y);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const handleCTA = () => {
    const target = document.getElementById(ctaTargetId);
    if (target) {
      target.scrollIntoView({ behavior: "smooth", block: "start" });
    } else {
      window.scrollBy({ top: window.innerHeight * 0.9, behavior: "smooth" });
    }
  };

  const parallaxOrnament = { transform: `translateY(${scrollY * 0.2}px)` };
  const parallaxSig = { transform: `translateY(${scrollY * 0.1}px)` };

  return (
    <section
      ref={rootRef}
      className="editorial-hero print-hide relative overflow-hidden"
      aria-label="Capa editorial do dossiê DETRAN/AM"
    >
      {/* Atmosfera: textura papel + vinheta */}
      <div aria-hidden className="editorial-hero-bg" />
      <div aria-hidden className="editorial-hero-vignette" />

      {/* Ornamento superior */}
      <div className="editorial-hero-top" style={parallaxOrnament}>
        <span className="ornament-diamond" aria-hidden />
        <span className="small-caps font-mono text-[10px] tracking-[0.28em]">
          Dossiê da Auditoria Forense
        </span>
        <span className="ornament-diamond" aria-hidden />
      </div>

      {/* Título mega */}
      <div className="editorial-hero-title">
        <div className="editorial-hero-kicker font-mono tracking-[0.20em] small-caps">
          Volume I · Edição 2026
        </div>
        <h1 className="editorial-hero-h1 font-display">
          <span className="editorial-hero-marca">DETRAN</span>
          <span className="editorial-hero-slash">/</span>
          <span className="editorial-hero-marca">AM</span>
        </h1>
        <div className="editorial-hero-tagline font-display italic">
          Dossiê de Cobrança das <span className="editorial-hero-acento">202 faturas</span>{" "}
          remanescentes
        </div>
      </div>

      {/* Ornamento e linha */}
      <div className="editorial-hero-divider" aria-hidden>
        <span>❖</span>
      </div>

      {/* Metadados editoriais */}
      <div className="editorial-hero-meta">
        <div className="editorial-hero-meta-col">
          <div className="small-caps text-[9px] tracking-[0.22em] text-[color:var(--t3)]">
            Saldo devedor principal
          </div>
          <div className="font-display text-[22px] sm:text-[26px] tabular-nums mt-1">
            {metrics.saldo}
          </div>
        </div>
        <div className="editorial-hero-meta-col">
          <div className="small-caps text-[9px] tracking-[0.22em] text-[color:var(--t3)]">
            Correção C1 SELIC
          </div>
          <div className="font-display text-[22px] sm:text-[26px] tabular-nums mt-1 text-[color:var(--gold)]">
            {metrics.correcao}
          </div>
        </div>
        <div className="editorial-hero-meta-col">
          <div className="small-caps text-[9px] tracking-[0.22em] text-[color:var(--t3)]">
            Universo auditado
          </div>
          <div className="font-display text-[22px] sm:text-[26px] tabular-nums mt-1">
            {metrics.faturas}{" "}
            <span className="text-[14px] font-normal italic text-[color:var(--t2)]">
              faturas · {metrics.contratos} contratos
            </span>
          </div>
        </div>
      </div>

      {/* Cota jurídica */}
      <blockquote className="editorial-hero-quote font-display italic">
        “A prova robusta da cadeia documental transforma a pretensão em direito
        líquido, certo e exigível — sustentando a execução forçada pelo rito do
        art. 784 do CPC e preservando a integridade do crédito público.”
      </blockquote>

      {/* Assinatura editorial */}
      <div className="editorial-hero-sig" style={parallaxSig}>
        <div className="editorial-hero-sig-line" />
        <div className="small-caps text-[10px] tracking-[0.18em] text-[color:var(--t3)]">
          Brandão Ozores Advogados Associados
        </div>
        <div className="text-[9px] font-mono text-[color:var(--t4)] mt-0.5">
          OAB/AM 15.697 · Contrato 002/2026 · Data-base 16/04/2026
        </div>
      </div>

      {/* CTA explorar */}
      <button
        onClick={handleCTA}
        className="editorial-hero-cta group"
        aria-label="Explorar o dossiê"
      >
        <span className="small-caps text-[10px] tracking-[0.3em]">
          Explorar o dossiê
        </span>
        <ChevronDown
          size={22}
          className="mt-1 animate-bounce-slow group-hover:translate-y-0.5 transition-transform"
          strokeWidth={1.4}
        />
      </button>
    </section>
  );
}
