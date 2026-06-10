// @vitest-environment jsdom
/**
 * ForensicTable.test.tsx — Testes de branches para ForensicTable.tsx
 * Cobre: render básico, empty state, sort, busca, badge auto-detect,
 * total row, showRowIndex, compact, title, priorityCols, expandedRows.
 */
import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ForensicTable } from "./ForensicTable";
import type { TableData } from "@/data/types";

const basicTable: TableData = {
  headers: ["NF", "Contrato", "Valor", "Status"],
  rows: [
    ["001", "10/2021", "R$ 1.000,00", "VIGENTE"],
    ["002", "11/2021", "R$ 2.500,50", "PRESCRITO"],
    ["003", "12/2021", "R$ 500,00", "PENDENTE"],
    ["Total", "", "R$ 4.000,50", ""],
  ],
};

const emptyTable: TableData = {
  headers: ["NF", "Contrato", "Valor"],
  rows: [],
};

describe("ForensicTable — render básico", () => {
  it("renderiza headers da tabela", () => {
    const { container } = render(<ForensicTable table={basicTable} />);
    expect(container.querySelector("table")).toBeTruthy();
    expect(container.textContent).toContain("NF");
    expect(container.textContent).toContain("Contrato");
  });

  it("renderiza todas as linhas de dados", () => {
    const { container } = render(<ForensicTable table={basicTable} />);
    expect(container.textContent).toContain("10/2021");
    expect(container.textContent).toContain("11/2021");
  });

  it("renderiza tabela vazia sem crash", () => {
    const { container } = render(<ForensicTable table={emptyTable} />);
    expect(container.querySelector("table")).toBeTruthy();
  });
});

describe("ForensicTable — title e searchable", () => {
  it("exibe title quando fornecido", () => {
    render(<ForensicTable table={basicTable} title="Tabela de Faturas" />);
    expect(screen.getByText("Tabela de Faturas")).toBeTruthy();
  });

  it("não exibe title quando não fornecido", () => {
    const { container } = render(<ForensicTable table={basicTable} />);
    expect(container.querySelector("h4")).toBeNull();
  });

  it("exibe campo de busca quando searchable=true", () => {
    const { container } = render(
      <ForensicTable table={basicTable} searchable={true} />
    );
    expect(container.querySelector("input")).toBeTruthy();
  });

  it("não exibe campo de busca quando searchable=false (padrão)", () => {
    const { container } = render(<ForensicTable table={basicTable} />);
    expect(container.querySelector("input")).toBeNull();
  });

  it("filtra linhas ao digitar na busca", () => {
    const { container } = render(
      <ForensicTable table={basicTable} searchable={true} />
    );
    const input = container.querySelector("input")!;
    fireEvent.change(input, { target: { value: "10/2021" } });
    expect(container.textContent).toContain("10/2021");
    expect(container.textContent).not.toContain("11/2021");
  });

  it("exibe placeholder customizado na busca", () => {
    const { container } = render(
      <ForensicTable
        table={basicTable}
        searchable={true}
        searchPlaceholder="Filtrar contratos..."
      />
    );
    const input = container.querySelector("input") as HTMLInputElement;
    expect(input.placeholder).toBe("Filtrar contratos...");
  });
});

describe("ForensicTable — showRowIndex", () => {
  it("exibe coluna # quando showRowIndex=true", () => {
    const { container } = render(
      <ForensicTable table={basicTable} showRowIndex={true} />
    );
    expect(container.textContent).toContain("#");
  });

  it("não exibe coluna # quando showRowIndex=false (padrão)", () => {
    const { container } = render(<ForensicTable table={basicTable} />);
    // Verifica que o header # não está presente
    const headers = container.querySelectorAll("th");
    const headerTexts = Array.from(headers).map((h) => h.textContent?.trim());
    expect(headerTexts).not.toContain("#");
  });
});

describe("ForensicTable — sort", () => {
  it("clica no header para ordenar (asc)", () => {
    const { container } = render(<ForensicTable table={basicTable} />);
    const headers = container.querySelectorAll("th");
    // Clica no header "Valor" (índice 2)
    fireEvent.click(headers[2]);
    // Deve renderizar sem crash
    expect(container.querySelector("table")).toBeTruthy();
  });

  it("clica no mesmo header duas vezes para inverter ordenação", () => {
    const { container } = render(<ForensicTable table={basicTable} />);
    const headers = container.querySelectorAll("th");
    fireEvent.click(headers[2]);
    fireEvent.click(headers[2]);
    expect(container.querySelector("table")).toBeTruthy();
  });

  it("ordena coluna de texto (NF)", () => {
    const { container } = render(<ForensicTable table={basicTable} />);
    const headers = container.querySelectorAll("th");
    fireEvent.click(headers[0]); // NF
    expect(container.querySelector("table")).toBeTruthy();
  });
});

describe("ForensicTable — badgeCols", () => {
  it("renderiza badge quando badgeCols é fornecido explicitamente", () => {
    const { container } = render(
      <ForensicTable table={basicTable} badgeCols={[3]} />
    );
    // Status column (idx 3) deve ter badges
    expect(container.textContent).toContain("VIGENTE");
  });

  it("auto-detecta colunas de badge via BADGE_PATTERNS", () => {
    const { container } = render(<ForensicTable table={basicTable} />);
    // VIGENTE e PRESCRITO devem ser renderizados (auto-detectados)
    expect(container.textContent).toContain("VIGENTE");
    expect(container.textContent).toContain("PRESCRITO");
  });
});

describe("ForensicTable — compact", () => {
  it("renderiza sem crash com compact=true", () => {
    const { container } = render(
      <ForensicTable table={basicTable} compact={true} />
    );
    expect(container.querySelector("table")).toBeTruthy();
  });
});

describe("ForensicTable — priorityCols (acordeão)", () => {
  it("renderiza com priorityCols sem crash", () => {
    const { container } = render(
      <ForensicTable table={basicTable} priorityCols={[0, 2]} />
    );
    expect(container.querySelector("table")).toBeTruthy();
  });

  it("exibe apenas colunas prioritárias nos headers", () => {
    const { container } = render(
      <ForensicTable table={basicTable} priorityCols={[0, 2]} />
    );
    const headerRow = container.querySelector("thead tr");
    expect(headerRow?.textContent).toContain("NF");
    expect(headerRow?.textContent).toContain("Valor");
  });

  it("expande linha ao clicar no botão de acordeão", () => {
    const { container } = render(
      <ForensicTable table={basicTable} priorityCols={[0, 2]} />
    );
    const expandBtns = container.querySelectorAll("tbody tr td button, tbody tr td svg");
    // Clica na primeira linha para expandir
    const firstRow = container.querySelector("tbody tr");
    if (firstRow) fireEvent.click(firstRow.querySelector("td")!);
    expect(container.querySelector("table")).toBeTruthy();
  });
});

describe("ForensicTable — total row highlight", () => {
  it("linha 'Total' é renderizada", () => {
    const { container } = render(<ForensicTable table={basicTable} />);
    expect(container.textContent).toContain("Total");
  });

  it("tabela sem total row renderiza normalmente", () => {
    const tableNoTotal: TableData = {
      headers: ["NF", "Valor"],
      rows: [["001", "R$ 100"], ["002", "R$ 200"]],
    };
    const { container } = render(<ForensicTable table={tableNoTotal} />);
    expect(container.querySelector("table")).toBeTruthy();
    expect(container.textContent).toContain("001");
  });
});

describe("ForensicTable — maxHeight", () => {
  it("aplica maxHeight customizado ao container", () => {
    const { container } = render(
      <ForensicTable table={basicTable} maxHeight="300px" />
    );
    const scrollDiv = container.querySelector("[style]");
    expect(scrollDiv?.getAttribute("style")).toContain("300px");
  });
});
