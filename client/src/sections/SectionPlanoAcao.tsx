// SectionPlanoAcao — 5 passos táticos ordenados por prioridade
import { useAuditoria } from "@/contexts/AuditoriaContext";
import { SectionHeader } from "@/components/ForensicCard";
import { Target, Zap, Clock, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";

const priorityStyle: Record<string, { color: string; Icon: React.ComponentType<{ className?: string }> }> = {
  P1: { color: "text-red-400 border-red-400/40 bg-red-400/5", Icon: Zap },
  P2: { color: "text-amber-400 border-amber-400/40 bg-amber-400/5", Icon: Target },
  P3: { color: "text-primary border-primary/40 bg-primary/5", Icon: Clock },
  P4: { color: "text-emerald-400 border-emerald-400/40 bg-emerald-400/5", Icon: CheckCircle2 },
};

export default function SectionPlanoAcao() {
  const { planoAcao } = useAuditoria();

  return (
    <>
      <SectionHeader
        title="Plano de Ação · Próximos 90 Dias"
        desc="Roadmap tático ordenado por prioridade jurídico-financeira. P1 = crítico, P2 = alto, P3 = médio, P4 = baixo."
      />

      <div className="mt-6 space-y-3">
        {planoAcao.map((p, idx) => {
          const style = priorityStyle[p.prioridade || "P3"] || priorityStyle.P3;
          const { Icon } = style;
          return (
            <div
              key={p.id}
              className={cn(
                "border rounded p-4 flex items-start gap-4 relative",
                style.color,
              )}
            >
              <div className="flex-shrink-0 w-10 h-10 rounded-full border-2 border-current flex items-center justify-center font-display text-lg font-bold">
                {idx + 1}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <Icon className="h-4 w-4" />
                  <span className="text-[10px] font-mono tracking-wider uppercase font-bold">
                    {p.prioridade} · Passo {idx + 1} de {planoAcao.length}
                  </span>
                </div>
                <h4 className="font-display text-base font-semibold text-foreground mb-1">
                  {p.acao}
                </h4>
                <p className="text-[12px] text-muted-foreground leading-relaxed">
                  <strong className="text-foreground/90">Impacto:</strong> {p.impacto}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </>
  );
}
