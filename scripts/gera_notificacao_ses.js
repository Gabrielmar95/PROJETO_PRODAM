#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { Document, Packer, Paragraph, TextRun, AlignmentType, HeadingLevel } = require('docx');

// ============================================================
// BLOQUEIO MANUAL — adicionado em 2026-05-10
// Motivo: numeração "NOT/001/2026" hardcoded colide com a NE 001/2026
// DETRAN já protocolada via ICP-Brasil em 20/04/2026.
// Para destravar: substituir todas as ocorrências de "NOT/001/2026"
// por numeração SES não conflitante e remover este bloqueio.
// ============================================================
throw new Error("[BLOQUEADO] Numeração NOT/001/2026 colide com NE DETRAN. Ver bloco de comentário no topo do arquivo.");

const profilesPath = "C:\\Users\\gabri\\Desktop\\PROJETO_PRODAM\\PRODAM_DOCS\\profiles.json";
const outputDir = "C:\\Users\\gabri\\Desktop\\PROJETO_PRODAM\\PRODAM_DOCS\\_SKILLS\\dossie-juridico-prodam-workspace\\iteration-1\\eval-2-notificacao-ses\\with_skill\\outputs";
const outputFile = path.join(outputDir, "NOT_SES_SUSAM_001_2026.docx");

// Create output directory
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

// Load data
const profiles = JSON.parse(fs.readFileSync(profilesPath, 'utf8'));
const dados = profiles["SES/SUSAM"];

const valExig = parseFloat(dados.val_exig);
const valExigFmt = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(valExig);

const paragrafos = [
  // Título
  new Paragraph({
    text: "NOTIFICAÇÃO EXTRAJUDICIAL",
    alignment: AlignmentType.CENTER,
    spacing: { before: 200, after: 200 },
    bold: true,
    size: 28,
    color: "1F3864"
  }),

  // Separador
  new Paragraph({
    text: "————————————————————",
    alignment: AlignmentType.CENTER,
    spacing: { after: 200 },
    color: "B8963E"
  }),

  // Número e data
  new Paragraph({
    text: "NOT/001/2026",
    alignment: AlignmentType.CENTER,
    spacing: { after: 100 },
    bold: true
  }),

  new Paragraph({
    text: `Manaus, ${new Date().toLocaleDateString('pt-BR', { year: 'numeric', month: 'long', day: 'numeric' })}.`,
    alignment: AlignmentType.RIGHT,
    spacing: { after: 300 }
  }),

  // Destinatário
  new Paragraph({
    text: "DESTINATÁRIO",
    bold: true,
    spacing: { before: 300, after: 100 }
  }),

  new Paragraph({
    children: [
      new TextRun({ text: "Secretaria de Saúde do Amazonas / Fundação de Medicina Tropical", bold: true }),
      new TextRun({ text: "\nCNPJ: 00.697.295/0001-05\nManaus, Amazonas" })
    ],
    spacing: { after: 300 }
  }),

  // Assunto
  new Paragraph({
    text: "ASSUNTO",
    bold: true,
    spacing: { before: 300, after: 100 }
  }),

  new Paragraph({
    text: "Notificação para pagamento de dívida vencida conforme art. 784 do Código de Processo Civil.",
    spacing: { after: 300 },
    alignment: AlignmentType.JUSTIFIED
  }),

  // Conteúdo
  new Paragraph({
    text: "CONTEÚDO",
    bold: true,
    spacing: { before: 300, after: 100 }
  }),

  // Parágrafo introdutório
  new Paragraph({
    children: [
      new TextRun("A "),
      new TextRun({ text: "Gabriel Mar Sociedade Individual de Advocacia", smallCaps: true }),
      new TextRun(", agindo como representante legal de "),
      new TextRun({ text: "PRODAM S.A.", bold: true }),
      new TextRun(" (CNPJ "),
      new TextRun({ text: "04.407.920/0001-80", bold: true }),
      new TextRun("), vem, por este meio, ")
    ],
    spacing: { after: 200 },
    alignment: AlignmentType.JUSTIFIED
  }),

  // Notificar
  new Paragraph({
    children: [
      new TextRun({ text: "NOTIFICAR", bold: true, caps: true }),
      new TextRun(" a "),
      new TextRun({ text: "SES/SUSAM", bold: true }),
      new TextRun(" do débito em aberto de ")
    ],
    spacing: { after: 100 },
    alignment: AlignmentType.JUSTIFIED
  }),

  new Paragraph({
    children: [
      new TextRun({ text: `${valExigFmt} (quatorze milhões, setecentos e quarenta e oito mil, quarenta e oito reais e noventa e seis centavos)`, bold: true }),
      new TextRun(", referente a faturas vencidas não pagas, resultante de contratações legítimas de serviços.")
    ],
    spacing: { after: 300 },
    alignment: AlignmentType.JUSTIFIED
  }),

  // Fundamentos
  new Paragraph({
    text: "FUNDAMENTOS JURÍDICOS",
    bold: true,
    spacing: { before: 300, after: 100 }
  }),

  new Paragraph({
    children: [
      new TextRun({ text: "I. ", bold: true }),
      new TextRun("A notificação fundamenta-se no art. 784 do Código de Processo Civil, que admite execução extrajudicial contra devedor que reconhece a dívida, bem como no reconhecimento tácito evidenciado por empenhos, notas de liquidação e aceites técnicos.")
    ],
    spacing: { after: 150 },
    alignment: AlignmentType.JUSTIFIED,
    indent: { left: 720, hanging: 360 }
  }),

  new Paragraph({
    children: [
      new TextRun({ text: "II. ", bold: true }),
      new TextRun("O valor referido encontra-se devidamente atualizado conforme índice SELIC, em conformidade com a Lei 14.905/2024 e os arts. 404 a 406 do Código Civil.")
    ],
    spacing: { after: 150 },
    alignment: AlignmentType.JUSTIFIED,
    indent: { left: 720, hanging: 360 }
  }),

  new Paragraph({
    children: [
      new TextRun({ text: "III. ", bold: true }),
      new TextRun("A composição documental (contrato + empenho + nota de liquidação + aceite) constitui título executivo extrajudicial, conforme jurisprudência consolidada (REsp 793.969/RJ, Rel. p/ acórdão Min. José Delgado; Teori Zavascki vencido).")
    ],
    spacing: { after: 300 },
    alignment: AlignmentType.JUSTIFIED,
    indent: { left: 720, hanging: 360 }
  }),

  // Prazo
  new Paragraph({
    text: "PRAZO PARA PAGAMENTO",
    bold: true,
    spacing: { before: 300, after: 100 }
  }),

  new Paragraph({
    children: [
      new TextRun("Fica a "),
      new TextRun({ text: "SES/SUSAM", bold: true }),
      new TextRun(" notificada para que proceda ao pagamento da dívida no prazo de "),
      new TextRun({ text: "15 (quinze) dias úteis", bold: true }),
      new TextRun(" contados do recebimento desta notificação, sob pena de ajuizamento de ação executiva.")
    ],
    spacing: { after: 300 },
    alignment: AlignmentType.JUSTIFIED
  }),

  // Alerta prescrição
  new Paragraph({
    text: "ALERTA — PRESCRIÇÃO IMINENTE",
    bold: true,
    spacing: { before: 300, after: 100 }
  }),

  new Paragraph({
    children: [
      new TextRun({ text: "ATENÇÃO: ", bold: true }),
      new TextRun("O direito de PRODAM prescreve em "),
      new TextRun({ text: "13 de maio de 2026", bold: true }),
      new TextRun(" (em "),
      new TextRun({ text: "29 dias", bold: true }),
      new TextRun("). Passada esta data, a cobrança será prejudicada pela fluência do prazo prescricional de 5 (cinco) anos contado do vencimento das faturas (art. 206, §5º, I do CC).")
    ],
    spacing: { after: 300 },
    alignment: AlignmentType.JUSTIFIED
  }),

  // Consequências
  new Paragraph({
    text: "CONSEQUÊNCIAS DO NÃO PAGAMENTO",
    bold: true,
    spacing: { before: 300, after: 100 }
  }),

  new Paragraph({
    children: [
      new TextRun({ text: "1. ", bold: true }),
      new TextRun("Sem resposta em 15 dias úteis: ajuizamento de ação executiva perante o Tribunal de Justiça do Estado do Amazonas, com todos os ônus processuais (custas, honorários, multa de 10%).")
    ],
    spacing: { after: 150 },
    alignment: AlignmentType.JUSTIFIED,
    indent: { left: 720, hanging: 360 }
  }),

  new Paragraph({
    children: [
      new TextRun({ text: "2. ", bold: true }),
      new TextRun("Perda da prescrição: caso o prazo de prescrição se complete (31/08/2026), PRODAM perderia todo e qualquer direito de cobrança, sem direito a regressão.")
    ],
    spacing: { after: 150 },
    alignment: AlignmentType.JUSTIFIED,
    indent: { left: 720, hanging: 360 }
  }),

  new Paragraph({
    children: [
      new TextRun({ text: "3. ", bold: true }),
      new TextRun("Regime de execução: como entidade da administração direta, a execução se dará via precatório ou Requisição de Pequeno Valor (RPV), conforme art. 100 CF.")
    ],
    spacing: { after: 300 },
    alignment: AlignmentType.JUSTIFIED,
    indent: { left: 720, hanging: 360 }
  }),

  // Acordo
  new Paragraph({
    text: "POSSIBILIDADE DE ACORDO",
    bold: true,
    spacing: { before: 300, after: 100 }
  }),

  new Paragraph({
    text: "PRODAM permanece aberta a negociações. Manifestações ou propostas de pagamento devem ser encaminhadas a este escritório no prazo supracitado.",
    spacing: { after: 300 },
    alignment: AlignmentType.JUSTIFIED
  }),

  // Foro
  new Paragraph({
    text: "FORO COMPETENTE",
    bold: true,
    spacing: { before: 300, after: 100 }
  }),

  new Paragraph({
    text: "Fica reservado o direito de PRODAM de promover execução judicial perante o Tribunal de Justiça do Estado do Amazonas (Foro de Manaus).",
    spacing: { after: 400 },
    alignment: AlignmentType.JUSTIFIED
  }),

  // Encerramento
  new Paragraph({
    text: "Respeitosamente apresentado,",
    alignment: AlignmentType.CENTER,
    spacing: { after: 400 }
  }),

  // Assinatura
  new Paragraph({
    text: "Gabriel Mar",
    alignment: AlignmentType.CENTER,
    bold: true,
    spacing: { after: 50 }
  }),

  new Paragraph({
    text: "OAB/AM 15.697",
    alignment: AlignmentType.CENTER,
    spacing: { after: 50 }
  }),

  new Paragraph({
    text: "Advogado",
    alignment: AlignmentType.CENTER,
    spacing: { after: 50 }
  }),

  new Paragraph({
    text: "Gabriel Mar Sociedade Individual de Advocacia",
    alignment: AlignmentType.CENTER,
    bold: true,
    smallCaps: true,
    spacing: { after: 50 }
  }),

  new Paragraph({
    text: "Em nome de Brandão Ozores Advogados",
    alignment: AlignmentType.CENTER
  })
];

const doc = new Document({
  sections: [{
    properties: {
      page: {
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    children: paragrafos
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync(outputFile, buffer);
  console.log(`[✓] Notificação gerada com sucesso!`);
  console.log(`    Arquivo: ${outputFile}`);
  process.exit(0);
}).catch(err => {
  console.error(`[✗] Erro ao gerar notificação:`, err);
  process.exit(1);
});
