// Cenários de Cobrança — C1 / C2 / C3
import { dashboard, fmtBRL, parseBRL } from "@/data/helpers";
import { KpiGrid } from "@/components/KpiCard";
import { ForensicCard, SectionHeader } from "@/components/ForensicCard";
import { ForensicTable } from "@/components/ForensicTable";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import WaterfallChart from "@/components/WaterfallChart";
import Calculator from "@/components/Calculator";
import ScenarioReveal, { type Scenario } from "@/components/ScenarioReveal";

export default function SectionCenarios() {
  const sec = dashboard.cenarios;
  const comparativo = sec.tables[0];

  // Montar dados do gráfico comparativo (sem linha TOTAL)
  const chartData =
    comparativo?.rows
      .filter((r) => !r[0].toLowerCase().startsWith("total"))
      .map((r) => ({
        name: r[0],
        C1: parseBRL(r[3]),
        C2: parseBRL(r[4]),
        C3: parseBRL(r[5]),
      })) || [];

  return (
    <div className="space-y-6">
      <SectionHeader title={sec.title} desc={sec.desc} />
      <KpiGrid kpis={sec.kpis} />

      {comparativo && (
        <ForensicCard title="Comparativo por Regime Jurídico">
          <ForensicTable table={comparativo} maxHeight="500px" />
        </ForensicCard>
      )}

      <ForensicCard title="Visualização Gráfica — C1 vs C2 vs C3 por Regime" variant="highlight">
        <div className="text-[11px] text-muted-foreground mb-3">
          Cada regime jurídico gera três cenários distintos conforme tese aplicada. Passe o mouse sobre as barras para ver valores detalhados.
        </div>
        <MultiBar data={chartData} />
      </ForensicCard>

      {(() => {
        const totalRow = comparativo?.rows.find((r) => r[0].toLowerCase().startsWith("total"));
        if (!totalRow) return null;
        // Layout da row TOTAL: [Regime, Faturas, Saldo, C1, C2, C3, %]
        const saldo = parseBRL(totalRow[2]);
        const c1 = parseBRL(totalRow[3]);
        const c2 = parseBRL(totalRow[4]);
        const c3 = parseBRL(totalRow[5]);
        return (
          <ForensicCard title="Cascata (Waterfall) · Composição dos 3 Cenários">
            <div className="text-[11px] text-muted-foreground mb-4">
              De onde vem cada real: Saldo original → Correção do cenário → Valor total exigível.
            </div>
            <WaterfallChart
              saldo={saldo}
              scenarios={[
                { name: "Cenário Principal", code: "C1 SELIC", total: c1, color: "#C5A55A" },
                { name: "Cenário Subsidiário", code: "C2 Poupança", total: c2, color: "#6B8FA8" },
                { name: "Cenário Subsidiário", code: "C3 1% a.m.", total: c3, color: "#6BAF5E" },
              ]}
            />
          </ForensicCard>
        );
      })()}

      {(() => {
        const totalRow = comparativo?.rows.find((r) => r[0].toLowerCase().startsWith("total"));
        if (!totalRow) return null;
        const saldo = parseBRL(totalRow[2]);
        const c1 = parseBRL(totalRow[3]);
        const c2 = parseBRL(totalRow[4]);
        const c3 = parseBRL(totalRow[5]);
        const scenarios: [Scenario, Scenario, Scenario] = [
          {
            code: "C1",
            label: "SELIC",
            legalBasis: "Art. 406 CC · Tema 99 STJ",
            total: c1,
            narrative:
              "Tese principal: indexação pela taxa SELIC desde o vencimento, com juízos integrais, aplicável em sede de execução forçada nos termos do art. 784 do CPC.",
            pullQuote:
              "A SELIC compreende juros e correção monetária desde a edição da Lei 11.960/2009— parametrizando o montante devido pelo Poder Público.",
          },
          {
            code: "C2",
            label: "Poupança + Juros",
            legalBasis: "Lei 11.960/2009 (redução de encargos)",
            total: c2,
            narrative:
              "Tese subsidiária conservadora: TR como correção mais juros simples até 2021, assegurando cenário mínimo defensável em caso de afastamento da SELIC.",
            pullQuote:
              "Mesmo no cenário mais restritivo, a massa remanescente excede R$ 26,9 milhões — demonstrando a robustez da pretensão creditória.",
          },
          {
            code: "C3",
            label: "1% a.m. linear",
            legalBasis: "Art. 161 CTN (juros de mora)",
            total: c3,
            narrative:
              "Tese alternativa: juros mensais lineares de 1% sobre o saldo principal, cumulados com correção monetária INPC — confere balizamento próprio ao Estado.",
          },
        ];
        return (
          <>
            <ScenarioReveal saldoOriginal={saldo} scenarios={scenarios} />
            <Calculator baselineC1={c1} baselineC2={c2} baselineC3={c3} />
          </>
        );
      })()}

      {sec.cards.map((c, i) => (
        <ForensicCard key={i} title={c.title} variant={i === 0 ? "highlight" : "default"}>
          <div className="text-[11.5px] text-[color:var(--t2)] leading-relaxed whitespace-pre-line">
            {c.text}
          </div>
          {sec.tables[1] && i === 0 && (
            <div className="mt-3">
              <ForensicTable table={sec.tables[1]} maxHeight="300px" />
            </div>
          )}
        </ForensicCard>
      ))}
    </div>
  );
}

function MultiBar({ data }: { data: { name: string; C1: number; C2: number; C3: number }[] }) {
  const valueFormatter = (v: number) =>
    v >= 1_000_000 ? `R$ ${(v / 1_000_000).toFixed(2)}M` : `R$ ${(v / 1000).toFixed(0)}k`;

  return (
    <div style={{ width: "100%", height: 360 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 10, right: 20, left: 10, bottom: 50 }}>
          <CartesianGrid stroke="rgba(197,165,90,0.08)" strokeDasharray="2 4" />
          <XAxis
            dataKey="name"
            tick={{ fill: "#B0A898", fontSize: 10 }}
            stroke="rgba(197,165,90,0.2)"
            angle={-20}
            textAnchor="end"
            height={70}
            interval={0}
          />
          <YAxis
            tick={{ fill: "#7A7468", fontSize: 10, fontFamily: "Fira Code" }}
            tickFormatter={valueFormatter}
            stroke="rgba(197,165,90,0.2)"
          />
          <Tooltip
            contentStyle={{
              background: "rgba(18, 18, 26, 0.98)",
              border: "1px solid rgba(197, 165, 90, 0.4)",
              borderRadius: "4px",
              padding: "8px 12px",
              fontSize: "11px",
              fontFamily: "Inter, sans-serif",
            }}
            labelStyle={{ color: "#C5A55A", fontWeight: 600, marginBottom: 4 }}
            itemStyle={{ fontFamily: "Fira Code, monospace", fontSize: "10.5px" }}
            formatter={(v: number) => valueFormatter(v)}
            cursor={{ fill: "rgba(197,165,90,0.05)" }}
          />
          <Legend
            verticalAlign="top"
            height={28}
            iconType="square"
            iconSize={10}
            wrapperStyle={{ fontSize: "10px", color: "#B0A898" }}
          />
          <Bar dataKey="C1" name="C1 — SELIC" fill="#C5A55A" radius={[2, 2, 0, 0]} />
          <Bar dataKey="C2" name="C2 — Poupança" fill="#6B8FA8" radius={[2, 2, 0, 0]} />
          <Bar dataKey="C3" name="C3 — 1% a.m." fill="#6BAF5E" radius={[2, 2, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export { fmtBRL };
