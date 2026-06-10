// Seção Admin — edição colaborativa (apenas role=admin)
import { useState } from "react";
import { trpc } from "@/lib/trpc";
import { useAuth } from "@/_core/hooks/useAuth";
import { SectionHeader, ForensicCard } from "@/components/ForensicCard";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Shield, Lock, Edit3, History, CheckCircle2, Loader2, Radio, WifiOff } from "lucide-react";
import { useEffect, useRef } from "react";
import { getLoginUrl } from "@/const";
import { toast } from "sonner";

export default function SectionAdmin() {
  const { user, loading, isAuthenticated } = useAuth();

  if (loading) {
    return (
      <div className="py-16 text-center">
        <Loader2 className="h-6 w-6 animate-spin text-primary mx-auto mb-2" />
        <p className="text-[11px] text-muted-foreground">Verificando autenticação...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="space-y-5">
        <SectionHeader
          title="Edição Colaborativa"
          desc="Painel restrito — autentique-se para acessar"
        />
        <ForensicCard title="Acesso Restrito" variant="highlight">
          <div className="flex flex-col items-center py-8 text-center">
            <Lock className="h-10 w-10 text-primary/70 mb-3" />
            <p className="text-[13px] text-foreground mb-2 max-w-md">
              Esta área permite a edição colaborativa de contratos e faturas e requer autenticação Manus.
            </p>
            <p className="text-[11px] text-muted-foreground mb-5 max-w-md">
              Apenas usuários com perfil <span className="font-mono text-primary">admin</span> podem aplicar alterações. Todas as edições são registradas em log de auditoria.
            </p>
            <Button asChild className="gap-2">
              <a href={getLoginUrl()}>
                <Shield className="h-4 w-4" />
                Entrar com Manus
              </a>
            </Button>
          </div>
        </ForensicCard>
      </div>
    );
  }

  const isAdmin = user?.role === "admin";

  return (
    <div className="space-y-5">
      <SectionHeader
        title="Edição Colaborativa"
        desc={`Conectado como ${user?.name || user?.email || "usuário"} · perfil ${user?.role ?? "user"}`}
      />

      {!isAdmin && (
        <ForensicCard title="Permissão Insuficiente" variant="alert">
          <p className="text-[12px] text-foreground">
            Você está autenticado, mas não tem privilégios de administrador.
            Para obter acesso, solicite ao owner do projeto a atribuição do perfil
            <span className="font-mono text-primary ml-1">admin</span>.
          </p>
          <p className="text-[10px] text-muted-foreground mt-2">
            Nesta página você pode visualizar o histórico de edições, mas não aplicar alterações.
          </p>
        </ForensicCard>
      )}

      {isAdmin && (
        <>
          <ContratoEditor />
          <FaturaEditor />
        </>
      )}

      <AuditLogViewer />
    </div>
  );
}

// ============================================================================
function ContratoEditor() {
  const utils = trpc.useUtils();
  const { data: contratos = [], isLoading } = trpc.dashboard.contratos.useQuery();
  const [selected, setSelected] = useState<string>("");
  const [form, setForm] = useState({
    objeto: "",
    clausulaCorrecao: "",
    fundamentacao: "",
    validadoJuridicamente: "",
  });

  const update = trpc.admin.updateContrato.useMutation({
    onSuccess: async () => {
      toast.success("Contrato atualizado com sucesso");
      await Promise.all([
        utils.dashboard.contratos.invalidate(),
        utils.admin.auditLog.invalidate(),
      ]);
    },
    onError: (err) => {
      toast.error("Falha ao atualizar: " + err.message);
    },
  });

  const selectedContrato = contratos.find((c) => c.numero === selected);

  const loadForm = (numero: string) => {
    setSelected(numero);
    const c = contratos.find((x) => x.numero === numero);
    if (c) {
      setForm({
        objeto: c.objeto ?? "",
        clausulaCorrecao: c.clausulaCorrecao ?? "",
        fundamentacao: c.fundamentacao ?? "",
        validadoJuridicamente: c.validadoJuridicamente ?? "",
      });
    }
  };

  const submit = () => {
    if (!selected) return;
    update.mutate({ numero: selected, patch: form });
  };

  return (
    <ForensicCard title="Editor de Contratos" variant="highlight">
      <div className="flex items-start gap-2 mb-4 pb-3 border-b border-border/40">
        <Edit3 className="h-4 w-4 text-primary mt-0.5" />
        <p className="text-[11.5px] text-foreground/85 leading-relaxed">
          Atualize metadados jurídicos dos 18 contratos. Toda alteração é persistida e registrada no audit log.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div>
          <label className="small-caps text-[10px] text-muted-foreground block mb-1.5">
            Selecione o contrato
          </label>
          <Select
            value={selected}
            onValueChange={loadForm}
            disabled={isLoading}
          >
            <SelectTrigger className="h-9 text-[12px]">
              <SelectValue placeholder={isLoading ? "Carregando..." : "Escolha um contrato..."} />
            </SelectTrigger>
            <SelectContent>
              {contratos.map((c) => (
                <SelectItem key={c.numero} value={c.numero}>
                  {c.numero} — {(c.objeto ?? "").slice(0, 50)}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {selectedContrato && (
            <div className="mt-3 text-[10px] text-muted-foreground font-mono space-y-0.5">
              <div>Regime: <span className="text-primary">{selectedContrato.regimeJuridico || "—"}</span></div>
              <div>Faturas: {selectedContrato.totalFaturas || 0}</div>
              <div>C1 SELIC: R$ {Number(selectedContrato.c1Selic || 0).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}</div>
            </div>
          )}
        </div>

        {selected && (
          <div className="space-y-3">
            <Field
              label="Objeto"
              value={form.objeto}
              onChange={(v) => setForm({ ...form, objeto: v })}
              textarea
            />
            <Field
              label="Cláusula de Correção"
              value={form.clausulaCorrecao}
              onChange={(v) => setForm({ ...form, clausulaCorrecao: v })}
              placeholder="ex: 11.1"
            />
            <Field
              label="Fundamentação"
              value={form.fundamentacao}
              onChange={(v) => setForm({ ...form, fundamentacao: v })}
              textarea
            />
            <Field
              label="Validação Jurídica"
              value={form.validadoJuridicamente}
              onChange={(v) => setForm({ ...form, validadoJuridicamente: v })}
              placeholder="Sim / Parcial / Pendente"
            />
            <Button
              onClick={submit}
              disabled={update.isPending}
              className="w-full gap-2"
            >
              {update.isPending ? (
                <><Loader2 className="h-3 w-3 animate-spin" /> Salvando...</>
              ) : (
                <><CheckCircle2 className="h-3 w-3" /> Salvar alterações</>
              )}
            </Button>
          </div>
        )}
      </div>
    </ForensicCard>
  );
}

// ============================================================================
function FaturaEditor() {
  const utils = trpc.useUtils();
  const { data: faturas = [] } = trpc.dashboard.faturas.useQuery();
  const [query, setQuery] = useState("");
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [form, setForm] = useState({
    regime: "",
    prescricao: "",
    procedencia: "",
    observacoes: "",
  });

  const filtered = faturas
    .filter((f) => !query || `${f.nf} ${f.contratoNumero}`.toLowerCase().includes(query.toLowerCase()))
    .slice(0, 20);

  const loadForm = (id: number) => {
    setSelectedId(id);
    const f = faturas.find((x) => x.id === id);
    if (f) {
      setForm({
        regime: f.regime ?? "",
        prescricao: f.prescricao ?? "",
        procedencia: f.procedencia ?? "",
        observacoes: f.observacoes ?? "",
      });
    }
  };

  const update = trpc.admin.updateFatura.useMutation({
    onSuccess: async () => {
      toast.success("Fatura atualizada com sucesso");
      await Promise.all([
        utils.dashboard.faturas.invalidate(),
        utils.admin.auditLog.invalidate(),
      ]);
    },
    onError: (err) => toast.error("Falha: " + err.message),
  });

  return (
    <ForensicCard title="Editor de Faturas">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div>
          <label className="small-caps text-[10px] text-muted-foreground block mb-1.5">
            Buscar por NF ou contrato
          </label>
          <Input
            placeholder="Ex: 135059 ou 22/2014"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="h-8 text-[11px]"
          />
          <div className="mt-2 max-h-72 overflow-y-auto border border-border rounded-sm">
            {filtered.length === 0 ? (
              <div className="p-4 text-center text-[10px] text-muted-foreground">
                {query ? "Nenhum resultado" : "Digite para buscar..."}
              </div>
            ) : (
              filtered.map((f) => (
                <button
                  key={f.id}
                  onClick={() => loadForm(f.id)}
                  className={`w-full text-left px-3 py-2 border-b border-border/40 last:border-0 text-[10.5px] font-mono hover:bg-accent/30 transition-colors ${
                    selectedId === f.id ? "bg-primary/10 text-primary" : "text-foreground"
                  }`}
                >
                  <span className="font-semibold">NF {f.nf}</span> · {f.contratoNumero} · {f.competencia}
                </button>
              ))
            )}
          </div>
        </div>

        {selectedId !== null && (
          <div className="space-y-3">
            <Field label="Regime" value={form.regime} onChange={(v) => setForm({ ...form, regime: v })} />
            <Field label="Prescrição" value={form.prescricao} onChange={(v) => setForm({ ...form, prescricao: v })} placeholder="VIGENTE / PRESCRITA" />
            <Field label="Procedência" value={form.procedencia} onChange={(v) => setForm({ ...form, procedencia: v })} placeholder="P1-DOC / P2-PARCIAL" />
            <Field label="Observações" value={form.observacoes} onChange={(v) => setForm({ ...form, observacoes: v })} textarea />
            <Button
              onClick={() => update.mutate({ id: selectedId, patch: form })}
              disabled={update.isPending}
              className="w-full gap-2"
            >
              {update.isPending ? (
                <><Loader2 className="h-3 w-3 animate-spin" /> Salvando...</>
              ) : (
                <><CheckCircle2 className="h-3 w-3" /> Salvar fatura</>
              )}
            </Button>
          </div>
        )}
      </div>
    </ForensicCard>
  );
}

// ============================================================================
function AuditLogViewer() {
  // A4 — Live Audit via tRPC polling + detecção de novos eventos
  const POLL_MS = 4000;
  const { data: log = [], isLoading, isFetching, dataUpdatedAt } =
    trpc.admin.auditLog.useQuery(undefined, {
      refetchInterval: POLL_MS,
      refetchIntervalInBackground: false,
      staleTime: 1000,
    });

  // Detectar novos eventos comparando o topo do array (mais recente)
  const lastIdRef = useRef<number | null>(null);
  useEffect(() => {
    if (log.length === 0) return;
    const topId = log[0]?.id ?? null;
    if (topId === null) return;
    if (lastIdRef.current !== null && topId !== lastIdRef.current) {
      const newEntries = log.filter((e) => {
        const currentId = lastIdRef.current;
        return currentId !== null && e.id > currentId;
      });
      newEntries.forEach((entry) => {
        toast.info(
          `Nova edição: ${entry.action} · ${entry.target}`,
          {
            description: `por ${entry.userName || entry.userOpenId.slice(0, 8)}`,
            icon: <Radio className="h-4 w-4" />,
            duration: 5000,
          }
        );
      });
    }
    lastIdRef.current = topId;
  }, [log]);

  const isOnline =
    typeof navigator !== "undefined" ? navigator.onLine !== false : true;
  const lastUpdateText = dataUpdatedAt
    ? new Date(dataUpdatedAt).toLocaleTimeString("pt-BR")
    : "—";

  return (
    <ForensicCard title="Log de Auditoria (canal ao vivo)">
      {/* Banner live pulsante */}
      <div className="live-banner flex items-center justify-between gap-3 mb-3 p-2.5 rounded-sm border border-[color:var(--gold)]/25 bg-[color:var(--gold)]/5">
        <div className="flex items-center gap-2.5">
          <span
            className={`live-indicator ${isOnline ? "live-on" : "live-off"} ${
              isFetching ? "is-fetching" : ""
            }`}
            aria-hidden
          />
          <div className="flex items-center gap-1.5">
            {isOnline ? (
              <Radio className="h-3.5 w-3.5 text-[color:var(--gold)]" />
            ) : (
              <WifiOff className="h-3.5 w-3.5 text-[color:var(--t3)]" />
            )}
            <span className="small-caps text-[10px] tracking-[0.18em] font-semibold text-[color:var(--gold)]">
              {isOnline ? "Canal ao vivo" : "Offline"}
            </span>
          </div>
          <span className="text-[9px] font-mono text-[color:var(--t3)] hidden sm:inline">
            {isOnline ? `polling a cada ${POLL_MS / 1000}s` : "reconexão automática"}
          </span>
        </div>
        <div className="text-[9px] font-mono text-[color:var(--t3)]">
          última atualização · <span className="text-[color:var(--t2)]">{lastUpdateText}</span>
        </div>
      </div>

      <div className="flex items-center gap-2 mb-3 pb-2 border-b border-border/40">
        <History className="h-4 w-4 text-primary" />
        <p className="text-[11px] text-foreground/80">
          Histórico completo com detecção em tempo real. Cada ação is timestamped,
          atribuída ao usuário autor e notificada por toast.
        </p>
      </div>

      {isLoading ? (
        <div className="py-8 text-center text-[11px] text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin mx-auto mb-1" />
          Carregando log...
        </div>
      ) : log.length === 0 ? (
        <div className="py-8 text-center text-[11px] text-muted-foreground italic">
          Nenhuma alteração registrada ainda.
        </div>
      ) : (
        <div className="max-h-96 overflow-y-auto">
          <table className="w-full text-[10.5px] font-mono">
            <thead className="sticky top-0 bg-[color:var(--bg-3)] border-b border-primary/30">
              <tr className="text-primary">
                <th className="px-2 py-1.5 text-left">Quando</th>
                <th className="px-2 py-1.5 text-left">Usuário</th>
                <th className="px-2 py-1.5 text-left">Ação</th>
                <th className="px-2 py-1.5 text-left">Alvo</th>
                <th className="px-2 py-1.5 text-left">Detalhes</th>
              </tr>
            </thead>
            <tbody>
              {log.map((entry) => (
                <tr key={entry.id} className="border-b border-border/20 hover:bg-accent/20">
                  <td className="px-2 py-1.5 text-muted-foreground whitespace-nowrap">
                    {new Date(entry.createdAt).toLocaleString("pt-BR")}
                  </td>
                  <td className="px-2 py-1.5 text-foreground">{entry.userName || entry.userOpenId.slice(0, 8)}</td>
                  <td className="px-2 py-1.5">
                    <span className="px-1.5 py-0.5 rounded-sm bg-primary/10 text-primary text-[9px]">
                      {entry.action}
                    </span>
                  </td>
                  <td className="px-2 py-1.5 text-foreground">{entry.target}</td>
                  <td className="px-2 py-1.5 text-muted-foreground truncate max-w-[280px]">
                    {entry.patch}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </ForensicCard>
  );
}

// ============================================================================
function Field({
  label,
  value,
  onChange,
  textarea,
  placeholder,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  textarea?: boolean;
  placeholder?: string;
}) {
  return (
    <div>
      <label className="small-caps text-[10px] text-muted-foreground block mb-1">
        {label}
      </label>
      {textarea ? (
        <Textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          rows={2}
          className="text-[11px] min-h-[56px]"
        />
      ) : (
        <Input
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="h-8 text-[11px]"
        />
      )}
    </div>
  );
}
