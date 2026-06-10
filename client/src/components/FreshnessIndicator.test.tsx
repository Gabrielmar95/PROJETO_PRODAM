/**
 * Testes do FreshnessIndicator (S3-M15).
 */
import { render, screen, cleanup } from "@testing-library/react";
import { afterEach, beforeAll, describe, expect, it, vi } from "vitest";
import type { ReactNode } from "react";
import { FreshnessIndicator } from "./FreshnessIndicator";

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

// Mock minimal do contexto via vi.mock — evita acoplar ao DashboardProvider real
let mockUpdatedAt = new Date().toISOString();
vi.mock("@/contexts/DashboardContext", () => ({
  useDashboardMeta: () => ({ updatedAt: mockUpdatedAt, meta: {} }),
  useDashboard: () => ({}),
  DashboardProvider: ({ children }: { children: ReactNode }) => children,
}));

afterEach(() => {
  cleanup();
});

describe("FreshnessIndicator (S3-M15)", () => {
  it("renderiza variante chip com data atual (fresh)", () => {
    mockUpdatedAt = new Date(Date.now() - 1000 * 60 * 30).toISOString(); // há 30 min
    render(<FreshnessIndicator />);
    const chip = screen.getByTestId("freshness-chip");
    expect(chip.getAttribute("data-freshness")).toBe("fresh");
    expect(chip.textContent).toMatch(/min/);
  });

  it("classifica como stale quando data é entre 24h e 7 dias", () => {
    mockUpdatedAt = new Date(Date.now() - 1000 * 60 * 60 * 48).toISOString(); // há 2 dias
    render(<FreshnessIndicator />);
    const chip = screen.getByTestId("freshness-chip");
    expect(chip.getAttribute("data-freshness")).toBe("stale");
    expect(chip.textContent).toMatch(/2d/);
  });

  it("classifica como old quando data é > 7 dias", () => {
    mockUpdatedAt = new Date(Date.now() - 1000 * 60 * 60 * 24 * 30).toISOString(); // há 30 dias
    render(<FreshnessIndicator />);
    const chip = screen.getByTestId("freshness-chip");
    expect(chip.getAttribute("data-freshness")).toBe("old");
  });

  it("variante inline aplica testid distinto", () => {
    mockUpdatedAt = new Date().toISOString();
    render(<FreshnessIndicator variant="inline" />);
    expect(screen.getByTestId("freshness-inline")).toBeTruthy();
  });

  it("título contém data absoluta legível", () => {
    mockUpdatedAt = new Date("2026-04-20T15:30:00Z").toISOString();
    render(<FreshnessIndicator />);
    const chip = screen.getByTestId("freshness-chip");
    const title = chip.getAttribute("title") || "";
    expect(title).toMatch(/20\/04\/2026/);
  });

  it("aria-label inclui tempo relativo", () => {
    mockUpdatedAt = new Date(Date.now() - 1000 * 60 * 60 * 3).toISOString(); // há 3h
    render(<FreshnessIndicator />);
    const chip = screen.getByTestId("freshness-chip");
    expect(chip.getAttribute("aria-label")).toMatch(/atualizados há 3h/);
  });
});
