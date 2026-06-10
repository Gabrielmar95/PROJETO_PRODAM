import { cn } from "@/lib/utils";
import type { ReactNode } from "react";

interface Props {
  title?: string;
  children: ReactNode;
  variant?: "default" | "highlight" | "alert";
  className?: string;
}

export function ForensicCard({ title, children, variant = "default", className }: Props) {
  return (
    <div
      className={cn(
        "forensic-card lift-on-hover",
        variant === "highlight" && "highlight",
        variant === "alert" && "alert",
        className
      )}
    >
      {title && (
        <h3
          className={cn(
            "font-display text-[16px] font-semibold mb-3 leading-tight",
            variant === "alert" ? "text-[color:var(--warn)]" : "text-primary"
          )}
          style={{ fontFeatureSettings: '"liga", "dlig", "onum"' }}
        >
          {title}
        </h3>
      )}
      {children}
    </div>
  );
}

export function SectionHeader({ title, desc }: { title: string; desc?: string }) {
  return (
    <div className="section-header mb-6">
      <div className="ornament text-[10px] mb-2">
        <span className="ornament-diamond" aria-hidden />
        <span className="small-caps font-mono">Dossiê Forense</span>
        <span className="ornament-diamond" aria-hidden />
      </div>
      <h2
        className="font-display text-[26px] lg:text-[34px] font-semibold leading-[1.05] tracking-[-0.012em] bg-gradient-to-b from-[color:var(--t1)] to-[color:var(--t1)]/70 bg-clip-text text-transparent"
        style={{ fontFeatureSettings: '"liga", "dlig", "onum"' }}
      >
        {title}
      </h2>
      {desc && (
        <p className="text-[12.5px] text-muted-foreground mt-2 max-w-3xl leading-relaxed">
          {desc}
        </p>
      )}
      <div className="gold-line mt-3" />
    </div>
  );
}
