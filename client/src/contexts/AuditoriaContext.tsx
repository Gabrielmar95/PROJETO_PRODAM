// AuditoriaContext — carrega dados da auditoria completa (v11) via tRPC
// NEs, Cobranças, Marcos, Score 12D, Plano Ação, Cadeia, Inventário, Faturas+
import { createContext, useContext, ReactNode } from "react";
import { trpc } from "@/lib/trpc";
import { Loader2 } from "lucide-react";

export type ScoreDimensao = {
  id: number;
  dimensao: string;
  pesoPct: string | null;
  score: string | null;
  contribuicao: string | null;
  detalhes: unknown;
  ordem: number;
};

export type NotaEmpenho = {
  id: number;
  numero: string;
  contrato: string | null;
  valor: string | null;
  fonteAfi: string | null;
  dataEmissao: string | null;
  descricao: string | null;
  situacao: string | null;
  orgaoAfi: string | null;
  link: string | null;
};

export type Cobranca = {
  id: number;
  numero: string;
  contrato: string | null;
  competencia: string | null;
  servicos: string | null;
  valor: string | null;
  diasAtraso: number | null;
  valorCorrigido: string | null;
  status: string | null;
  url: string | null;
};

export type MarcoInterruptivo = {
  id: number;
  ne: string;
  ano: string | null;
  prescricao: string | null;
  cadeia: string | null;
  valor: string | null;
  dataUltima: string | null;
  docs: number | null;
};

export type PlanoAcao = {
  id: number;
  prioridade: string | null;
  acao: string | null;
  impacto: string | null;
  ordem: number;
};

export type CadeiaContrato = {
  id: number;
  contrato: string;
  ano: string | null;
  cadeia: string | null;
  nes: number | null;
  nls: number | null;
  nfs: number | null;
  aceites: number | null;
  docs: number | null;
  primeira: string | null;
  ultima: string | null;
};

export type InventarioDoc = {
  id: number;
  arquivo: string;
  tamanhoMb: string | null;
  chars: number | null;
  precisouOcr: string | null;
  tipoNovo: string | null;
  qualidadeOcr: string | null;
  nes: string | null;
  nls: string | null;
  nfs: string | null;
};

export type FaturaDetalhada = {
  id: number;
  nf: string;
  contrato: string | null;
  competencia: string | null;
  dataVencimento: string | null;
  dataPrescricao: string | null;
  diasAtePrescricao: number | null;
  statusPrescricao: string | null;
  situacaoSpcf: string | null;
  valorBruto: string | null;
  valorAtualizado: string | null;
  correcaoMonetaria: string | null;
  jurosMora: string | null;
  multa: string | null;
  indiceCorrecao: string | null;
  fatorCorrecao: string | null;
  mesesAtraso: number | null;
  cadeiaClasse: string | null;
  numNesVinculadas: number | null;
  elos: unknown;
};

export type AuditoriaData = {
  meta: Record<string, string>;
  notasEmpenho: NotaEmpenho[];
  cobrancas: Cobranca[];
  marcosInterruptivos: MarcoInterruptivo[];
  scoreDimensoes: ScoreDimensao[];
  planoAcao: PlanoAcao[];
  cadeiaContratos: CadeiaContrato[];
  inventarioDocs: InventarioDoc[];
  faturasDetalhadas: FaturaDetalhada[];
};

const AuditoriaCtx = createContext<AuditoriaData | null>(null);

export function AuditoriaProvider({ children }: { children: ReactNode }) {
  const { data, isLoading, error } = trpc.auditoria.get.useQuery(undefined, {
    staleTime: 60_000,
    refetchOnWindowFocus: false,
  });

  if (isLoading) {
    return (
      <div className="min-h-[400px] flex flex-col items-center justify-center gap-3">
        <Loader2 className="h-8 w-8 text-primary animate-spin" />
        <p className="text-xs font-mono uppercase tracking-wider text-muted-foreground">
          Carregando auditoria completa...
        </p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-[400px] flex items-center justify-center p-6 text-sm text-red-400">
        Falha ao carregar dados da auditoria: {error?.message}
      </div>
    );
  }

  return (
    <AuditoriaCtx.Provider value={data as unknown as AuditoriaData}>
      {children}
    </AuditoriaCtx.Provider>
  );
}

export function useAuditoria(): AuditoriaData {
  const ctx = useContext(AuditoriaCtx);
  if (!ctx) {
    throw new Error(
      "useAuditoria() deve ser usado dentro de <AuditoriaProvider>",
    );
  }
  return ctx;
}
