// DashboardContext — carrega o dashboard DETRAN/AM via tRPC e o expõe via hook
// Mantém a mesma interface do dashboard.json original, permitindo que as
// 15 seções continuem consumindo `dashboard` sem refatoração profunda.
import { createContext, useContext, ReactNode } from "react";
import { trpc } from "@/lib/trpc";
import type { Dashboard } from "@/data/types";
import { hydrateDashboard } from "@/data/helpers";
import { Loader2, AlertCircle } from "lucide-react";

type Ctx = {
  dashboard: Dashboard;
  meta: Record<string, string>;
  updatedAt: string;
};

const DashboardCtx = createContext<Ctx | null>(null);

export function DashboardProvider({ children }: { children: ReactNode }) {
  const { data, isLoading, error, refetch } = trpc.dashboard.get.useQuery(
    undefined,
    {
      staleTime: 60_000,
      refetchOnWindowFocus: false,
    },
  );

  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-background text-foreground gap-4">
        <div className="relative">
          <Loader2 className="h-10 w-10 text-primary animate-spin" />
        </div>
        <div className="text-center">
          <p className="font-display text-2xl text-primary tracking-wide">
            Brandão Ozores
          </p>
          <p className="text-xs text-muted-foreground mt-1 font-mono tracking-wider uppercase">
            Carregando Dossier Forense...
          </p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-background text-foreground gap-3 p-6">
        <AlertCircle className="h-10 w-10 text-red-400" />
        <p className="font-display text-xl text-primary">
          Falha ao carregar dados
        </p>
        <p className="text-xs text-muted-foreground max-w-md text-center">
          {error?.message ||
            "O servidor não retornou os dados do dashboard. Verifique a conexão com o banco."}
        </p>
        <button
          onClick={() => refetch()}
          className="mt-4 px-5 py-2 border border-primary/50 text-primary hover:bg-primary hover:text-background transition-colors text-xs font-mono uppercase tracking-wider"
        >
          Tentar Novamente
        </button>
      </div>
    );
  }

  // Hidrata síncrono ANTES de renderizar children (as seções leem o holder).
  const dashboardValue = data.sections as unknown as Dashboard;
  hydrateDashboard(dashboardValue);

  return (
    <DashboardCtx.Provider
      value={{
        dashboard: dashboardValue,
        meta: data.meta,
        updatedAt: data.updatedAt,
      }}
    >
      {children}
    </DashboardCtx.Provider>
  );
}

export function useDashboard(): Dashboard {
  const ctx = useContext(DashboardCtx);
  if (!ctx) {
    throw new Error(
      "useDashboard() deve ser usado dentro de <DashboardProvider>",
    );
  }
  return ctx.dashboard;
}

export function useDashboardMeta() {
  const ctx = useContext(DashboardCtx);
  if (!ctx) throw new Error("useDashboardMeta() requires DashboardProvider");
  return { meta: ctx.meta, updatedAt: ctx.updatedAt };
}
