// Design: Noturno Forense — Sidebar institucional fixa
// Mantém hierarquia de navegação original do dashboard HTML.

import { useRef } from "react";
import { NAV_SECTIONS } from "@/data/types";
import { cn } from "@/lib/utils";
import {
  Scale, FileText, FolderOpen, TrendingUp, Gavel, Receipt, LayoutDashboard,
  Clock, AlertTriangle, Calculator, Library, Award, Banknote, Mail,
  ShieldCheck, Link2, Target, Archive, ClipboardList, Edit3,
} from "lucide-react";

const iconFor: Record<string, React.ReactNode> = {
  painel: <LayoutDashboard className="h-3.5 w-3.5" />,
  cenarios: <TrendingUp className="h-3.5 w-3.5" />,
  score: <Award className="h-3.5 w-3.5" />,
  faturas_todas: <FileText className="h-3.5 w-3.5" />,
  faturas_contrato: <FolderOpen className="h-3.5 w-3.5" />,
  faturas_regime: <Library className="h-3.5 w-3.5" />,
  faturas_ano: <Clock className="h-3.5 w-3.5" />,
  decomposicao: <Calculator className="h-3.5 w-3.5" />,
  faturas_detalhadas: <ClipboardList className="h-3.5 w-3.5" />,
  contratos_todos: <FolderOpen className="h-3.5 w-3.5" />,
  contratos_detalhe: <FileText className="h-3.5 w-3.5" />,
  cadeia: <Link2 className="h-3.5 w-3.5" />,
  empenhos: <Banknote className="h-3.5 w-3.5" />,
  cobrancas: <Mail className="h-3.5 w-3.5" />,
  marcos: <ShieldCheck className="h-3.5 w-3.5" />,
  inventario: <Archive className="h-3.5 w-3.5" />,
  correcao_geral: <TrendingUp className="h-3.5 w-3.5" />,
  juridico: <Gavel className="h-3.5 w-3.5" />,
  prescricao: <Clock className="h-3.5 w-3.5" />,
  rpv: <Scale className="h-3.5 w-3.5" />,
  risco: <AlertTriangle className="h-3.5 w-3.5" />,
  plano_acao: <Target className="h-3.5 w-3.5" />,
  honorarios: <Receipt className="h-3.5 w-3.5" />,
  prontuario: <Gavel className="h-3.5 w-3.5" />,
  admin: <Edit3 className="h-3.5 w-3.5" />,
};

interface Props {
  active: string;
  onSelect: (id: string) => void;
  open: boolean;
  onClose: () => void;
}

export default function Sidebar({ active, onSelect, open, onClose }: Props) {
  // Swipe gesture: close sidebar on left-swipe (mobile)
  const touchStartX = useRef<number | null>(null);
  const touchStartY = useRef<number | null>(null);

  const onTouchStart = (e: React.TouchEvent) => {
    touchStartX.current = e.touches[0].clientX;
    touchStartY.current = e.touches[0].clientY;
  };

  const onTouchEnd = (e: React.TouchEvent) => {
    if (touchStartX.current === null || touchStartY.current === null) return;
    const endX = e.changedTouches[0].clientX;
    const endY = e.changedTouches[0].clientY;
    const deltaX = endX - touchStartX.current;
    const deltaY = endY - touchStartY.current;
    // Swipe left detected (deltaX < -60 e movimento horizontal predominante)
    if (deltaX < -60 && Math.abs(deltaX) > Math.abs(deltaY) * 1.5) {
      onClose();
    }
    touchStartX.current = null;
    touchStartY.current = null;
  };

  return (
    <>
      {/* Backdrop mobile */}
      {open && (
        <div
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      <aside
        onTouchStart={onTouchStart}
        onTouchEnd={onTouchEnd}
        className={cn(
          "fixed left-0 top-0 bottom-0 w-[260px] bg-sidebar border-r border-sidebar-border z-50 overflow-y-auto flex flex-col",
          "transition-transform duration-300 ease-out",
          "lg:translate-x-0",
          open ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {/* Logo */}
        <div className="relative px-4 pt-7 pb-5 border-b border-sidebar-border text-center">
          <div className="ornament text-[10px] mb-2 justify-center flex">
            <span className="ornament-diamond" aria-hidden />
          </div>
          <div
            className="font-display text-[18px] font-semibold tracking-[0.05em] text-primary italic leading-tight"
            style={{ fontFeatureSettings: '"liga", "dlig"' }}
          >
            Brandão Ozores
          </div>
          <div className="small-caps text-[9px] text-muted-foreground mt-0.5 tracking-[0.22em]">
            Advogados Associados
          </div>
          <div className="text-[9px] font-mono text-primary/60 mt-2.5 tracking-[0.18em]">
            AUDITORIA v10 · DOSSIER
          </div>
          <div className="mt-3 inline-block px-3 py-1 border border-primary/50 rounded bg-primary/10 text-[10px] font-semibold tracking-wider text-primary tabular-nums">
            202 FATURAS · 481 NEs · A+
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 py-2">
          {NAV_SECTIONS.map((group) => (
            <div key={group.group} className="mb-2">
              <div className="px-4 pt-3.5 pb-1.5 small-caps text-[10px] font-semibold text-[color:var(--gold-d)] flex items-center gap-2">
                <span className="w-1 h-1 bg-primary/60 rotate-45" aria-hidden />
                {group.group}
              </div>
              {group.items.map((item) => {
                const isActive = active === item.section;
                return (
                  <button
                    key={item.id}
                    onClick={() => {
                      onSelect(item.section);
                      onClose();
                    }}
                    className={cn(
                      "w-full flex items-center gap-2 px-4 py-2.5 lg:py-2 text-[11.5px] lg:text-[11px] text-left transition-all border-l-[3px] min-h-[40px] lg:min-h-0",
                      isActive
                        ? "bg-sidebar-accent text-primary font-semibold border-primary"
                        : "text-[color:var(--t3)] border-transparent hover:bg-sidebar-accent/60 hover:text-foreground hover:border-primary/40 active:bg-sidebar-accent/80"
                    )}
                  >
                    <span className="w-4 flex items-center justify-center text-primary/70">
                      {iconFor[item.id] || <FileText className="h-3.5 w-3.5" />}
                    </span>
                    <span className="flex-1 truncate">{item.label}</span>
                    {item.badge && (
                      <span className="text-[8px] font-bold tracking-wider px-1.5 py-0.5 rounded bg-primary/15 text-primary">
                        {item.badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          ))}
        </nav>

        {/* Footer */}
        <div className="px-4 py-4 border-t border-sidebar-border text-center">
          <div className="gold-line mx-auto mb-2" />
          <div className="small-caps text-[9px] text-muted-foreground tracking-[0.14em]">
            Contrato 002/2026 · OAB/AM 15.697
          </div>
          <div className="text-[9px] font-mono text-muted-foreground/60 mt-1">
            Data-base 16/04/2026
          </div>
        </div>
      </aside>
    </>
  );
}
