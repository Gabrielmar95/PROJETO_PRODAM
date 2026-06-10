// Home — Dashboard DETRAN/AM (Design: Noturno Forense)
// Layout: sidebar fixa à esquerda + header institucional + área de seções

import { useState, useMemo, useEffect, lazy, Suspense } from "react";
import { useRoute, useLocation } from "wouter";
import Sidebar from "@/components/Sidebar";
import ForensicHeader from "@/components/ForensicHeader";
import BackToTop from "@/components/BackToTop";
import CommandPalette from "@/components/CommandPalette";
import PrintCover from "@/components/PrintCover";
import ActiveFiltersBar from "@/components/ActiveFiltersBar";
import { FilterProvider, useFilters } from "@/contexts/FilterContext";
import { DashboardProvider } from "@/contexts/DashboardContext";
import { AuditoriaProvider } from "@/contexts/AuditoriaContext";
import { DensityProvider } from "@/contexts/DensityContext";
import { DossierThemeProvider } from "@/contexts/DossierThemeContext";
import { exportFaturas } from "@/lib/export";
import { exportFullDossiePDF } from "@/lib/pdfExport";
import { NAV_SECTIONS } from "@/data/types";
import { toast } from "sonner";
import { useGlobalShortcuts } from "@/hooks/useGlobalShortcuts";

// SectionPainel é eager (default landing) para evitar flash de loading inicial.
// Demais 24 seções viram chunks separados via React.lazy (S4-M01).
import SectionPainel from "@/sections/SectionPainel";

const SectionCenarios = lazy(() => import("@/sections/SectionCenarios"));
const SectionScore = lazy(() => import("@/sections/SectionScore"));
const SectionFaturasTodas = lazy(
  () => import("@/sections/SectionFaturasTodas")
);
const SectionFaturasContrato = lazy(
  () => import("@/sections/SectionFaturasContrato")
);
const SectionFaturasRegime = lazy(
  () => import("@/sections/SectionFaturasRegime")
);
const SectionFaturasAno = lazy(() => import("@/sections/SectionFaturasAno"));
const SectionDecomposicao = lazy(
  () => import("@/sections/SectionDecomposicao")
);
const SectionFaturasDetalhadas = lazy(
  () => import("@/sections/SectionFaturasDetalhadas")
);
const SectionContratosTodos = lazy(
  () => import("@/sections/SectionContratosTodos")
);
const SectionContratosDetalhe = lazy(
  () => import("@/sections/SectionContratosDetalhe")
);
const SectionCadeia = lazy(() => import("@/sections/SectionCadeia"));
const SectionEmpenhos = lazy(() => import("@/sections/SectionEmpenhos"));
const SectionCobrancas = lazy(() => import("@/sections/SectionCobrancas"));
const SectionMarcos = lazy(() => import("@/sections/SectionMarcos"));
const SectionInventario = lazy(() => import("@/sections/SectionInventario"));
const SectionCorrecaoGeral = lazy(
  () => import("@/sections/SectionCorrecaoGeral")
);
const SectionJuridico = lazy(() => import("@/sections/SectionJuridico"));
const SectionPrescricao = lazy(() => import("@/sections/SectionPrescricao"));
const SectionRPV = lazy(() => import("@/sections/SectionRPV"));
const SectionRisco = lazy(() => import("@/sections/SectionRisco"));
const SectionPlanoAcao = lazy(() => import("@/sections/SectionPlanoAcao"));
const SectionHonorarios = lazy(() => import("@/sections/SectionHonorarios"));
const SectionProntuario = lazy(() => import("@/sections/SectionProntuario"));
const SectionAdmin = lazy(() => import("@/sections/SectionAdmin"));

function SectionFallback() {
  return (
    <div className="flex items-center justify-center py-24 text-muted-foreground text-sm font-mono">
      <div className="animate-pulse">Carregando seção…</div>
    </div>
  );
}

function HomeInner() {
  // S3-M02: estado da seção ativa sincronizado com 3 fontes (em ordem de prioridade):
  //   1. URL /secao/:id (canonical, compartilhavel, navegação do browser)
  //   2. Hash legado #painel (backward-compat com bookmarks anteriores)
  //   3. fallback "painel"
  const [matchSecao, paramsSecao] = useRoute<{ id: string }>("/secao/:id");
  const [, navigate] = useLocation();

  const [active, setActive] = useState<string>(() => {
    if (matchSecao && paramsSecao?.id) return paramsSecao.id;
    const hash = window.location.hash.replace("#", "");
    return hash || "painel";
  });
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { filteredFaturas } = useFilters();

  // Sync URL canonical /secao/:id quando active mudar via UI
  useEffect(() => {
    const target = `/secao/${active}`;
    if (window.location.pathname !== target) {
      navigate(target, { replace: false });
    }
    // limpa hash antigo (#painel) pois agora a verdade é o pathname
    if (window.location.hash) {
      // history.replaceState evita scroll-jump
      window.history.replaceState(
        null,
        "",
        window.location.pathname + window.location.search
      );
    }
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, [active, navigate]);

  // Captura mudanças de URL via back/forward do browser
  useEffect(() => {
    if (matchSecao && paramsSecao?.id && paramsSecao.id !== active) {
      setActive(paramsSecao.id);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [matchSecao, paramsSecao?.id]);

  // Backward-compat: hash antigo #painel continua aceito
  useEffect(() => {
    const onHash = () => {
      const h = window.location.hash.replace("#", "");
      if (h && h !== active) setActive(h);
    };
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleExport = () => {
    exportFaturas(filteredFaturas, active);
    toast.success(`Exportado: ${filteredFaturas.length} faturas em CSV`, {
      description: "Arquivo salvo em Downloads",
    });
  };

  // S3-M13: Atalhos globais Alt+D / Alt+E / Alt+P
  useGlobalShortcuts({
    onExport: handleExport,
    onPrint: () => window.print(),
  });

  const handleFullPDF = () => {
    // Seleciona seuções principais do dossiê (não repete as de análise granular)
    const priorityIds = [
      "painel",
      "cenarios",
      "score",
      "faturas_regime",
      "faturas_ano",
      "contratos_todos",
      "cadeia",
      "marcos",
      "prescricao",
      "rpv",
      "risco",
      "plano_acao",
      "honorarios",
    ];
    const allItems = NAV_SECTIONS.flatMap(g => g.items);
    const sections = priorityIds
      .map(id => {
        const it = allItems.find(x => x.id === id);
        return it ? { id: it.id, label: it.label } : null;
      })
      .filter((x): x is { id: string; label: string } => x !== null);
    const originalActive = active;
    exportFullDossiePDF(sections, setActive).finally(() => {
      setActive(originalActive);
    });
  };

  const CurrentSection = useMemo(() => {
    const map: Record<string, React.ReactNode> = {
      painel: <SectionPainel />,
      cenarios: <SectionCenarios />,
      score: <SectionScore />,
      faturas_todas: <SectionFaturasTodas />,
      faturas_contrato: <SectionFaturasContrato />,
      faturas_regime: <SectionFaturasRegime />,
      faturas_ano: <SectionFaturasAno />,
      decomposicao: <SectionDecomposicao />,
      faturas_detalhadas: <SectionFaturasDetalhadas />,
      contratos_todos: <SectionContratosTodos />,
      contratos_detalhe: <SectionContratosDetalhe />,
      cadeia: <SectionCadeia />,
      empenhos: <SectionEmpenhos />,
      cobrancas: <SectionCobrancas />,
      marcos: <SectionMarcos />,
      inventario: <SectionInventario />,
      correcao_geral: <SectionCorrecaoGeral />,
      juridico: <SectionJuridico />,
      prescricao: <SectionPrescricao />,
      rpv: <SectionRPV />,
      risco: <SectionRisco />,
      plano_acao: <SectionPlanoAcao />,
      honorarios: <SectionHonorarios />,
      prontuario: <SectionProntuario />,
      admin: <SectionAdmin />,
    };
    return map[active] || <SectionPainel />;
  }, [active]);

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Sidebar
        active={active}
        onSelect={setActive}
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <div className="lg:ml-[260px]">
        <ForensicHeader
          onMenuClick={() => setSidebarOpen(true)}
          onExport={handleExport}
          onExportFullPDF={handleFullPDF}
        />
        <main className="px-5 py-6 lg:px-8 lg:py-8">
          <PrintCover />
          <ActiveFiltersBar />
          <div key={active} className="anim-fadein">
            <Suspense fallback={<SectionFallback />}>{CurrentSection}</Suspense>
          </div>
        </main>
        <footer className="px-6 lg:px-8 py-8 text-center border-t border-border mt-10">
          <div className="caligraphic-divider">❖</div>
          <p className="font-display italic text-[13px] text-[color:var(--t2)] mb-3 leading-relaxed max-w-2xl mx-auto">
            “A prova robusta da cadeia documental transforma a pretensão em
            direito líquido, certo e exigível.”
          </p>
          <p className="small-caps text-[10px] text-muted-foreground tracking-[0.18em]">
            Brandão Ozores Advogados Associados · OAB/AM 15.697 · Contrato
            002/2026
          </p>
          <p className="text-[10px] font-mono text-muted-foreground/60 mt-1.5">
            Dashboard DETRAN/AM · Auditoria Forense v10 · Score 94,0/100 A+ ·
            Data-base 16/04/2026
          </p>
        </footer>
      </div>
      <BackToTop />
      <CommandPalette onSelect={setActive} />
    </div>
  );
}

export default function Home() {
  return (
    <DossierThemeProvider>
      <DensityProvider>
        <DashboardProvider>
          <AuditoriaProvider>
            <FilterProvider>
              <HomeInner />
            </FilterProvider>
          </AuditoriaProvider>
        </DashboardProvider>
      </DensityProvider>
    </DossierThemeProvider>
  );
}
