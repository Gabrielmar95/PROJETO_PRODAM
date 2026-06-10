/**
 * Vitest — DensityContext (Sprint 2 Estrutural S2)
 *
 * Cobertura:
 *  1. valor padrão é "comfort" quando localStorage está vazio;
 *  2. setDensity atualiza estado, localStorage e atributo data-density no <html>;
 *  3. cycleDensity roda o ciclo compact → comfort → detailed → compact;
 *  4. preferência salva em localStorage é restaurada ao remontar o provider;
 *  5. leitura fora do provider lança erro explicativo.
 */
import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { act, cleanup, render, screen } from "@testing-library/react";
import { DensityProvider, useDensity } from "./DensityContext";

function Harness() {
  const { density, setDensity, cycleDensity } = useDensity();
  return (
    <div>
      <span data-testid="value">{density}</span>
      <button data-testid="set-compact" onClick={() => setDensity("compact")}>compact</button>
      <button data-testid="set-detailed" onClick={() => setDensity("detailed")}>detailed</button>
      <button data-testid="cycle" onClick={() => cycleDensity()}>cycle</button>
    </div>
  );
}

describe("DensityContext", () => {
  beforeEach(() => {
    window.localStorage.clear();
    document.documentElement.removeAttribute("data-density");
  });

  afterEach(() => {
    // garante DOM limpo entre testes para evitar multiple matches
    cleanup();
  });

  it("usa 'comfort' como valor padrão quando localStorage está vazio", () => {
    render(<DensityProvider><Harness /></DensityProvider>);
    expect(screen.getByTestId("value").textContent).toBe("comfort");
    expect(document.documentElement.getAttribute("data-density")).toBe("comfort");
  });

  it("setDensity atualiza estado, atributo DOM e localStorage", () => {
    render(<DensityProvider><Harness /></DensityProvider>);
    act(() => {
      screen.getByTestId("set-detailed").click();
    });
    expect(screen.getByTestId("value").textContent).toBe("detailed");
    expect(document.documentElement.getAttribute("data-density")).toBe("detailed");
    expect(window.localStorage.getItem("detran_density_v1")).toBe("detailed");
  });

  it("cycleDensity percorre compact → comfort → detailed → compact", () => {
    render(<DensityProvider><Harness /></DensityProvider>);
    // começa em comfort; cycle → detailed → compact → comfort
    act(() => { screen.getByTestId("cycle").click(); });
    expect(screen.getByTestId("value").textContent).toBe("detailed");
    act(() => { screen.getByTestId("cycle").click(); });
    expect(screen.getByTestId("value").textContent).toBe("compact");
    act(() => { screen.getByTestId("cycle").click(); });
    expect(screen.getByTestId("value").textContent).toBe("comfort");
  });

  it("restaura valor salvo em localStorage no próximo mount", () => {
    window.localStorage.setItem("detran_density_v1", "compact");
    render(<DensityProvider><Harness /></DensityProvider>);
    expect(screen.getByTestId("value").textContent).toBe("compact");
    expect(document.documentElement.getAttribute("data-density")).toBe("compact");
  });

  it("lança erro ao usar useDensity fora de DensityProvider", () => {
    // Suprime o error log do React durante este teste específico
    const origError = console.error;
    console.error = () => {};
    expect(() => render(<Harness />)).toThrow(/useDensity must be used within/);
    console.error = origError;
  });
});
