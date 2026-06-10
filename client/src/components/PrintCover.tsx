/**
 * PrintCover — Sprint 2 Estrutural S5
 *
 * Capa institucional + sumário executivo exibidos apenas em modo impressão
 * (print:block). Desenhados para um dossiê forense em A4 retrato, com
 * paginação e watermark CONFIDENCIAL aplicados via CSS @page + body::after
 * definidos em index.css.
 *
 * Seções desta peça (cada uma force page-break-after):
 *   1. Frontispício — brasão, título, data-base, devedor/credor, valor C1
 *   2. Sumário Executivo — síntese + 3 takeaways numéricos + parecer final
 *   3. Índice Navegável — lista das 22 seções com âncora/número de página
 *   4. Ficha Técnica do Dossiê — metadados de auditoria, fontes, metodologia
 */
import { NAV_SECTIONS } from "@/data/types";

export default function PrintCover() {
  const dataBase = "16/04/2026";
  const devedor = "DETRAN/AM · CNPJ 04.224.028/0001-63";
  const credor = "PRODAM · CNPJ 04.407.920/0001-80";
  const numeroProcesso = "Contrato 002/2026 — Brandão Ozores Advogados Associados";
  const versao = "v10 · Dossier Edition";

  return (
    <div className="print-cover-wrapper hidden print:block">
      {/* ===================================================
          PÁGINA 1 — FRONTISPÍCIO
          ===================================================
          Capa editorial institucional: ornamento superior, título principal,
          metadados legais e régua inferior com selo de auditoria. */}
      <section className="print-page print-frontispiece">
        <header className="print-cover-header">
          <div className="print-ornament">◆ ◆ ◆</div>
          <div className="print-firm small-caps">
            Brandão Ozores Advogados Associados · OAB/AM 15.697
          </div>
        </header>

        <div className="print-hero">
          <div className="print-eyebrow small-caps">Auditoria Forense de Cobrança Administrativa</div>
          <h1 className="print-title font-display">
            DETRAN
            <span className="print-title-divider"> · </span>
            <em>Amazonas</em>
          </h1>
          <p className="print-subtitle">
            Dossiê consolidado da relação jurídica DETRAN/AM × PRODAM — exigibilidade, prescrição
            qüinqüenal, atualização monetária e estratégia executiva.
          </p>
          <div className="print-goldrule" />
        </div>

        <div className="print-meta-grid">
          <Field label="Data-base" value={dataBase} />
          <Field label="Versão do dossiê" value={versao} />
          <Field label="Devedor" value={devedor} />
          <Field label="Credora" value={credor} />
          <Field label="Valor principal · C1 SELIC" value="R$ 28.142.624,30" strong />
          <Field label="Saldo original auditado" value="R$ 21.434.211,45" />
          <Field label="Score forense 12D" value="A+ · 94,0 / 100" strong />
          <Field label="Marcos interruptivos" value="148 atos (Art. 202 VI CC)" />
          <Field label="Contratos / Regimes" value="18 contratos · 6 regimes" />
          <Field label="Título executivo" value="Art. 784 CPC · NE + NL + NF + Aceite" />
        </div>

        <footer className="print-cover-footer">
          <div className="print-goldline" />
          <div className="print-signature">
            <div className="print-signature-label small-caps">Responsável técnico</div>
            <div className="print-signature-name">{numeroProcesso}</div>
          </div>
          <div className="print-confidential small-caps">
            Documento confidencial · uso interno · sigilo profissional
          </div>
        </footer>
      </section>

      {/* ===================================================
          PÁGINA 2 — SUMÁRIO EXECUTIVO (narrativa + takeaways)
          =================================================== */}
      <section className="print-page">
        <h2 className="print-section-title font-display">Sumário Executivo</h2>
        <div className="print-goldline" />

        <div className="print-narrative">
          <p>
            <span className="print-dropcap">O</span> dossiê consolida a relação creditória entre o{" "}
            <strong>Departamento Estadual de Trânsito do Amazonas</strong> e a <strong>PRODAM</strong>,
            contemplando <strong>202 faturas</strong> auditadas em <strong>18 contratos</strong> ativos e{" "}
            <strong>6 regimes jurídicos</strong>. O saldo devedor original monta a{" "}
            <strong>R$ 21.434.211,45</strong>, atualizado pelo cenário principal (SELIC) a{" "}
            <strong>R$ 28.142.624,30</strong> — correção de <strong>31,3%</strong> conforme Art. 406 do
            Código Civil (redação da Lei 14.905/2024) e Tema 99 do STJ.
          </p>
          <p>
            A cadeia documental é robusta: cada NE representa ato inequívoco de reconhecimento do débito
            (Art. 202 VI CC), interrompendo a prescrição quinquenal do Decreto 20.910/1932 e conferindo
            à PRODAM plena legitimidade ativa para execução forçada nos termos do Art. 784 do CPC. A
            auditoria identificou <strong>148 marcos interruptivos</strong>, dos quais a maioria apresenta
            cadeia FORTE ou COMPLETA com documentos fiscais e administrativos correspondentes.
          </p>
          <p>
            A defesa jurídica se sustenta em três pilares: (i) título executivo extrajudicial perfeito;
            (ii) prescrição vigente em todas as faturas cobráveis; (iii) possibilidade de execução por RPV
            individualizado (Art. 100 §3º CF/88), permitindo rito mais célere e menor exposição judicial.
            O Score Forense 12D atinge <strong>94,0/100 (A+)</strong>, indicativo de caso de excelência
            com risco reputacional e jurídico minimizados.
          </p>
        </div>

        <div className="print-takeaways">
          <Takeaway label="Correção acumulada" value="+31,3%" note="R$ 6,7 M em encargos sobre o principal" />
          <Takeaway label="Regime dominante" value="Silente Admin." note="R$ 12,4 M · 44% do total atualizado" />
          <Takeaway label="Faturas cobráveis" value="202" note="100% dentro do prazo qüinqüenal" />
        </div>

        <div className="print-callout">
          <div className="small-caps print-callout-label">Parecer conclusivo</div>
          <p>
            Recomenda-se o ajuizamento imediato da execução forçada pelo cenário C1 SELIC, com protesto
            extrajudicial prévio de título como alternativa de impulso negocial. O caso apresenta
            viabilidade jurídica excepcional e expectativa de resolução dentro de 24–36 meses.
          </p>
        </div>
      </section>

      {/* ===================================================
          PÁGINA 3 — ÍNDICE NAVEGÁVEL
          =================================================== */}
      <section className="print-page">
        <h2 className="print-section-title font-display">Índice do Dossiê</h2>
        <div className="print-goldline" />
        <p className="print-toc-note">
          As seções a seguir compõem o corpo do dossiê. Cada seção inicia em nova página no modo
          impressão completa.
        </p>

        <ol className="print-toc">
          {NAV_SECTIONS.flatMap((grp, gi) => [
            <li key={`grp-${gi}`} className="print-toc-group">
              <span className="small-caps">{grp.group}</span>
            </li>,
            ...grp.items.map((item, ii) => {
              const globalIdx = NAV_SECTIONS.slice(0, gi).reduce((s, g) => s + g.items.length, 0) + ii + 1;
              return (
                <li key={item.id} className="print-toc-item">
                  <span className="print-toc-num tabular-nums">{String(globalIdx).padStart(2, "0")}</span>
                  <span className="print-toc-label">{item.label}</span>
                  <span className="print-toc-dots" aria-hidden />
                  <span className="print-toc-ref font-mono">§{globalIdx}</span>
                </li>
              );
            }),
          ])}
        </ol>
      </section>

      {/* ===================================================
          PÁGINA 4 — FICHA TÉCNICA
          =================================================== */}
      <section className="print-page">
        <h2 className="print-section-title font-display">Ficha Técnica do Dossiê</h2>
        <div className="print-goldline" />

        <dl className="print-meta-grid">
          <Field label="Escritório responsável" value="Brandão Ozores Advogados Associados" strong />
          <Field label="Registro OAB" value="OAB/AM 15.697" />
          <Field label="Contrato de honorários" value="002/2026" />
          <Field label="Tipo de engajamento" value="Êxito + aviso prévio" />
          <Field label="Fontes primárias" value="prodam.db (AFI/SPCF), OCR de documentação escaneada" />
          <Field label="Metodologia de atualização" value="BCB/SGS (SELIC 4189, Poupança 195)" />
          <Field label="Cenários modelados" value="C1 SELIC · C2 Poupança · C3 1% a.m." />
          <Field label="Normas aplicáveis" value="CF/88 Art. 100 · CC Arts. 202, 406 · CPC Arts. 784, 910 · Dec. 20.910/1932" />
          <Field label="Jurisprudência" value="STJ Temas 99, 810 · Súmula 106 STJ · Lei 14.905/2024" />
          <Field label="Auditoria técnica" value="202 faturas · 481 NEs · 18 contratos · 148 marcos interruptivos" />
        </dl>

        <div className="print-sign-block">
          <div className="print-sign-line" />
          <div className="print-sign-who font-display">Dr. Fabiano Brandão Ozores</div>
          <div className="print-sign-role small-caps">Advogado responsável técnico · OAB/AM 15.697</div>
        </div>
      </section>
    </div>
  );
}

function Field({ label, value, strong = false }: { label: string; value: string; strong?: boolean }) {
  return (
    <>
      <dt className="print-meta-label small-caps">{label}</dt>
      <dd className={`print-meta-value ${strong ? "print-meta-strong" : ""}`}>{value}</dd>
    </>
  );
}

function Takeaway({ label, value, note }: { label: string; value: string; note: string }) {
  return (
    <div className="print-takeaway">
      <div className="print-takeaway-label small-caps">{label}</div>
      <div className="print-takeaway-value font-display tabular-nums">{value}</div>
      <div className="print-takeaway-note">{note}</div>
    </div>
  );
}
