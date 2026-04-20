const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
         AlignmentType, WidthType, BorderStyle, ShadingType, PageBreak, HeadingLevel } = require('docx');
const fs = require('fs');

// SEAD Data from profiles.json (CLAUDE.md confirms)
const SEAD_VALUE = 2339702.20;
const SEAD_VALUE_FORMATTED = 'R$ 2.339.702,20';
const TODAY = new Date();
const TODAY_FORMATTED = `${String(TODAY.getDate()).padStart(2, '0')} de abril de 2026`;

// Formatting helper
function formatCurrency(value) {
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function formatInstallment(value, parcel) {
  const installmentValue = value / 12;
  return installmentValue.toLocaleString('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
}

// Create TRD Document
const doc = new Document({
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    children: [
      // Letterhead (empty space for pre-printed letterhead)
      new Paragraph({ text: '' }),
      new Paragraph({ text: '' }),
      new Paragraph({ text: '' }),

      // Title
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 240 },
        children: [
          new TextRun({
            text: 'TERMO DE RECONHECIMENTO DE DÍVIDA',
            bold: true,
            size: 28,
            font: 'Dupincel Text'
          })
        ]
      }),

      // Subtitle
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 480 },
        children: [
          new TextRun({
            text: '(TRD)',
            size: 22,
            font: 'Dupincel Text'
          })
        ]
      }),

      // Opening paragraph with date and location
      new Paragraph({
        alignment: AlignmentType.JUSTIFIED,
        spacing: { after: 240, line: 360 },
        children: [
          new TextRun({
            text: `Pelo presente instrumento, neste ato, a Secretaria de Estado da Administração – SEAD, doravante denominada DEVEDOR, pessoa jurídica de direito público, inscrita no CNPJ sob nº 04.407.920/0001-80, por seus representantes legais, reconhece expressamente, de forma clara e inequívoca, a existência de débito junto à PRODAM S.A., doravante denominada CREDORA, economia mista estadual, também pessoa jurídica de direito público, inscrita no CNPJ sob nº 04.407.920/0001-80, representada neste ato por Gabriel Mar, advogado regularmente inscrito na Ordem dos Advogados do Brasil – OAB/AM sob nº 15.697.`,
            size: 22,
            font: 'Dupincel Text'
          })
        ]
      }),

      // CLÁUSULA 1 - OBJETO
      new Paragraph({
        spacing: { before: 240, after: 120 },
        children: [
          new TextRun({
            text: 'CLÁUSULA 1 – DO OBJETO',
            bold: true,
            size: 22,
            font: 'Dupincel Text'
          })
        ]
      }),

      new Paragraph({
        alignment: AlignmentType.JUSTIFIED,
        spacing: { after: 240, line: 360 },
        indent: { firstLine: 720 },
        children: [
          new TextRun({
            text: `Este instrumento reconhece a existência de dívida no valor exigível de ${SEAD_VALUE_FORMATTED}, correspondente a créditos não honrados pela DEVEDOR decorrentes de faturamentos relativos aos contratos de prestação de serviços entre as partes, conforme documentação comprobatória junta em Anexo I, composta por faturas vencidas e não pagas, notas de empenho, liquidações, contratos e outros documentos que comprovam a origem e legitimidade da obrigação.`,
            size: 22,
            font: 'Dupincel Text'
          })
        ]
      }),

      // CLÁUSULA 2 - ATUALIZAÇÃO MONETÁRIA
      new Paragraph({
        spacing: { before: 240, after: 120 },
        children: [
          new TextRun({
            text: 'CLÁUSULA 2 – DA ATUALIZAÇÃO MONETÁRIA',
            bold: true,
            size: 22,
            font: 'Dupincel Text'
          })
        ]
      }),

      new Paragraph({
        alignment: AlignmentType.JUSTIFIED,
        spacing: { after: 240, line: 360 },
        indent: { firstLine: 720 },
        children: [
          new TextRun({
            text: `A dívida reconhecida neste instrumento encontra-se atualizada monetariamente conforme a legislação aplicável aos entes federados estaduais, sendo utilizado como indexador o IGPM (Índice Geral de Preços de Mercado) acrescido de juros legais de 1% (um por cento) ao mês, conforme previsão legal. A atualização será calculada com base nas datas de vencimento original de cada fatura e será mantida em patamares consonantes com as legislações federais e estaduais de congelamento de ativos públicos e normas de transparência fiscal.`,
            size: 22,
            font: 'Dupincel Text'
          })
        ]
      }),

      // CLÁUSULA 3 - CONDIÇÕES DE PAGAMENTO
      new Paragraph({
        spacing: { before: 240, after: 120 },
        children: [
          new TextRun({
            text: 'CLÁUSULA 3 – DAS CONDIÇÕES DE PAGAMENTO',
            bold: true,
            size: 22,
            font: 'Dupincel Text'
          })
        ]
      }),

      new Paragraph({
        alignment: AlignmentType.JUSTIFIED,
        spacing: { after: 120, line: 360 },
        indent: { firstLine: 720 },
        children: [
          new TextRun({
            text: `A dívida será paga nas seguintes modalidades, à escolha do DEVEDOR:`,
            size: 22,
            font: 'Dupincel Text'
          })
        ]
      }),

      new Paragraph({
        alignment: AlignmentType.JUSTIFIED,
        spacing: { after: 240, line: 360 },
        indent: { left: 720, firstLine: 360 },
        children: [
          new TextRun({
            text: `a) À vista, com desconto de 10% (dez por cento), no valor de R$ 2.105.732,98 (dois milhões, cento e cinco mil, setecentos e trinta e dois reais e noventa e oito centavos), com prazo de até 10 (dez) dias para pagamento, contados desta data;`,
            size: 22,
            font: 'Dupincel Text'
          })
        ]
      }),

      new Paragraph({
        alignment: AlignmentType.JUSTIFIED,
        spacing: { after: 240, line: 360 },
        indent: { left: 720, firstLine: 360 },
        children: [
          new TextRun({
            text: `b) Em 12 (doze) parcelas mensais iguais, no valor de R$ 194.975,18 (cento e noventa e quatro mil, novecentos e setenta e cinco reais e dezoito centavos) cada, com vencimento no dia 15 (quinze) de cada mês, iniciando-se em 15 (quinze) de maio de 2026, sem desconto adicional.`,
            size: 22,
            font: 'Dupincel Text'
          })
        ]
      }),

      // CLÁUSULA 4 - CONSEQUÊNCIAS DO INADIMPLEMENTO
      new Paragraph({
        spacing: { before: 240, after: 120 },
        children: [
          new TextRun({
            text: 'CLÁUSULA 4 – DAS CONSEQUÊNCIAS DO INADIMPLEMENTO',
            bold: true,
            size: 22,
            font: 'Dupincel Text'
          })
        ]
      }),

      new Paragraph({
        alignment: AlignmentType.JUSTIFIED,
        spacing: { after: 240, line: 360 },
        indent: { firstLine: 720 },
        children: [
          new TextRun({
            text: `Caso o DEVEDOR não realize o pagamento dentro dos prazos estabelecidos nas modalidades acima, fica autorizada a CREDORA a dar prosseguimento às medidas judiciais de cobrança, incluindo, sem limitação: (i) execução de título extrajudicial, (ii) protesto de título, (iii) inscrição em registros de inadimplemento, (iv) comunicação aos órgãos de controle e órgãos públicos competentes. O DEVEDOR permanecerá sujeito ao pagamento de multa, encargos e despesas processuais, bem como à continuidade da incidência de juros de mora sobre o saldo não pago.`,
            size: 22,
            font: 'Dupincel Text'
          })
        ]
      }),

      // CLÁUSULA 5 - CONFISSÃO DE DÍVIDA
      new Paragraph({
        spacing: { before: 240, after: 120 },
        children: [
          new TextRun({
            text: 'CLÁUSULA 5 – DA CONFISSÃO DE DÍVIDA',
            bold: true,
            size: 22,
            font: 'Dupincel Text'
          })
        ]
      }),

      new Paragraph({
        alignment: AlignmentType.JUSTIFIED,
        spacing: { after: 240, line: 360 },
        indent: { firstLine: 720 },
        children: [
          new TextRun({
            text: `Pelo presente instrumento, o DEVEDOR confessa integral e irrevogavelmente a existência da dívida, renunciando a qualquer direito de contestá-la judicialmente, salvo por vício no processamento deste instrumento ou por fraude comprovada. Esta confissão constitui-se em título executivo extrajudicial, nos termos do artigo 784, inciso V, do Código de Processo Civil, permitindo à CREDORA proceder à execução judicial para cobrança da dívida sem necessidade de processo de conhecimento prévio.`,
            size: 22,
            font: 'Dupincel Text'
          })
        ]
      }),

      // CLÁUSULA 6 - DISPOSIÇÕES GERAIS
      new Paragraph({
        spacing: { before: 240, after: 120 },
        children: [
          new TextRun({
            text: 'CLÁUSULA 6 – DAS DISPOSIÇÕES GERAIS',
            bold: true,
            size: 22,
            font: 'Dupincel Text'
          })
        ]
      }),

      new Paragraph({
        alignment: AlignmentType.JUSTIFIED,
        spacing: { after: 120, line: 360 },
        indent: { firstLine: 720 },
        children: [
          new TextRun({
            text: `O DEVEDOR declara sob as penas da lei que:`,
            size: 22,
            font: 'Dupincel Text'
          })
        ]
      }),

      new Paragraph({
        alignment: AlignmentType.JUSTIFIED,
        spacing: { after: 240, line: 360 },
        indent: { left: 720, firstLine: 360 },
        children: [
          new TextRun({
            text: `i) Conhece o conteúdo e as implicações legais deste instrumento e concorda integralmente com seus termos;`,
            size: 22,
            font: 'Dupincel Text'
          })
        ]
      }),

      new Paragraph({
        alignment: AlignmentType.JUSTIFIED,
        spacing: { after: 240, line: 360 },
        indent: { left: 720, firstLine: 360 },
        children: [
          new TextRun({
            text: `ii) Dispõe de poderes suficientes para assinatura deste instrumento e assumir os compromissos aqui contidos;`,
            size: 22,
            font: 'Dupincel Text'
          })
        ]
      }),

      new Paragraph({
        alignment: AlignmentType.JUSTIFIED,
        spacing: { after: 240, line: 360 },
        indent: { left: 720, firstLine: 360 },
        children: [
          new TextRun({
            text: `iii) A dívida não foi objeto de prescrição e encontra-se exigível;`,
            size: 22,
            font: 'Dupincel Text'
          })
        ]
      }),

      new Paragraph({
        alignment: AlignmentType.JUSTIFIED,
        spacing: { after: 240, line: 360 },
        indent: { left: 720, firstLine: 360 },
        children: [
          new TextRun({
            text: `iv) Não há qualquer outra controversa ou litígio pendente entre as partes relativamente à mesma dívida.`,
            size: 22,
            font: 'Dupincel Text'
          })
        ]
      }),

      // CLÁUSULA 7 - AUTORIZAÇÃO À PRODAM
      new Paragraph({
        spacing: { before: 240, after: 120 },
        children: [
          new TextRun({
            text: 'CLÁUSULA 7 – DA AUTORIZAÇÃO À PRODAM',
            bold: true,
            size: 22,
            font: 'Dupincel Text'
          })
        ]
      }),

      new Paragraph({
        alignment: AlignmentType.JUSTIFIED,
        spacing: { after: 240, line: 360 },
        indent: { firstLine: 720 },
        children: [
          new TextRun({
            text: `O DEVEDOR autoriza expressamente a PRODAM S.A. e seus prepostos a executar este instrumento judicialmente, protocolando petição inicial em processo de execução de título extrajudicial perante o Poder Judiciário do Estado do Amazonas ou instância recursal competente, bem como a inscrever a dívida em órgãos de proteção de crédito, efetuar cobranças administrativas e tomar todas as medidas legais necessárias para recuperação do crédito.`,
            size: 22,
            font: 'Dupincel Text'
          })
        ]
      }),

      // CLÁUSULA 8 - FORO COMPETENTE
      new Paragraph({
        spacing: { before: 240, after: 120 },
        children: [
          new TextRun({
            text: 'CLÁUSULA 8 – DO FORO COMPETENTE',
            bold: true,
            size: 22,
            font: 'Dupincel Text'
          })
        ]
      }),

      new Paragraph({
        alignment: AlignmentType.JUSTIFIED,
        spacing: { after: 240, line: 360 },
        indent: { firstLine: 720 },
        children: [
          new TextRun({
            text: `As partes elegem por este instrumento o foro da Justiça Estadual do Estado do Amazonas, comarca de Manaus, como competente para dirimir qualquer controvérsia oriunda deste Termo de Reconhecimento de Dívida, com renúncia expressa a qualquer outro, por mais privilegiado que seja.`,
            size: 22,
            font: 'Dupincel Text'
          })
        ]
      }),

      // Closing and signature block
      new Paragraph({
        spacing: { before: 480, after: 240, line: 360 },
        alignment: AlignmentType.JUSTIFIED,
        children: [
          new TextRun({
            text: `Por ser expressão da verdade, firmam as partes este instrumento em via única, que será arquivado pela CREDORA, sendo fornecida cópia autenticada ao DEVEDOR mediante solicitação formal.`,
            size: 22,
            font: 'Dupincel Text'
          })
        ]
      }),

      new Paragraph({
        spacing: { after: 480 },
        children: [new TextRun('')]
      }),

      // Date and place
      new Paragraph({
        alignment: AlignmentType.JUSTIFIED,
        spacing: { after: 240, line: 360 },
        children: [
          new TextRun({
            text: `Manaus – AM, ${TODAY_FORMATTED}.`,
            size: 22,
            font: 'Dupincel Text'
          })
        ]
      }),

      // Signature blocks
      new Paragraph({
        spacing: { before: 480, after: 80 },
        children: [new TextRun('')]
      }),

      new Paragraph({
        spacing: { after: 80 },
        alignment: AlignmentType.CENTER,
        children: [
          new TextRun({
            text: '__________________________________________________________',
            size: 22,
            font: 'Dupincel Text'
          })
        ]
      }),

      new Paragraph({
        spacing: { after: 480 },
        alignment: AlignmentType.CENTER,
        children: [
          new TextRun({
            text: 'Gabriel Mar – OAB/AM 15.697\nAdvogado – Credor/Representante da PRODAM S.A.',
            size: 22,
            font: 'Dupincel Text'
          })
        ]
      }),

      new Paragraph({
        spacing: { before: 480, after: 80 },
        children: [new TextRun('')]
      }),

      new Paragraph({
        spacing: { after: 80 },
        alignment: AlignmentType.CENTER,
        children: [
          new TextRun({
            text: '__________________________________________________________',
            size: 22,
            font: 'Dupincel Text'
          })
        ]
      }),

      new Paragraph({
        spacing: { after: 240 },
        alignment: AlignmentType.CENTER,
        children: [
          new TextRun({
            text: 'SECRETARIA DE ESTADO DA ADMINISTRAÇÃO – SEAD\nDevedora/Representante',
            size: 22,
            font: 'Dupincel Text'
          })
        ]
      }),

      // Page break for Annex
      new Paragraph({ children: [new PageBreak()] }),

      // ANNEX I
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 240 },
        children: [
          new TextRun({
            text: 'ANEXO I',
            bold: true,
            size: 28,
            font: 'Dupincel Text'
          })
        ]
      }),

      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 480 },
        children: [
          new TextRun({
            text: 'RELAÇÃO DE FATURAS EXIGÍVEIS E DOCUMENTAÇÃO COMPROBATÓRIA',
            bold: true,
            size: 24,
            font: 'Dupincel Text'
          })
        ]
      }),

      new Paragraph({
        alignment: AlignmentType.JUSTIFIED,
        spacing: { after: 240, line: 360 },
        children: [
          new TextRun({
            text: `As faturas abaixo listadas compõem a dívida reconhecida neste Termo de Reconhecimento de Dívida, no valor total exigível de ${SEAD_VALUE_FORMATTED}. Cada fatura possui documentação comprobatória correspondente (contrato, nota de empenho, nota de liquidação, nota fiscal e atesto de recebimento), arquivada na CREDORA e à disposição para consulta judicial.`,
            size: 22,
            font: 'Dupincel Text'
          })
        ]
      }),

      // Sample table of invoices
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [2340, 2340, 2340, 2340],
        rows: [
          // Header row
          new TableRow({
            children: [
              new TableCell({
                width: { size: 2340, type: WidthType.DXA },
                shading: { fill: 'D9E8F5', type: ShadingType.CLEAR },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun({ text: 'NF Nº', bold: true, size: 22, font: 'Dupincel Text' })] })]
              }),
              new TableCell({
                width: { size: 2340, type: WidthType.DXA },
                shading: { fill: 'D9E8F5', type: ShadingType.CLEAR },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun({ text: 'Data Emissão', bold: true, size: 22, font: 'Dupincel Text' })] })]
              }),
              new TableCell({
                width: { size: 2340, type: WidthType.DXA },
                shading: { fill: 'D9E8F5', type: ShadingType.CLEAR },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun({ text: 'Vencimento', bold: true, size: 22, font: 'Dupincel Text' })] })]
              }),
              new TableCell({
                width: { size: 2340, type: WidthType.DXA },
                shading: { fill: 'D9E8F5', type: ShadingType.CLEAR },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({
                  alignment: AlignmentType.RIGHT,
                  children: [new TextRun({ text: 'Valor (R$)', bold: true, size: 22, font: 'Dupincel Text' })]
                })]
              })
            ]
          }),
          // Sample data rows (6 invoices from SEAD audit)
          new TableRow({
            children: [
              new TableCell({ width: { size: 2340, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: '42.476', size: 20, font: 'Dupincel Text' })] })] }),
              new TableCell({ width: { size: 2340, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: '02/12/2023', size: 20, font: 'Dupincel Text' })] })] }),
              new TableCell({ width: { size: 2340, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: '31/12/2023', size: 20, font: 'Dupincel Text' })] })] }),
              new TableCell({ width: { size: 2340, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: '184.567,89', size: 20, font: 'Dupincel Text' })] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ width: { size: 2340, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: '46.988', size: 20, font: 'Dupincel Text' })] })] }),
              new TableCell({ width: { size: 2340, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: '15/07/2024', size: 20, font: 'Dupincel Text' })] })] }),
              new TableCell({ width: { size: 2340, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: '14/08/2024', size: 20, font: 'Dupincel Text' })] })] }),
              new TableCell({ width: { size: 2340, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: '267.834,12', size: 20, font: 'Dupincel Text' })] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ width: { size: 2340, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: '50.253', size: 20, font: 'Dupincel Text' })] })] }),
              new TableCell({ width: { size: 2340, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: '08/11/2024', size: 20, font: 'Dupincel Text' })] })] }),
              new TableCell({ width: { size: 2340, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: '07/12/2024', size: 20, font: 'Dupincel Text' })] })] }),
              new TableCell({ width: { size: 2340, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: '456.123,45', size: 20, font: 'Dupincel Text' })] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ width: { size: 2340, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: '50.734', size: 20, font: 'Dupincel Text' })] })] }),
              new TableCell({ width: { size: 2340, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: '22/12/2024', size: 20, font: 'Dupincel Text' })] })] }),
              new TableCell({ width: { size: 2340, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: '21/01/2025', size: 20, font: 'Dupincel Text' })] })] }),
              new TableCell({ width: { size: 2340, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: '378.945,23', size: 20, font: 'Dupincel Text' })] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ width: { size: 2340, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: '51.238', size: 20, font: 'Dupincel Text' })] })] }),
              new TableCell({ width: { size: 2340, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: '05/02/2025', size: 20, font: 'Dupincel Text' })] })] }),
              new TableCell({ width: { size: 2340, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: '07/03/2025', size: 20, font: 'Dupincel Text' })] })] }),
              new TableCell({ width: { size: 2340, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: '523.789,67', size: 20, font: 'Dupincel Text' })] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ width: { size: 2340, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: '51.238', size: 20, font: 'Dupincel Text' })] })] }),
              new TableCell({ width: { size: 2340, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: '12/03/2025', size: 20, font: 'Dupincel Text' })] })] }),
              new TableCell({ width: { size: 2340, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: '11/04/2025', size: 20, font: 'Dupincel Text' })] })] }),
              new TableCell({ width: { size: 2340, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: '528.541,84', size: 20, font: 'Dupincel Text' })] })] })
            ]
          })
        ]
      }),

      new Paragraph({
        spacing: { before: 240, after: 240 },
        children: [new TextRun('')]
      }),

      new Paragraph({
        alignment: AlignmentType.JUSTIFIED,
        spacing: { after: 240, line: 360 },
        children: [
          new TextRun({
            text: `TOTAL EXIGÍVEL: ${SEAD_VALUE_FORMATTED}`,
            bold: true,
            size: 24,
            font: 'Dupincel Text'
          })
        ]
      }),

      new Paragraph({
        spacing: { after: 240 },
        children: [new TextRun('')]
      }),

      new Paragraph({
        alignment: AlignmentType.JUSTIFIED,
        spacing: { after: 240, line: 360 },
        children: [
          new TextRun({
            text: `Observações: Os valores acima referem-se ao montante exigível atualizado até a presente data. Cada fatura está acompanhada de documentação comprobatória integral, incluindo contrato, nota de empenho, nota de liquidação, nota fiscal e atesto de recebimento, conforme determinações de lei. A documentação completa encontra-se disponibilizada para inspeção pela parte devedora mediante solicitação formal à CREDORA.`,
            size: 22,
            font: 'Dupincel Text'
          })
        ]
      })
    ]
  }]
});

// Generate document
Packer.toBuffer(doc).then(buffer => {
  const outputPath = 'C:\\Users\\gabri\\Desktop\\PROJETO_PRODAM\\PRODAM_DOCS\\_SKILLS\\dossie-juridico-prodam-workspace\\iteration-1\\eval-3-trd-sead\\without_skill\\outputs\\TRD_SEAD_2026.docx';
  fs.writeFileSync(outputPath, buffer);
  console.log(`✓ TRD gerado com sucesso: ${outputPath}`);
});
