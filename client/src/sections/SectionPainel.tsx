// Design: Noturno Forense — Painel Executivo
import { dashboard, fmtBRL } from "@/data/helpers";
import { KpiGrid, KpiCard } from "@/components/KpiCard";
import { ForensicCard, SectionHeader } from "@/components/ForensicCard";
import { ForensicBar, ForensicPie } from "@/components/Charts";
import { ForensicTable } from "@/components/ForensicTable";
import { ExecutiveSummary } from "@/components/ExecutiveSummary";
import EditorialHero from "@/components/EditorialHero";
import { useFilters } from "@/contexts/FilterContext";
import { useMemo } from "react";

export default function SectionPainel() {
  const sec = dashboard.painel;
  const { filteredFaturas, filters, applyDrillDown } = useFilters();

  const porRegime = Object.values(
    filteredFaturas.reduce<Record<string, { name: string; value: number; count: number }>>((acc, f) => {
      const k = f.regime || "Outros";
      if (!acc[k]) acc[k] = { name: k, value: 0, count: 0 };
      acc[k].value += f.c1Num;
      acc[k].count += 1;
      return acc;
    }, {})
  ).sort((a, b) => b.value - a.value);

  const porAno = Object.values(
    filteredFaturas.reduce<Record<string, { name: string; value: number }>>((acc, f) => {
      const k = String(f.ano);
      if (!acc[k]) acc[k] = { name: k, value: 0 };
      acc[k].value += f.c1Num;
      return acc;
    }, {})
  ).sort((a, b) => a.name.localeCompare(b.name));

  const tables = sec.tables || [];
  const cards = sec.cards || [];
  const top20 = tables[0];

  // Nota jurídica é o 2º card no JSON, mas queremos que ela receba drop-cap
  // Renderizamos: primeiro a tabela Top 20, depois a Nota Jurídica em destaque com drop-cap
  const notaJuridica = cards.find((c) => /nota.*jur|juridic/i.test(c.title)) || cards[1];

  // Métricas do EditorialHero (reativas ao drill-down)
  const heroMetrics = useMemo(() => {
    const total = filteredFaturas.reduce((s, f) => s + f.saldoNum, 0);
    const totalC1 = filteredFaturas.reduce((s, f) => s + f.c1Num, 0);
    const correcaoPct = total > 0 ? ((totalC1 / total - 1) * 100).toFixed(1).replace(".", ",") : "0,0";
    const contratosSet = new Set(filteredFaturas.map((f) => f.contrato).filter(Boolean));
    return {
      saldo: fmtBRL(total),
      correcao: `+${correcaoPct}%`,
      faturas: String(filteredFaturas.length),
      contratos: String(contratosSet.size),
    };
  }, [filteredFaturas]);

  return (
    <div className="space-y-6">
      {/* A2 — Editorial Hero (capa de revista no topo) */}
      <EditorialHero ctaTargetId="executive-summary" metrics={heroMetrics} />

      <SectionHeader title={sec.title} desc={sec.desc} />

      {/* S3 — Síntese Executiva narrativa (drop-cap + 3 takeaways + cota) */}
      <div id="executive-summary">
        <ExecutiveSummary faturas={filteredFaturas} />
      </div>

      {/* Hierarquia F-pattern: 2 KPIs herói (Saldo + C1) ocupam linha de topo,
          secundários em grid abaixo, restante mais denso. Cria leitura ocidental
          natural e dá peso editorial à informação crítica. */}
      {sec.kpis.length > 2 ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 stagger">
            {sec.kpis.slice(0, 2).map((k, i) => (
              <KpiCard key={`hero-${i}`} kpi={{ ...k, big: true }} idx={i} />
            ))}
          </div>
          <KpiGrid kpis={sec.kpis.slice(2)} />
        </>
      ) : (
        <KpiGrid kpis={sec.kpis} />
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ForensicCard title="Distribuição por Regime Jurídico (C1 SELIC)">
          <div className="text-[10px] text-muted-foreground/80 mb-2 italic">
            Clique em uma fatia para filtrar todas as seções por regime.
          </div>
          <ForensicPie
            data={porRegime.map((r) => ({ name: r.name, value: r.value }))}
            valueFormatter={fmtBRL}
            height={320}
            onSliceClick={(name) => applyDrillDown("regime", name)}
            activeName={filters.regime !== "all" ? filters.regime : undefined}
          />
        </ForensicCard>
        <ForensicCard title="Valor Atualizado por Ano de Vencimento">
          <div className="text-[10px] text-muted-foreground/80 mb-2 italic">
            Clique em uma barra para filtrar por ano de vencimento.
          </div>
          <ForensicBar
            data={porAno}
            valueFormatter={(v) =>
              v >= 1_000_000 ? `R$ ${(v / 1_000_000).toFixed(1)}M` : `R$ ${(v / 1000).toFixed(0)}k`
            }
            height={320}
            onBarClick={(name) => applyDrillDown("ano", name)}
            activeName={filters.ano !== "all" ? filters.ano : undefined}
          />
        </ForensicCard>
      </div>

      {top20 && top20.rows && top20.rows.length > 0 && (
        <ForensicCard title="Top 20 Faturas por Valor Atualizado (C1 — SELIC)">
          <div className="text-[10px] text-muted-foreground/80 mb-2 italic">
            Clique em qualquer linha para revelar dados técnicos (meses em atraso, encargos, fator).
          </div>
          <ForensicTable
            table={{ headers: top20.headers || [], rows: top20.rows }}
            maxHeight="480px"
            compact
            // Mostra 6 colunas-chave; demais (#, Meses, Encargos, Fator) vão para acordão expand-row
            priorityCols={[1, 2, 3, 5, 7, 9]}
          />
        </ForensicCard>
      )}

      {notaJuridica && (
        <ForensicCard title={notaJuridica.title} variant="highlight">
          <div
            className="text-[12.5px] text-[color:var(--t1)]/90 leading-[1.8] drop-cap"
            style={{ fontFeatureSettings: '"onum", "liga"' }}
          >
            {notaJuridica.text}
          </div>
        </ForensicCard>
      )}
    </div>
  );
}
