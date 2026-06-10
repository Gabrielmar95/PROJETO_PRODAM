// Prontuário de Execução — DETRAN/AM × PRODAM
// Consolidação executável dos drill-downs D2, D4, D5, D6 e SOMBRA.
// Cada card é uma ficha por contrato com: via processual, prontidão, docs em mãos,
// docs faltantes, prescrição fatal, valor exequível, honorários estimados.

import { useState, useMemo } from "react";
import { dashboard, fmtBRL } from "@/data/helpers";
import { SectionHeader, ForensicCard } from "@/components/ForensicCard";
import { KpiGrid } from "@/components/KpiCard";
import { ForensicTable } from "@/components/ForensicTable";
import { cn } from "@/lib/utils";
import {
  Scale,
  FileText,
  ChevronDown,
  ChevronRight,
  CheckCircle2,
  AlertTriangle,
  FileSearch,
  FilePlus,
  MapPin,
  Clock,
  Gavel,
  Banknote,
  ShieldAlert,
  BookOpen,
} from "lucide-react";

interface ContratoProntuario {
  numero: string;
  numero_oficial: string;
  objeto: string;
  classe: string;
  badge: string | null;
  regime: string | null;
  clausula_correcao: string;
  fundamentacao_juridica: string;
  pdf_contrato_disponivel: boolean;
  pdf_path: string | null;
  qtd_faturas: number;
  qtd_faturas_prescritas: number;
  saldo_bruto_nominal: number;
  valor_atualizado_total: number;
  valor_prescrito: number;
  valor_exequivel_atualizado: number;
  multa_computada: number;
  correcao_monetaria: number;
  juros_mora: number;
  honorarios_estim_20pct: number;
  venc_menor: string | null;
  venc_maior: string | null;
  prescr_fatal: string | null;
  status_prescr_fatal: string | null;
  via_processual_recomendada: string;
  juizo_competente: string;
  prontidao_execucao: string;
  fundamentos_executivos: string[];
  documentos_em_maos: Record<string, number>;
  documentos_faltantes: string[];
  custas_estim_2pct: number;
  nota_multa: string;
  nes_spcf?: {
    qtd: number | null;
    classe?: string;
    exemplos?: Array<{ ne: string; contrato_ref: string; valor: number; situacao: string; data: string | null }>;
    observacao: string;
  };
}

const PRONTIDAO_META: Record<
  string,
  { label: string; tone: string; icon: React.ReactNode; ordem: number }
> = {
  PRONTO: {
    label: "PRONTO — execução imediata",
    tone: "ok",
    icon: <CheckCircle2 className="h-4 w-4" />,
    ordem: 1,
  },
  PROVA_SUPLEMENTAR: {
    label: "PROVA SUPLEMENTAR",
    tone: "warn",
    icon: <FileSearch className="h-4 w-4" />,
    ordem: 2,
  },
  REVISAR_FUNDAMENTO_MULTA: {
    label: "REVISAR FUNDAMENTO (multa)",
    tone: "warn",
    icon: <Scale className="h-4 w-4" />,
    ordem: 3,
  },
  RASTREIO_DOCUMENTAL: {
    label: "RASTREIO DOCUMENTAL",
    tone: "err",
    icon: <AlertTriangle className="h-4 w-4" />,
    ordem: 4,
  },
  INDEFINIDO: {
    label: "INDEFINIDO",
    tone: "info",
    icon: <FileText className="h-4 w-4" />,
    ordem: 5,
  },
};

function toneClasses(tone: string) {
  switch (tone) {
    case "ok":
      return "bg-emerald-500/15 text-emerald-400 border-emerald-500/40";
    case "warn":
      return "bg-amber-500/15 text-amber-400 border-amber-500/40";
    case "err":
      return "bg-red-500/15 text-red-400 border-red-500/40";
    case "info":
      return "bg-blue-500/15 text-blue-400 border-blue-500/40";
    default:
      return "bg-primary/10 text-primary border-primary/30";
  }
}

function PrescricaoBadge({ status }: { status: string | null }) {
  const safe = status || "SEM_DATA";
  let tone = "info";
  if (safe.includes("PRESCRITA")) tone = "err";
  else if (safe.includes("CRÍTICO")) tone = "err";
  else if (safe.includes("ATENÇÃO")) tone = "warn";
  else if (safe.includes("VIGENTE")) tone = "ok";
  return (
    <span
      className={cn(
        "text-[10px] font-mono font-semibold px-2 py-0.5 rounded border uppercase tracking-wider",
        toneClasses(tone),
      )}
    >
      {status}
    </span>
  );
}

function DocsInline({ docs }: { docs: Record<string, number> }) {
  const entries = Object.entries(docs).filter(([, v]) => v > 0);
  if (!entries.length)
    return (
      <span className="text-[11px] italic text-muted-foreground">
        Nenhum documento físico vinculado no pendrive auditado
      </span>
    );
  return (
    <div className="flex flex-wrap gap-1.5">
      {entries.map(([k, v]) => (
        <span
          key={k}
          className="text-[10.5px] font-mono tabular-nums px-2 py-0.5 rounded border border-primary/30 bg-primary/5 text-[color:var(--t2)]"
        >
          {k.replaceAll("_", " ")}
          <strong className="ml-1 text-primary">{v}</strong>
        </span>
      ))}
    </div>
  );
}

function ContratoFicha({ c, open, onToggle }: { c: ContratoProntuario; open: boolean; onToggle: () => void }) {
  const pr = PRONTIDAO_META[c.prontidao_execucao] || PRONTIDAO_META.INDEFINIDO;

  return (
    <div className="forensic-card lift-on-hover border border-border p-0 overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full text-left px-4 py-3.5 flex items-start gap-3 hover:bg-primary/5 transition-colors"
      >
        <span className="mt-0.5 flex-shrink-0 text-primary/70">
          {open ? (
            <ChevronDown className="h-4 w-4" />
          ) : (
            <ChevronRight className="h-4 w-4" />
          )}
        </span>

        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2 mb-1.5">
            <span className="font-display font-semibold text-[14.5px] text-primary tracking-tight">
              Contrato {c.numero_oficial}
            </span>
            <span
              className={cn(
                "text-[9.5px] font-mono font-bold px-2 py-0.5 rounded-full border tracking-wider uppercase flex items-center gap-1",
                toneClasses(pr.tone),
              )}
            >
              {pr.icon}
              {pr.label}
            </span>
            <PrescricaoBadge status={c.status_prescr_fatal} />
          </div>
          <div className="text-[11.5px] text-[color:var(--t2)] leading-relaxed truncate">
            {c.objeto || "(objeto não informado)"}
          </div>
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-1.5 text-[10.5px] font-mono text-muted-foreground">
            <span>
              <strong className="text-primary">{c.qtd_faturas}</strong> fat.
            </span>
            <span>
              Bruto <strong className="text-foreground">{fmtBRL(c.saldo_bruto_nominal)}</strong>
            </span>
            <span className="text-emerald-400">
              Exequível <strong>{fmtBRL(c.valor_exequivel_atualizado)}</strong>
            </span>
            <span>
              Honorários 20%{" "}
              <strong className="text-primary">{fmtBRL(c.honorarios_estim_20pct)}</strong>
            </span>
          </div>
        </div>
      </button>

      {open && (
        <div className="border-t border-border px-4 py-4 space-y-4 bg-background/40">
          {/* Via processual */}
          <div>
            <div className="small-caps text-[10px] font-semibold text-primary tracking-[0.18em] mb-1.5 flex items-center gap-1.5">
              <Gavel className="h-3 w-3" />
              Via processual recomendada
            </div>
            <div className="text-[12px] text-foreground leading-relaxed">
              {c.via_processual_recomendada}
            </div>
            <div className="text-[10.5px] font-mono text-muted-foreground mt-1 flex items-start gap-1">
              <MapPin className="h-3 w-3 mt-0.5 flex-shrink-0" />
              {c.juizo_competente}
            </div>
          </div>

          {/* Prazo prescricional */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-[10.5px] font-mono">
            <div>
              <div className="small-caps text-muted-foreground tracking-wider mb-0.5">Prescrição fatal</div>
              <div className="text-foreground font-semibold flex items-center gap-1">
                <Clock className="h-3 w-3 text-primary/70" />
                {c.prescr_fatal ?? "N/D"}
              </div>
            </div>
            <div>
              <div className="small-caps text-muted-foreground tracking-wider mb-0.5">Vencimento mais antigo</div>
              <div className="text-foreground">{c.venc_menor ?? "N/D"}</div>
            </div>
            <div>
              <div className="small-caps text-muted-foreground tracking-wider mb-0.5">Vencimento mais recente</div>
              <div className="text-foreground">{c.venc_maior ?? "N/D"}</div>
            </div>
            <div>
              <div className="small-caps text-muted-foreground tracking-wider mb-0.5">Faturas prescritas</div>
              <div className="text-foreground">
                {c.qtd_faturas_prescritas} <span className="text-muted-foreground">(R$ {c.valor_prescrito.toLocaleString("pt-BR")})</span>
              </div>
            </div>
          </div>

          {/* Composição do valor */}
          <div>
            <div className="small-caps text-[10px] font-semibold text-primary tracking-[0.18em] mb-1.5 flex items-center gap-1.5">
              <Banknote className="h-3 w-3" />
              Composição do valor exequível
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-[11px]">
              <div className="rounded border border-primary/20 bg-primary/5 p-2">
                <div className="text-[9.5px] uppercase text-muted-foreground tracking-wider">Saldo bruto</div>
                <div className="font-mono tabular-nums text-foreground">{fmtBRL(c.saldo_bruto_nominal)}</div>
              </div>
              <div className="rounded border border-primary/20 bg-primary/5 p-2">
                <div className="text-[9.5px] uppercase text-muted-foreground tracking-wider">Correção monetária</div>
                <div className="font-mono tabular-nums text-foreground">{fmtBRL(c.correcao_monetaria)}</div>
              </div>
              <div className="rounded border border-primary/20 bg-primary/5 p-2">
                <div className="text-[9.5px] uppercase text-muted-foreground tracking-wider">Juros de mora</div>
                <div className="font-mono tabular-nums text-foreground">{fmtBRL(c.juros_mora)}</div>
              </div>
              <div className="rounded border border-amber-500/30 bg-amber-500/5 p-2">
                <div className="text-[9.5px] uppercase text-amber-400 tracking-wider">Multa 2%</div>
                <div className="font-mono tabular-nums text-foreground">{fmtBRL(c.multa_computada)}</div>
              </div>
              <div className="rounded border border-emerald-500/30 bg-emerald-500/5 p-2 col-span-2 md:col-span-2">
                <div className="text-[9.5px] uppercase text-emerald-400 tracking-wider">Valor exequível atualizado</div>
                <div className="font-mono tabular-nums text-foreground text-[13px] font-semibold">
                  {fmtBRL(c.valor_exequivel_atualizado)}
                </div>
              </div>
              <div className="rounded border border-primary/30 bg-primary/5 p-2">
                <div className="text-[9.5px] uppercase text-primary tracking-wider">Honorários 20%</div>
                <div className="font-mono tabular-nums text-foreground">{fmtBRL(c.honorarios_estim_20pct)}</div>
              </div>
              <div className="rounded border border-muted-foreground/30 bg-muted-foreground/5 p-2">
                <div className="text-[9.5px] uppercase text-muted-foreground tracking-wider">Custas estimadas 2%</div>
                <div className="font-mono tabular-nums text-foreground">{fmtBRL(c.custas_estim_2pct)}</div>
              </div>
            </div>
            <div className="text-[10.5px] italic text-muted-foreground mt-2 flex items-start gap-1">
              <BookOpen className="h-3 w-3 mt-0.5 flex-shrink-0" />
              {c.nota_multa}
            </div>
          </div>

          {/* Fundamentos */}
          {c.fundamentos_executivos.length > 0 && (
            <div>
              <div className="small-caps text-[10px] font-semibold text-primary tracking-[0.18em] mb-1.5 flex items-center gap-1.5">
                <ShieldAlert className="h-3 w-3" />
                Fundamentos para a petição inicial
              </div>
              <ul className="text-[11.5px] text-foreground space-y-1 list-disc list-inside">
                {c.fundamentos_executivos.map((f, i) => (
                  <li key={i}>{f}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Documentos em mãos */}
          <div>
            <div className="small-caps text-[10px] font-semibold text-primary tracking-[0.18em] mb-1.5 flex items-center gap-1.5">
              <FileText className="h-3 w-3" />
              Documentos em mãos (pendrive auditado)
            </div>
            <DocsInline docs={c.documentos_em_maos} />
          </div>

          {/* NEs SPCF (cruzamento oficial DETRAN/AM) */}
          {c.nes_spcf && c.nes_spcf.qtd !== null && (
            <div>
              <div className="small-caps text-[10px] font-semibold text-primary tracking-[0.18em] mb-1.5 flex items-center gap-1.5">
                <ShieldAlert className="h-3 w-3" />
                Cruzamento SPCF — Notas de Empenho DETRAN/AM
              </div>
              <div className={cn(
                "rounded border p-2.5 text-[11px] space-y-1.5",
                c.nes_spcf.qtd! > 0 ? "border-emerald-500/30 bg-emerald-500/5" : "border-red-500/30 bg-red-500/5"
              )}>
                <div className="font-mono text-[10.5px]">
                  <strong className={c.nes_spcf.qtd! > 0 ? "text-emerald-400" : "text-red-400"}>
                    {c.nes_spcf.qtd} NE{c.nes_spcf.qtd === 1 ? "" : "s"} localizada{c.nes_spcf.qtd === 1 ? "" : "s"}
                  </strong>
                  {c.nes_spcf.classe && <span className="ml-2 text-muted-foreground">({c.nes_spcf.classe})</span>}
                </div>
                {c.nes_spcf.exemplos && c.nes_spcf.exemplos.length > 0 && (
                  <ul className="text-[10.5px] font-mono text-foreground space-y-0.5">
                    {c.nes_spcf.exemplos.map((ex, i) => (
                      <li key={i} className="pl-2 border-l-2 border-primary/30">
                        <strong>NE {ex.ne}</strong> · ref={ex.contrato_ref} · {fmtBRL(ex.valor)} · {ex.situacao}
                      </li>
                    ))}
                  </ul>
                )}
                <div className="text-[10.5px] italic text-muted-foreground leading-relaxed">
                  {c.nes_spcf.observacao}
                </div>
              </div>
            </div>
          )}

          {/* Documentos faltantes */}
          {c.documentos_faltantes.length > 0 && (
            <div>
              <div className="small-caps text-[10px] font-semibold text-amber-400 tracking-[0.18em] mb-1.5 flex items-center gap-1.5">
                <FilePlus className="h-3 w-3" />
                Ações e documentos faltantes
              </div>
              <ul className="text-[11.5px] text-foreground space-y-1 list-disc list-inside">
                {c.documentos_faltantes.map((f, i) => (
                  <li key={i}>{f}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Metadados */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-x-4 gap-y-1 text-[10.5px] font-mono text-muted-foreground pt-2 border-t border-border/50">
            <span><span className="text-muted-foreground/70">Classe:</span> {c.classe}</span>
            <span><span className="text-muted-foreground/70">Regime:</span> {c.regime || "N/D"}</span>
            <span><span className="text-muted-foreground/70">PDF:</span> {c.pdf_contrato_disponivel ? "Disponível" : "Pendente"}</span>
            <span className="md:col-span-3"><span className="text-muted-foreground/70">Cláusula correção:</span> {c.clausula_correcao || "AUSENTE"}</span>
            <span className="md:col-span-3"><span className="text-muted-foreground/70">Fundamentação:</span> {c.fundamentacao_juridica || "—"}</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default function SectionProntuario() {
  const sec = dashboard.prontuario;
  const [openMap, setOpenMap] = useState<Record<string, boolean>>({});
  const [filtroProntidao, setFiltroProntidao] = useState<string>("");
  const [busca, setBusca] = useState("");

  // Os cards vêm com .text = JSON serializado do contrato completo
  const contratos: ContratoProntuario[] = useMemo(() => {
    return (sec.cards || [])
      .map((card) => {
        try {
          return JSON.parse(card.text) as ContratoProntuario;
        } catch {
          return null;
        }
      })
      .filter((x): x is ContratoProntuario => x !== null);
  }, [sec.cards]);

  const filtrados = useMemo(() => {
    const q = busca.trim().toLowerCase();
    return contratos
      .filter((c) => !filtroProntidao || c.prontidao_execucao === filtroProntidao)
      .filter((c) =>
        !q ||
        c.numero_oficial.toLowerCase().includes(q) ||
        c.objeto.toLowerCase().includes(q) ||
        c.via_processual_recomendada.toLowerCase().includes(q),
      )
      .sort((a, b) => {
        const oa = PRONTIDAO_META[a.prontidao_execucao]?.ordem ?? 99;
        const ob = PRONTIDAO_META[b.prontidao_execucao]?.ordem ?? 99;
        if (oa !== ob) return oa - ob;
        return b.valor_exequivel_atualizado - a.valor_exequivel_atualizado;
      });
  }, [contratos, filtroProntidao, busca]);

  const resumoPorProntidao = useMemo(() => {
    const m = new Map<string, { qtd: number; valor: number }>();
    for (const c of contratos) {
      const k = c.prontidao_execucao;
      const cur = m.get(k) || { qtd: 0, valor: 0 };
      cur.qtd += 1;
      cur.valor += c.valor_exequivel_atualizado;
      m.set(k, cur);
    }
    return Array.from(m.entries()).sort((a, b) => b[1].valor - a[1].valor);
  }, [contratos]);

  return (
    <div className="space-y-5">
      <SectionHeader title={sec.title} desc={sec.desc} />
      <KpiGrid kpis={sec.kpis} />

      {/* Filtros */}
      <div className="flex flex-wrap gap-2 items-center">
        <span className="text-[11px] small-caps text-muted-foreground mr-2">Prontidão:</span>
        <button
          onClick={() => setFiltroProntidao("")}
          className={cn(
            "text-[10.5px] font-mono px-2.5 py-1 rounded-full border transition-colors",
            !filtroProntidao
              ? "bg-primary/20 border-primary text-primary"
              : "border-border text-muted-foreground hover:border-primary/50",
          )}
        >
          Todos ({contratos.length})
        </button>
        {resumoPorProntidao.map(([k, v]) => {
          const meta = PRONTIDAO_META[k] || PRONTIDAO_META.INDEFINIDO;
          return (
            <button
              key={k}
              onClick={() => setFiltroProntidao(filtroProntidao === k ? "" : k)}
              className={cn(
                "text-[10.5px] font-mono px-2.5 py-1 rounded-full border transition-colors flex items-center gap-1",
                filtroProntidao === k
                  ? toneClasses(meta.tone)
                  : "border-border text-muted-foreground hover:border-primary/50",
              )}
            >
              {meta.label} <strong>({v.qtd})</strong>
            </button>
          );
        })}
        <input
          type="search"
          value={busca}
          onChange={(e) => setBusca(e.target.value)}
          placeholder="Buscar por nº, objeto ou via..."
          className="ml-auto text-[11.5px] px-3 py-1.5 rounded border border-border bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:border-primary w-full sm:w-64"
        />
      </div>

      {/* Lista expansível */}
      <div className="space-y-2">
        {filtrados.map((c) => (
          <ContratoFicha
            key={c.numero_oficial}
            c={c}
            open={!!openMap[c.numero_oficial]}
            onToggle={() =>
              setOpenMap((prev) => ({ ...prev, [c.numero_oficial]: !prev[c.numero_oficial] }))
            }
          />
        ))}
      </div>

      {/* Tabela resumo */}
      {sec.tables?.[0] && (
        <ForensicCard title="Resumo por prontidão executória" variant="highlight">
          <ForensicTable table={sec.tables[0]} />
        </ForensicCard>
      )}
    </div>
  );
}
