/**
 * Testes do DossierThemeContext — Sprint 3 A1
 */
import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, act, cleanup } from "@testing-library/react";
import {
  DossierThemeProvider,
  useDossierTheme,
} from "./DossierThemeContext";

function ThemeConsumer() {
  const { theme, setTheme, cycleTheme } = useDossierTheme();
  return (
    <div>
      <span data-testid="theme">{theme}</span>
      <button onClick={() => setTheme("day")} data-testid="set-day">
        day
      </button>
      <button onClick={cycleTheme} data-testid="cycle">
        cycle
      </button>
    </div>
  );
}

describe("DossierThemeContext", () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.removeAttribute("data-dossier-theme");
  });
  afterEach(() => {
    cleanup();
  });

  it("usa 'dossier' como tema padrão", () => {
    render(
      <DossierThemeProvider>
        <ThemeConsumer />
      </DossierThemeProvider>
    );
    expect(screen.getByTestId("theme").textContent).toBe("dossier");
  });

  it("setTheme altera o tema e atualiza data-dossier-theme", () => {
    render(
      <DossierThemeProvider>
        <ThemeConsumer />
      </DossierThemeProvider>
    );
    act(() => {
      fireEvent.click(screen.getByTestId("set-day"));
    });
    expect(screen.getByTestId("theme").textContent).toBe("day");
    expect(document.documentElement.getAttribute("data-dossier-theme")).toBe(
      "day"
    );
  });

  it("cycleTheme cicla dossier → day → print → dossier", () => {
    render(
      <DossierThemeProvider>
        <ThemeConsumer />
      </DossierThemeProvider>
    );
    const theme = () => screen.getByTestId("theme").textContent;
    expect(theme()).toBe("dossier");
    act(() => fireEvent.click(screen.getByTestId("cycle")));
    expect(theme()).toBe("day");
    act(() => fireEvent.click(screen.getByTestId("cycle")));
    expect(theme()).toBe("print");
    act(() => fireEvent.click(screen.getByTestId("cycle")));
    expect(theme()).toBe("dossier");
  });

  it("persiste o tema em localStorage", () => {
    render(
      <DossierThemeProvider>
        <ThemeConsumer />
      </DossierThemeProvider>
    );
    act(() => fireEvent.click(screen.getByTestId("set-day")));
    expect(localStorage.getItem("detran_dossier_theme_v1")).toBe("day");
  });

  it("throws quando useDossierTheme é chamado fora do provider", () => {
    // Silenciar console.error do React para o teste
    const originalError = console.error;
    console.error = () => {};
    expect(() => render(<ThemeConsumer />)).toThrow();
    console.error = originalError;
  });
});
