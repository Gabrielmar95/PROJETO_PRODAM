/** @vitest-environment jsdom */
import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, cleanup } from "@testing-library/react";
import SectionProntuario from "./SectionProntuario";
import { hydrateDashboard, dashboard } from "@/data/helpers";

const payload = {
  title: "Prontuário de Execução — DETRAN/AM × PRODAM",
  desc: "Consolidação executável dos 18 contratos.",
  kpis: [
    { label: "Contratos", value: "18", detail: "18 instrumentos" },
    { label: "Valor exequível", value: "R$ 29.54M", detail: "multa 2%", big: true, green: true },
  ],
  tables: [{ headers: ["Prontidão", "Qtd"], rows: [["PRONTO", "5"]] }],
  cards: [
    {
      title: "Contrato 22/2014 — OFICIAL_COMPLETO",
      text: JSON.stringify({
        numero: "022/2014",
        numero_oficial: "22/2014",
        objeto: "Execução de Sistemas",
        classe: "OFICIAL_COMPLETO",
        qtd_faturas: 12,
        saldo_bruto_nominal: 1584062.67,
        valor_exequivel_atualizado: 3206636.76,
        valor_prescrito: 0,
        multa_computada: 39102.15,
        correcao_monetaria: 1579400.0,
        juros_mora: 0,
        honorarios_estim_20pct: 641327.35,
        custas_estim_2pct: 64132.73,
        venc_menor: "27/10/2021",
        venc_maior: "27/10/2021",
        prescr_fatal: "26/10/2026",
        status_prescr_fatal: "ATENCAO",
        via_processual_recomendada: "Execução por quantia certa (art. 783-785 CPC)",
        juizo_competente: "Vara da Fazenda Pública de Manaus",
        prontidao_execucao: "PRONTO",
        fundamentos_executivos: ["Art. 784, III CPC", "Lei 14.133/2021"],
        documentos_em_maos: { NOTA_FISCAL: 1, NOTA_DE_EMPENHO: 2 },
        documentos_faltantes: ["Aceite técnico", "NL"],
        nota_multa: "Multa 2% Lei 14.133",
      }),
    },
    {
      title: "Contrato 296/2025 — SOMBRA_SPCF",
      text: JSON.stringify({
        numero: "296/2025",
        numero_oficial: "296/2025",
        objeto: "Migração sistemas",
        classe: "SOMBRA_SPCF",
        qtd_faturas: 4,
        saldo_bruto_nominal: 2522329.4,
        valor_exequivel_atualizado: 2719996.25,
        valor_prescrito: 0,
        multa_computada: 50604.21,
        correcao_monetaria: 147062.64,
        juros_mora: 0,
        honorarios_estim_20pct: 543999.25,
        custas_estim_2pct: 54399.93,
        venc_menor: null,
        venc_maior: null,
        prescr_fatal: null,
        status_prescr_fatal: null,
        via_processual_recomendada: "Ação de cobrança (art. 319 CPC)",
        juizo_competente: "Vara da Fazenda Pública de Manaus",
        prontidao_execucao: "RASTREIO_DOCUMENTAL",
        fundamentos_executivos: ["CC art. 884"],
        documentos_em_maos: { NOTA_FISCAL: 4, NOTA_DE_EMPENHO: 1 },
        documentos_faltantes: ["Contrato formal"],
        nota_multa: "Multa 2%",
        nes_spcf: {
          qtd: 0,
          classe: "SOMBRA_SPCF",
          exemplos: [],
          observacao: "Contrato SOMBRA sem NE direta — exige ação de enriquecimento sem causa (CC art. 884) como fundamento principal.",
        },
      }),
    },
    {
      title: "Contrato 8/2021 — OFICIAL_COMPLEMENTAR",
      text: JSON.stringify({
        numero: "008/2021",
        numero_oficial: "8/2021",
        objeto: "(Complementar — consultar PRODAM_DOCS/)",
        classe: "OFICIAL_COMPLEMENTAR",
        qtd_faturas: 12,
        saldo_bruto_nominal: 30625.82,
        valor_exequivel_atualizado: 21814.45,
        valor_prescrito: 0,
        multa_computada: 403.22,
        correcao_monetaria: 30.73,
        juros_mora: 1250.10,
        honorarios_estim_20pct: 4362.89,
        custas_estim_2pct: 436.29,
        venc_menor: "27/12/2021",
        venc_maior: "27/03/2026",
        prescr_fatal: "26/03/2031",
        status_prescr_fatal: "VIGENTE",
        via_processual_recomendada: "Ação de cobrança ordinária (art. 319 CPC) com prova suplementar",
        juizo_competente: "Vara Especializada da Fazenda Pública Estadual",
        prontidao_execucao: "PROVA_SUPLEMENTAR",
        fundamentos_executivos: ["Art. 389 c/c 406 CC", "STJ REsp 1.112.743/BA"],
        documentos_em_maos: {},
        documentos_faltantes: ["ACEITE/ATESTADO", "PDF do CONTRATO"],
        nota_multa: "Multa 2% Lei 14.133/2021 art. 156, III",
        nes_spcf: {
          qtd: 348,
          classe: "OFICIAL_COMPLEMENTAR",
          exemplos: [
            { ne: "2025NE0000529", contrato_ref: "8/2021", valor: 13169.17, situacao: "Ativo" },
            { ne: "2025NE0001609", contrato_ref: "18/2021", valor: 12485.67, situacao: "Ativo" },
            { ne: "2025NE0001610", contrato_ref: "18/2021", valor: 12485.67, situacao: "Ativo" },
          ],
          observacao: "Contratos complementares com NE direta em SPCF constituem prova suficiente para cobrança (TCE-AM Res. 04/2022).",
        },
      }),
    },
  ],
};

describe("SectionProntuario", () => {
  beforeEach(() => {
    // Hidrata dashboard singleton com payload de teste
    hydrateDashboard({ ...dashboard, prontuario: payload } as any);
  });

  afterEach(() => {
    cleanup();
  });

  it("renderiza o título e a descrição", () => {
    render(<SectionProntuario />);
    expect(screen.getByText(/Prontuário de Execução/)).toBeTruthy();
    expect(screen.getByText(/Consolidação executável dos 18/)).toBeTruthy();
  });

  it("renderiza os KPIs", () => {
    render(<SectionProntuario />);
    expect(screen.getByText("R$ 29.54M")).toBeTruthy();
    expect(screen.getByText("18 instrumentos")).toBeTruthy();
  });

  it("renderiza os 2 cards e mostra número oficial", () => {
    render(<SectionProntuario />);
    expect(screen.getByText(/Contrato 22\/2014/)).toBeTruthy();
    expect(screen.getByText(/Contrato 296\/2025/)).toBeTruthy();
  });

  it("filtra por prontidão (botão PRONTO mostra só o card de 22/2014)", () => {
    render(<SectionProntuario />);
    // Há vários botões com esse texto (badges dos cards); pega o primeiro, que é o chip de filtro
    const buttons = screen.getAllByRole("button", { name: /PRONTO — execução imediata/i });
    // Filtro vem primeiro no DOM
    fireEvent.click(buttons[0]);
    expect(screen.getByText(/Contrato 22\/2014/)).toBeTruthy();
    expect(screen.queryByText(/Contrato 296\/2025/)).toBeNull();
  });

  it("busca por 'sombra' via input filtra 296/2025", () => {
    render(<SectionProntuario />);
    const input = screen.getByPlaceholderText(/Buscar/i) as HTMLInputElement;
    fireEvent.change(input, { target: { value: "296" } });
    expect(screen.getByText(/Contrato 296\/2025/)).toBeTruthy();
    expect(screen.queryByText(/Contrato 22\/2014/)).toBeNull();
  });

  it("expande a ficha ao clicar no card", () => {
    render(<SectionProntuario />);
    const card = screen.getByText(/Contrato 22\/2014/).closest("button");
    expect(card).toBeTruthy();
    fireEvent.click(card!);
    expect(screen.getByText(/Via Processual Recomendada/i)).toBeTruthy();
    expect(screen.getByText(/Execução por quantia certa/i)).toBeTruthy();
  });

  it("exibe bloco 'Cruzamento SPCF' no card OFICIAL_COMPLEMENTAR expandido (348 NEs)", () => {
    render(<SectionProntuario />);
    const card = screen.getByText(/Contrato 8\/2021/).closest("button");
    expect(card).toBeTruthy();
    fireEvent.click(card!);
    expect(screen.getByText(/Cruzamento SPCF/i)).toBeTruthy();
    expect(screen.getByText(/348 NEs localizadas/)).toBeTruthy();
    expect(screen.getByText(/2025NE0000529/)).toBeTruthy();
    expect(screen.getByText(/TCE-AM Res\. 04\/2022/)).toBeTruthy();
  });

  it("exibe bloco 'Cruzamento SPCF' vermelho no card SOMBRA expandido (0 NEs)", () => {
    render(<SectionProntuario />);
    const card = screen.getByText(/Contrato 296\/2025/).closest("button");
    expect(card).toBeTruthy();
    fireEvent.click(card!);
    expect(screen.getByText(/0 NEs localizadas/)).toBeTruthy();
    expect(screen.getByText(/enriquecimento sem causa/)).toBeTruthy();
  });

  it("NÃO exibe bloco SPCF em card OFICIAL_COMPLETO (qtd=null)", () => {
    render(<SectionProntuario />);
    const card = screen.getByText(/Contrato 22\/2014/).closest("button");
    fireEvent.click(card!);
    // bloco SPCF não aparece quando qtd=null (caso do 22/2014)
    expect(screen.queryByText(/Cruzamento SPCF/i)).toBeNull();
  });

  it("renderiza tabela de resumo por prontidão", () => {
    render(<SectionProntuario />);
    // Tabela imprime 'PRONTO' na primeira coluna
    const tabela = screen.getByRole("table");
    expect(tabela.textContent).toMatch(/PRONTO/);
    expect(tabela.textContent).toMatch(/5/);
  });
});
