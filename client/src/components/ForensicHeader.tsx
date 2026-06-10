// Header institucional — dossier edition com selo, ornamento e tipografia editorial
import { Menu, Download, Printer, Search, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { exportCurrentSectionPDF } from "@/lib/pdfExport";
import { DensityToggle } from "@/components/DensityToggle";
import ThemeSwitcher from "@/components/ThemeSwitcher";
import FreshnessSeal from "@/components/FreshnessSeal";
import { FreshnessIndicator } from "@/components/FreshnessIndicator";

interface Props {
  onMenuClick: () => void;
  onExport: () => void;
  onExportFullPDF?: () => void;
}

export default function ForensicHeader({ onMenuClick, onExport, onExportFullPDF }: Props) {
  const handlePrint = () => exportCurrentSectionPDF();

  return (
    <header className="relative border-b border-border overflow-hidden">
      {/* camadas de atmosfera do header */}
      <div
        aria-hidden
        className="absolute inset-0 bg-gradient-to-br from-[color:var(--bg-2)] via-[color:var(--bg-2)] to-[color:var(--bg-3)]"
      />
      <div
        aria-hidden
        className="absolute inset-0 opacity-[0.18]"
        style={{
          backgroundImage:
            "radial-gradient(500px 200px at 85% -10%, color-mix(in oklch, var(--gold) 28%, transparent), transparent 60%)",
        }}
      />
      <div className="relative px-6 lg:px-8 py-6">
        <div className="flex flex-col lg:flex-row gap-6 items-start lg:items-center justify-between">
          {/* Título + metadados */}
          <div className="flex items-start gap-3 w-full lg:w-auto lg:flex-1 min-w-0">
            <Button
              variant="ghost"
              size="icon"
              onClick={onMenuClick}
              className="lg:hidden text-primary hover:bg-primary/10 shrink-0"
            >
              <Menu className="h-5 w-5" />
            </Button>
            <div className="flex-1 min-w-0">
              <div className="ornament text-[10px] mb-1.5">
                <span className="ornament-diamond" aria-hidden />
                <span className="small-caps font-mono text-[10px]">
                  Auditoria Forense v10 · Dossier Edition
                </span>
                <span className="ornament-diamond" aria-hidden />
              </div>
              <h1
                className="font-display text-[20px] sm:text-[26px] lg:text-[34px] font-semibold leading-[1.02] tracking-tight"
                style={{ fontFeatureSettings: '"liga", "dlig", "onum"' }}
              >
                DETRAN/AM
                <span className="text-[color:var(--t3)] font-normal mx-2 italic">·</span>
                <span className="text-primary italic">Dashboard de Cobrança</span>
                {/* Selo mobile inline (apenas <md) */}
                <span
                  className="audit-seal-mobile align-middle ml-2"
                  aria-label="Score Forense A+ 94,0 sobre 100"
                  title="Score Forense 12D — A+ (94,0/100)"
                >
                  A+ <span className="font-mono text-[9px] opacity-80">94,0</span>
                </span>
              </h1>
              <p className="text-[11px] text-muted-foreground mt-1.5 leading-relaxed">
                202 faturas auditadas &nbsp;·&nbsp; 481 notas de empenho &nbsp;·&nbsp; 18 contratos
                &nbsp;·&nbsp; 6 regimes jurídicos &nbsp;·&nbsp; Data-base 16/04/2026
              </p>
              <p className="text-[10px] font-mono text-[color:var(--t4)] mt-1 break-words">
                Devedor DETRAN/AM · CNPJ 04.224.028/0001-63 · Credora PRODAM · CNPJ 04.407.920/0001-80
              </p>
              <div className="mt-2 flex flex-wrap items-center gap-2">
                <FreshnessSeal />
                <FreshnessIndicator />
              </div>
              <div className="gold-line mt-3" />
            </div>
          </div>

          {/* Valor principal + selo + ações */}
          <div className="flex items-start gap-3 sm:gap-5 w-full lg:w-auto justify-between lg:justify-end flex-wrap">
            <div className="text-right">
              <div className="small-caps text-[10px] text-[color:var(--t3)] font-semibold">
                C1 Principal · SELIC
              </div>
              <div
                className="font-display text-[22px] sm:text-[26px] lg:text-[38px] font-semibold text-primary leading-[1.0] tabular-nums mt-0.5"
                style={{ fontFeatureSettings: '"onum", "tnum"' }}
              >
                R$ 28.142.624,30
              </div>
              <div className="text-[9px] uppercase tracking-[0.14em] text-[color:var(--t4)] mt-1">
                Regime Precatórios/RPV · Lei AM 2.748/2002
              </div>
            </div>

            {/* Selo de auditoria */}
            <div className="hidden md:block shrink-0">
              <div className="audit-seal">
                <span className="text-[9px] small-caps leading-none mt-2">Score</span>
                <span className="text-[20px] leading-none mt-0.5 font-semibold">A+</span>
                <span className="text-[8px] font-mono leading-none mt-1">94,0/100</span>
              </div>
            </div>

            {/* Ações */}
            <div className="flex flex-col gap-1.5 shrink-0">
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  const evt = new KeyboardEvent("keydown", { key: "k", metaKey: true, bubbles: true });
                  document.dispatchEvent(evt);
                }}
                className="h-7 px-2.5 text-[10px] border-primary/40 text-primary hover:bg-primary/10 hover:text-primary gap-1.5"
                title="Buscar (⌘K ou Ctrl+K)"
              >
                <Search className="h-3 w-3" />
                Buscar
                <kbd className="hidden sm:inline rounded border border-primary/40 bg-primary/5 px-1 text-[8px] font-mono">
                  ⌘K
                </kbd>
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={onExport}
                className="h-7 px-2.5 text-[10px] border-primary/40 text-primary hover:bg-primary/10 hover:text-primary gap-1.5"
              >
                <Download className="h-3 w-3" />
                CSV
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handlePrint}
                className="h-7 px-2.5 text-[10px] border-border text-foreground hover:bg-accent gap-1.5"
                title="Imprime apenas a seção atual"
              >
                <Printer className="h-3 w-3" />
                Imprimir
              </Button>
              {onExportFullPDF && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={onExportFullPDF}
                  className="h-7 px-2.5 text-[10px] border-primary/40 bg-primary/5 text-primary hover:bg-primary/15 gap-1.5"
                  title="Gera PDF com todas as seções"
                >
                  <FileText className="h-3 w-3" />
                  Dossiê PDF
                </Button>
              )}
              {/* Tema do dossiê: dossier / day / print */}
              <ThemeSwitcher />
              {/* Densidade: conforto/compacto/detalhado */}
              <DensityToggle className="self-end" />
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
