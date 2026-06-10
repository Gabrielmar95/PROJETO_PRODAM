/**
 * Testes do hook S3-M13 — atalhos globais.
 */
import { render, act, cleanup } from "@testing-library/react";
import { afterEach, beforeAll, describe, expect, it, vi } from "vitest";
import { DensityProvider } from "@/contexts/DensityContext";
import { useGlobalShortcuts } from "./useGlobalShortcuts";

beforeAll(() => {
  // sonner consulta matchMedia no mount; jsdom não implementa
  if (!window.matchMedia) {
    Object.defineProperty(window, "matchMedia", {
      writable: true,
      value: (q: string) => ({
        matches: false,
        media: q,
        addEventListener: () => {},
        removeEventListener: () => {},
        addListener: () => {},
        removeListener: () => {},
        onchange: null,
        dispatchEvent: () => false,
      }),
    });
  }
});

vi.mock("sonner", () => ({
  toast: {
    success: vi.fn(),
    info: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
  },
}));

function fireAlt(key: string, target?: EventTarget) {
  const ev = new KeyboardEvent("keydown", { key, altKey: true, bubbles: true, cancelable: true });
  if (target) {
    target.dispatchEvent(ev);
  } else {
    window.dispatchEvent(ev);
  }
}

function Harness({ onExport, onPrint }: { onExport?: () => void; onPrint?: () => void }) {
  useGlobalShortcuts({ onExport, onPrint });
  return null;
}

function setup(opts: { onExport?: () => void; onPrint?: () => void } = {}) {
  return render(
    <DensityProvider>
      <Harness {...opts} />
    </DensityProvider>,
  );
}

afterEach(() => {
  cleanup();
  document.documentElement.removeAttribute("data-density");
});

describe("useGlobalShortcuts (S3-M13)", () => {
  it("Alt+E dispara onExport", () => {
    const onExport = vi.fn();
    setup({ onExport });
    act(() => fireAlt("e"));
    expect(onExport).toHaveBeenCalledTimes(1);
  });

  it("Alt+P dispara onPrint", () => {
    const onPrint = vi.fn();
    setup({ onPrint });
    act(() => fireAlt("p"));
    expect(onPrint).toHaveBeenCalledTimes(1);
  });

  it("Alt+D cicla densidade no documentElement", () => {
    setup();
    // estado inicial: comfort
    expect(document.documentElement.getAttribute("data-density")).toBe("comfort");
    act(() => fireAlt("d"));
    expect(document.documentElement.getAttribute("data-density")).toBe("detailed");
    act(() => fireAlt("d"));
    expect(document.documentElement.getAttribute("data-density")).toBe("compact");
  });

  it("não dispara quando foco está em <input>", () => {
    const onExport = vi.fn();
    setup({ onExport });
    const input = document.createElement("input");
    document.body.appendChild(input);
    input.focus();
    act(() => fireAlt("e", input));
    expect(onExport).not.toHaveBeenCalled();
    input.remove();
  });

  it("não dispara quando foco está em <textarea>", () => {
    const onPrint = vi.fn();
    setup({ onPrint });
    const ta = document.createElement("textarea");
    document.body.appendChild(ta);
    ta.focus();
    act(() => fireAlt("p", ta));
    expect(onPrint).not.toHaveBeenCalled();
    ta.remove();
  });

  it("ignora teclas sem Alt", () => {
    const onExport = vi.fn();
    setup({ onExport });
    const ev = new KeyboardEvent("keydown", { key: "e", altKey: false, bubbles: true });
    act(() => {
      window.dispatchEvent(ev);
    });
    expect(onExport).not.toHaveBeenCalled();
  });

  it("respeita disabled=true", () => {
    const onExport = vi.fn();
    function H() {
      useGlobalShortcuts({ onExport, disabled: true });
      return null;
    }
    render(
      <DensityProvider>
        <H />
      </DensityProvider>,
    );
    act(() => fireAlt("e"));
    expect(onExport).not.toHaveBeenCalled();
  });
});
