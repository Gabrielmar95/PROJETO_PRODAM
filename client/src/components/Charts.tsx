// Gráficos temáticos — Recharts com paleta Noturno Forense

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  PieChart,
  Pie,
  LineChart,
  Line,
  Legend,
} from "recharts";

const GOLD = "#C5A55A";
const GOLD_LIGHT = "#D4B96E";
const PALETTE = [
  "#C5A55A", // gold
  "#6B8FA8", // info blue
  "#6BAF5E", // ok green
  "#D4A03C", // warn amber
  "#9B7BB4", // purple
  "#5BA8B5", // cyan
  "#A08840", // gold dark
];

const tooltipStyle: React.CSSProperties = {
  background: "rgba(18, 18, 26, 0.98)",
  border: "1px solid rgba(197, 165, 90, 0.4)",
  borderRadius: "4px",
  padding: "8px 12px",
  color: "#F5F0E8",
  fontSize: "11px",
  fontFamily: "Inter, sans-serif",
};

const labelStyle: React.CSSProperties = {
  color: GOLD,
  fontWeight: 600,
  marginBottom: "4px",
  fontSize: "11px",
};

const itemStyle: React.CSSProperties = {
  color: "#F5F0E8",
  fontFamily: "Fira Code, monospace",
  fontSize: "10.5px",
};

interface BarChartProps {
  data: { name: string; value: number; label?: string }[];
  height?: number;
  valueFormatter?: (v: number) => string;
  color?: string;
  horizontal?: boolean;
  onBarClick?: (name: string) => void;
  activeName?: string;
}

export function ForensicBar({
  data,
  height = 280,
  valueFormatter = (v) => v.toLocaleString("pt-BR"),
  color = GOLD,
  horizontal = false,
  yWidth,
  onBarClick,
  activeName,
}: BarChartProps & { yWidth?: number }) {
  const maxLabel = Math.max(0, ...data.map((d) => (d.name || "").length));
  const computedYWidth = yWidth ?? Math.min(240, Math.max(90, maxLabel * 6.5 + 16));
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart
        data={data}
        layout={horizontal ? "vertical" : "horizontal"}
        margin={{ top: 10, right: 20, left: horizontal ? 8 : 0, bottom: horizontal ? 10 : 20 }}
      >
        <CartesianGrid stroke="rgba(197,165,90,0.08)" strokeDasharray="2 4" />
        {horizontal ? (
          <>
            <XAxis
              type="number"
              tick={{ fill: "#7A7468", fontSize: 10, fontFamily: "Fira Code" }}
              tickFormatter={valueFormatter}
              stroke="rgba(197,165,90,0.2)"
            />
            <YAxis
              type="category"
              dataKey="name"
              tick={{ fill: "#B0A898", fontSize: 10 }}
              stroke="rgba(197,165,90,0.2)"
              width={computedYWidth}
              interval={0}
            />
          </>
        ) : (
          <>
            <XAxis
              dataKey="name"
              tick={{ fill: "#B0A898", fontSize: 10 }}
              stroke="rgba(197,165,90,0.2)"
              angle={-20}
              textAnchor="end"
              height={60}
            />
            <YAxis
              tick={{ fill: "#7A7468", fontSize: 10, fontFamily: "Fira Code" }}
              tickFormatter={valueFormatter}
              stroke="rgba(197,165,90,0.2)"
            />
          </>
        )}
        <Tooltip
          contentStyle={tooltipStyle}
          labelStyle={labelStyle}
          itemStyle={itemStyle}
          formatter={(v: number) => valueFormatter(v)}
          cursor={{ fill: "rgba(197,165,90,0.07)" }}
        />
        <Bar
          dataKey="value"
          radius={[2, 2, 0, 0]}
          onClick={onBarClick ? (e: unknown) => {
            const payload = (e as { name?: string })?.name;
            if (payload) onBarClick(payload);
          } : undefined}
          style={onBarClick ? { cursor: "pointer" } : undefined}
        >
          {data.map((d, i) => {
            const isActive = activeName && d.name === activeName;
            return (
              <Cell
                key={i}
                fill={color}
                fillOpacity={activeName ? (isActive ? 1 : 0.35) : 1}
                stroke={isActive ? "#D4B96E" : undefined}
                strokeWidth={isActive ? 2 : 0}
              />
            );
          })}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

export function ForensicPie({
  data,
  height = 280,
  valueFormatter = (v) => v.toLocaleString("pt-BR"),
  onSliceClick,
  activeName,
}: {
  data: { name: string; value: number }[];
  height?: number;
  valueFormatter?: (v: number) => string;
  onSliceClick?: (name: string) => void;
  activeName?: string;
}) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={50}
          outerRadius={95}
          paddingAngle={2}
          dataKey="value"
          labelLine={false}
          stroke="rgba(10,10,15,0.8)"
          strokeWidth={2}
          onClick={onSliceClick ? (e: unknown) => {
            const payload = (e as { name?: string })?.name;
            if (payload) onSliceClick(payload);
          } : undefined}
          style={onSliceClick ? { cursor: "pointer" } : undefined}
        >
          {data.map((d, i) => {
            const isActive = activeName && d.name === activeName;
            return (
              <Cell
                key={i}
                fill={PALETTE[i % PALETTE.length]}
                fillOpacity={activeName ? (isActive ? 1 : 0.4) : 1}
                stroke={isActive ? "#D4B96E" : "rgba(10,10,15,0.8)"}
                strokeWidth={isActive ? 3 : 2}
              />
            );
          })}
        </Pie>
        <Tooltip
          contentStyle={tooltipStyle}
          labelStyle={labelStyle}
          itemStyle={itemStyle}
          formatter={(v: number) => valueFormatter(v)}
        />
        <Legend
          verticalAlign="bottom"
          height={40}
          iconType="circle"
          iconSize={8}
          wrapperStyle={{ fontSize: "10px", color: "#B0A898", paddingTop: "8px" }}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}

export function ForensicLine({
  data,
  height = 280,
  valueFormatter = (v) => v.toLocaleString("pt-BR"),
  lines,
}: {
  data: Record<string, unknown>[];
  height?: number;
  valueFormatter?: (v: number) => string;
  lines: { key: string; name: string; color?: string }[];
}) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 10 }}>
        <CartesianGrid stroke="rgba(197,165,90,0.08)" strokeDasharray="2 4" />
        <XAxis
          dataKey="name"
          tick={{ fill: "#B0A898", fontSize: 10 }}
          stroke="rgba(197,165,90,0.2)"
        />
        <YAxis
          tick={{ fill: "#7A7468", fontSize: 10, fontFamily: "Fira Code" }}
          tickFormatter={valueFormatter}
          stroke="rgba(197,165,90,0.2)"
        />
        <Tooltip
          contentStyle={tooltipStyle}
          labelStyle={labelStyle}
          itemStyle={itemStyle}
          formatter={(v: number) => valueFormatter(v)}
        />
        <Legend
          verticalAlign="top"
          height={30}
          iconType="circle"
          iconSize={8}
          wrapperStyle={{ fontSize: "10px", color: "#B0A898" }}
        />
        {lines.map((l, i) => (
          <Line
            key={l.key}
            type="monotone"
            dataKey={l.key}
            name={l.name}
            stroke={l.color || PALETTE[i % PALETTE.length]}
            strokeWidth={2}
            dot={{ r: 3, fill: l.color || PALETTE[i % PALETTE.length] }}
            activeDot={{ r: 5, fill: GOLD_LIGHT }}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}

export { PALETTE };
