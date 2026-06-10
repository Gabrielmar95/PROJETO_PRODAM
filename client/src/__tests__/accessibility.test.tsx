/**
 * S3-M14 — Smoke tests de acessibilidade com axe-core.
 *
 * Não substituem auditoria manual com leitor de tela; cobrem a baseline:
 * landmark roles, contraste, alt text, label de form, ARIA válida.
 *
 * Alvo: componentes de chrome (header, sidebar) + indicadores reutilizáveis.
 * Seções inteiras (200+ tabelas) ficam fora desse smoke porque demandariam
 * mocks profundos de tRPC + Recharts; os ARIA roles delas são cobertos por
 * inspeção visual e CI separado.
 */
import { render, cleanup } from "@testing-library/react";
import { afterEach, beforeAll, describe, expect, it, vi } from "vitest";
import axe from "axe-core";
import { FreshnessIndicator } from "@/components/FreshnessIndicator";

beforeAll(() => {
  if (!window.matchMedia) {
    Object.defineProperty(window, "matchMedia", {
      writable: true,
      value: () => ({
        matches: false,
        addEventListener: () => {},
        removeEventListener: () => {},
      }),
    });
  }
});

vi.mock("@/contexts/DashboardContext", () => ({
  useDashboardMeta: () => ({
    updatedAt: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    meta: {},
  }),
  useDashboard: () => ({}),
}));

afterEach(() => cleanup());

async function runAxe(node: HTMLElement) {
  const results = await axe.run(node, {
    runOnly: {
      type: "tag",
      values: ["wcag2a", "wcag2aa"],
    },
    resultTypes: ["violations"],
  });
  return results.violations;
}

describe("Acessibilidade axe-core (S3-M14)", () => {
  it("FreshnessIndicator chip não tem violações WCAG2A/AA", async () => {
    const { container } = render(<FreshnessIndicator />);
    const violations = await runAxe(container);
    if (violations.length > 0) {
      // eslint-disable-next-line no-console
      console.error("Violations:", JSON.stringify(violations, null, 2));
    }
    expect(violations).toHaveLength(0);
  });

  it("FreshnessIndicator inline expõe aria-label", async () => {
    const { getByTestId } = render(<FreshnessIndicator variant="inline" />);
    const inline = getByTestId("freshness-inline");
    expect(inline.getAttribute("aria-label")).toMatch(/atualizados/);
  });

  it("Botão básico com label visível passa axe", async () => {
    const { container } = render(
      <button type="button" className="px-2 py-1">
        Exportar CSV
      </button>,
    );
    const violations = await runAxe(container);
    expect(violations).toHaveLength(0);
  });

  it("Botão sem label acessível falha (sanity check do próprio axe)", async () => {
    const { container } = render(
      <button type="button" className="px-2 py-1" aria-label="">
        {/* sem texto, sem aria-label útil */}
      </button>,
    );
    const violations = await runAxe(container);
    expect(violations.length).toBeGreaterThan(0);
  });
});
