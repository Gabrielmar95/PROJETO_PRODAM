"""Gera TRD_SES_SUSAM_2026-05-12.docx aplicando o design Brandão Ozores.

Reescreve em .docx o conteúdo aprovado do TRD em Markdown
(DOCUMENTOS_GERADOS/SES_SUSAM/TRD_SES_SUSAM_2026-05-12.md), preservando
literalidade jurídica das 8 cláusulas e usando os helpers
da skill `design-brandao-ozores`.

Pipeline (igual ao gerar_demo.py da skill, com repack via zipfile):
    1. Verificar SHA256 do template
    2. Unpack do template para tempdir
    3. Limpar settings.xml.rels + remover attachedTemplate
    4. Substituir <w:body>...</w:body> via helpers do gerador.py
    5. Substituir footer2.xml com footer_paginacao()
    6. Repack via zipfile (sem pack.py externo)
    7. Verificar SHA256 do template (não pode ter mudado)

NÃO altera profiles.json nem outros artefatos jurídicos.
NÃO toca o .md aprovado (continua sendo a fonte de auditoria do conteúdo).
"""
from __future__ import annotations

import hashlib
import logging
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

SKILL_ROOT = Path(r"C:\Users\gabri\.claude\skills\design-brandao-ozores")
sys.path.insert(0, str(SKILL_ROOT / "scripts"))
import gerador  # noqa: E402
from gerador import (  # noqa: E402
    titulo, separador_dourado, secao, corpo, alinea,
    caixa_sintese, footer_paginacao,
    verificacao_hash_template, reset_invariantes,
    rpr, run, para,
    COR_TEXTO, COR_DOURADO,
)

TEMPLATE = SKILL_ROOT / "template" / "Ppael_timbrado_brandao_ozores.docx"
OUTPUT = Path(
    r"C:\Users\gabri\Desktop\PROJETO_PRODAM\DOCUMENTOS_GERADOS\SES_SUSAM\TRD_SES_SUSAM_2026-05-12.docx"
)


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# ===========================================================================
# Helpers locais — tabela de valor consolidado (gerador.py não tem `tabela()`)
# ===========================================================================
def linha_tabela(label: str, valor: str, *, bold_valor: bool = False) -> str:
    """Linha tipo 'Label .................. R$ X' usando tab decimal.
    Mantém o padrão tipográfico (sem bullet/badge), só Bold no valor opcional.
    """
    return para(
        [
            run(label, size=22, color=COR_TEXTO),
            run("\t", size=22, color=COR_TEXTO),
            run(valor, size=22, bold=bold_valor, color=COR_TEXTO),
        ],
        align="both",
        indent_first=0,
        indent_left=300,
        indent_right=300,
        before=0,
        after=60,
        line=300,
    )


# ===========================================================================
# Composição do body (8 cláusulas literais do .md aprovado em 12/05/2026)
# ===========================================================================
def montar_corpo() -> str:
    reset_invariantes()
    out: list[str] = []

    # ---- Cabeçalho ----
    out.append(titulo("Termo de Reconhecimento de Dívida"))
    out.append(separador_dourado())

    out.append(corpo([
        ("Ref.: ", {"bold": True}),
        ("Secretaria de Estado de Saúde do Amazonas / SUSAM. Contratos administrativos identificados na pasta contratual da PRODAM.", {}),
    ]))
    out.append(corpo([
        ("Data-base do cálculo: ", {"bold": True}),
        ("12 de maio de 2026.", {}),
    ]))
    out.append(corpo([
        ("Instrumento extrajudicial fundado em: ", {"bold": True}),
        ("art. 784 do CPC (rol exemplificativo); art. 202, VI, do Código Civil; Súmula 339/STJ; REsp 793.969/RJ (Rel. p/ acórdão Min. José Delgado).", {}),
    ]))

    out.append(caixa_sintese([
        ("Devedora", "SES/SUSAM (CNPJ 00.697.295/0001-05) — administração direta estadual"),
        ("Faturas", "82 (oitenta e duas) — 3 Tier 1 + 79 Tier 2"),
        ("Principal bruto", "R$ 4.783.356,52"),
        ("Total atualizado SELIC (BCB 4390, data-base 12/05/2026)", "R$ 8.230.061,40"),
        ("Prazo crítico", "30/09/2026 — 3 faturas do contrato 74/2021 (D+141)"),
    ]))

    # ---- CLÁUSULA PRIMEIRA — DAS PARTES ----
    out.append(secao("I", "Das Partes"))
    out.append(corpo([
        ("CREDORA: PRODAM S.A. — Processamento de Dados Amazonas, ", {"bold": True}),
        ("sociedade de economia mista de capital estadual, inscrita no CNPJ sob o nº ", {}),
        ("04.407.920/0001-80", {"bold": True}),
        (", com sede em Manaus/AM, regida pela Lei nº 13.303/2016 e estatuto social vigente.", {}),
    ]))
    out.append(corpo([
        ("DEVEDORA: Secretaria de Estado de Saúde do Amazonas / SUSAM, ", {"bold": True}),
        ("órgão da administração direta estadual do Amazonas, inscrita no CNPJ sob o nº ", {}),
        ("00.697.295/0001-05", {"bold": True}),
        (", com sede em Manaus/AM, neste ato representada nos termos do art. 37, II, da Constituição Federal e do regimento interno da SES/AM.", {}),
    ]))
    out.append(corpo([
        ("INTERVENIENTE-MANDATÁRIO DA CREDORA: Brandão Ozores Advogados, ", {"bold": True}),
        ("sociedade de advogados regularmente inscrita na OAB/AM, por intermédio do advogado ", {}),
        ("Gabriel Mar (OAB/AM 15.697)", {"bold": True}),
        (", na forma do Contrato de Inexigibilidade nº 002/2026 — PRODAM × Brandão Ozores Advogados, firmado em 2026 e em plena vigência.", {}),
    ]))

    # ---- CLÁUSULA SEGUNDA — DO OBJETO ----
    out.append(secao("II", "Do Objeto"))
    out.append(corpo(
        "A DEVEDORA reconhece a existência, liquidez e exigibilidade de débito junto à CREDORA referente a serviços de tecnologia da informação efetivamente prestados, totalmente cumpridos e recebidos sem oposição administrativa, no montante, em valores nominais brutos, de R$ 4.783.356,52 (quatro milhões, setecentos e oitenta e três mil, trezentos e cinquenta e seis reais e cinquenta e dois centavos), correspondente a 82 (oitenta e duas) faturas emitidas no período de agosto/2014 a março/2026, vinculadas a 08 (oito) instrumentos contratuais administrativos mantidos entre as partes, discriminadas no Anexo I deste Termo (Memorial Preliminar de Cálculo SES/SUSAM, datado de 12/05/2026, parte integrante e inseparável deste instrumento)."
    ))

    # ---- CLÁUSULA TERCEIRA — DO RECONHECIMENTO E FUNDAMENTOS JURÍDICOS ----
    out.append(secao("III", "Do Reconhecimento e dos Fundamentos Jurídicos"))
    out.append(corpo(
        "3.1. A DEVEDORA reconhece formalmente, neste ato, ser legítima credora dos serviços de TI prestados pela PRODAM nas faturas relacionadas no Anexo I, estando os respectivos débitos assim documentalmente compostos:"
    ))
    out.append(alinea("a)", "Contrato administrativo válido e vigente entre as partes em cada caso, constando como documento público dotado de fé pública (REsp 487.913/MG, 1ª Turma, Min. José Delgado, j. 09/06/2003)."))
    out.append(alinea("b)", "Nota de Empenho (NE) emitida pela DEVEDORA, configurando ato inequívoco de reconhecimento orçamentário-administrativo da obrigação."))
    out.append(alinea("c)", "Nota Fiscal (NF) emitida pela PRODAM em razão da execução contratual."))
    out.append(alinea("d)", "Atesto/recebimento do serviço pela autoridade competente da DEVEDORA."))
    out.append(alinea("e)", "Liquidação contábil (NL), quando aplicável."))

    out.append(corpo(
        "3.2. A composição documental acima descrita constitui título executivo nos termos do REsp 793.969/RJ (1ª Turma do STJ, Rel. p/ acórdão Min. José Delgado, j. 21/02/2006) e do REsp 879.046/DF, dotada de liquidez, certeza e exigibilidade."
    ))
    out.append(corpo(
        "3.3. A DEVEDORA, por meio de Notas de Empenho expedidas em 2026 (relacionadas no Anexo I), praticou ato inequívoco de reconhecimento do débito anterior, nos exatos termos do art. 202, VI, do Código Civil, hipótese que interrompe a prescrição e a reinicia pela metade, na forma do art. 9º do Decreto nº 20.910/1932 (EREsp 1.725.030/SP, Corte Especial, Min. Raul Araújo, dez/2023)."
    ))
    out.append(corpo(
        "3.4. As 79 (setenta e nove) faturas vinculadas a Notas de Empenho posteriores ao respectivo vencimento, listadas no Anexo I sob a marcação \"Tier 2\", têm seu prazo prescricional reaberto, com termo final variando entre setembro/2028 e outubro/2028."
    ))
    out.append(corpo(
        "3.5. As 3 (três) faturas restantes, vinculadas ao contrato 74/2021, listadas no Anexo I sob a marcação \"Tier 1\", encontram-se ainda dentro do prazo prescricional natural quinquenal (art. 206, §5º, I, do Código Civil), com termo final em 30/09/2026."
    ))
    out.append(corpo(
        "3.6. Não há, neste reconhecimento, qualquer renúncia ou disposição de prerrogativas indisponíveis da DEVEDORA, observada a vedação do Tema 1.109/STJ (1ª Seção, Min. Sérgio Kukina, j. 13/09/2023), aplicando-se aqui exclusivamente reconhecimento de obrigação líquida pretérita já documentalmente constituída."
    ))

    # ---- CLÁUSULA QUARTA — VALOR CONSOLIDADO E ATUALIZAÇÃO ----
    out.append(secao("IV", "Do Valor Consolidado e da Atualização Monetária"))
    out.append(corpo("4.1. Memorial Preliminar de Cálculo (Anexo I), à data-base de 12/05/2026:"))
    out.append(linha_tabela("Principal nominal (82 faturas)", "R$ 4.783.356,52"))
    out.append(linha_tabela("Correção monetária + juros (SELIC série BCB 4390, fator médio 1,720562x)", "R$ 3.446.704,88"))
    out.append(linha_tabela("VALOR TOTAL ATUALIZADO", "R$ 8.230.061,40", bold_valor=True))
    out.append(corpo(
        "4.2. O critério único de atualização aplicado é a Taxa SELIC acumulada mensalmente, na forma do art. 3º da Emenda Constitucional nº 113/2021 e do art. 406 do Código Civil (redação dada pela Lei nº 14.905/2024), normas constitucional e legal cogentes para a Fazenda Pública. A SELIC engloba, simultaneamente, correção monetária e juros de mora, não havendo juros separados nem multa moratória contratual."
    ))
    out.append(corpo(
        "4.3. A memória de cálculo fatura-a-fatura, com identificação de NF, contrato, competência, vencimento, valor original, fator SELIC aplicado e valor atualizado, consta do Anexo I (arquivo MEMORIAL_PRELIMINAR_SES_SUSAM_2026-05-12.md e respectivo XLSX)."
    ))

    # ---- CLÁUSULA QUINTA — FORMA DE CUMPRIMENTO ----
    out.append(secao("V", "Da Forma de Cumprimento"))
    out.append(corpo(
        "5.1. Reconhecida a natureza de órgão da administração direta estadual da DEVEDORA, o adimplemento do débito reconhecido neste Termo observará estritamente o regime constitucional de precatórios e RPV, nos termos do art. 100 da Constituição Federal, da Lei nº 2.748/2002 do Estado do Amazonas (que disciplina o teto de RPV estadual em 20 salários-mínimos) e do Decreto Estadual nº 53.464/2026 vigente."
    ))
    out.append(corpo(
        "5.2. A DEVEDORA compromete-se, no prazo de 30 (trinta) dias a contar da assinatura deste Termo, a:"
    ))
    out.append(alinea("a)", "emitir Nota de Empenho complementar para a totalidade do débito atualizado nominado na Cláusula Quarta, observado o regime orçamentário aplicável (Lei nº 4.320/1964 e LDO/LOA vigentes);"))
    out.append(alinea("b)", "incluir formalmente o débito na próxima lista de pagamento da SES/SUSAM, observando o critério cronológico de apresentação e a ordem constitucional;"))
    out.append(alinea("c)", "comunicar à PRODAM o número da Nota de Empenho complementar e a previsão de pagamento, por ofício formal endereçado à sede da CREDORA e ao escritório-mandatário."))
    out.append(corpo(
        "5.3. O presente Termo não constitui parcelamento ou novação, mantendo-se incólumes a natureza, a liquidez, a certeza e a exigibilidade do débito original em cada uma das 82 faturas relacionadas."
    ))

    # ---- CLÁUSULA SEXTA — INADIMPLEMENTO E TUTELA JURISDICIONAL ----
    out.append(secao("VI", "Do Inadimplemento e da Tutela Jurisdicional"))
    out.append(corpo(
        "6.1. O descumprimento dos compromissos assumidos na Cláusula Quinta, ou a ausência de manifestação formal da DEVEDORA no prazo de 30 (trinta) dias a contar da assinatura, autorizará a CREDORA a promover, independentemente de nova notificação, a tutela jurisdicional adequada, em especial:"
    ))
    out.append(alinea("a)", "Ação Monitória contra a Fazenda Pública (Súmula 339/STJ), tendo este Termo, em conjunto com os documentos do Anexo I, como prova escrita suficiente;"))
    out.append(alinea("b)", "Ação de Cobrança com pedido de expedição de RPV/Precatório, observado o regime do art. 100 da Constituição Federal;"))
    out.append(alinea("c)", "Protesto extrajudicial das certidões de dívida correspondentes, observada a possibilidade jurídica (ADI 5.135/DF, Plenário STF, Min. Roberto Barroso, j. 09/11/2016, e REsp 1.686.659/SP)."))
    out.append(corpo(
        "6.2. A interrupção prescricional aqui formalizada observará a regra da unicidade, na forma do REsp 1.963.067/MS (3ª Turma, Min. Nancy Andrighi, j. 05/04/2022)."
    ))

    # ---- CLÁUSULA SÉTIMA — FORO ----
    out.append(secao("VII", "Do Foro"))
    out.append(corpo(
        "Fica eleito o foro da Vara da Fazenda Pública Estadual da Comarca de Manaus/AM para dirimir quaisquer controvérsias decorrentes do presente Termo, observada a competência absoluta em razão da pessoa (art. 109, CF, a contrario sensu)."
    ))

    # ---- CLÁUSULA OITAVA — DISPOSIÇÕES FINAIS ----
    out.append(secao("VIII", "Das Disposições Finais"))
    out.append(corpo(
        "8.1. O presente Termo é firmado em caráter irrevogável e irretratável, obrigando as partes, seus sucessores e cessionários a qualquer título."
    ))
    out.append(corpo(
        "8.2. Qualquer alteração deste instrumento será formalizada exclusivamente por aditivo escrito, firmado pelos representantes legais das partes."
    ))
    out.append(corpo(
        "8.3. As partes declaram a perfeição, validade e eficácia deste Termo, dispensada a presença de testemunhas, em atenção à força probatória dos documentos públicos da DEVEDORA (REsp 487.913/MG)."
    ))
    out.append(corpo(
        "8.4. Este instrumento e seu Anexo I integram um único documento jurídico indissociável."
    ))

    out.append(corpo("Manaus/AM, 12 de maio de 2026."))

    # ---- ASSINATURAS ----
    # Bloco DEVEDORA + CREDORA + assinatura do escritório
    out.append(separador_dourado())
    out.append(corpo([("CREDORA:", {"bold": True})]))
    out.append(para(
        [], align="center", indent_first=0, indent_left=2400, indent_right=2400,
        before=120, after=40, line=240,
        border_bottom=(COR_TEXTO, 1, 1),
    ))
    out.append(para(
        [run("PRODAM S.A. — PROCESSAMENTO DE DADOS AMAZONAS", size=22, bold=True, color=COR_TEXTO)],
        align="center", indent_first=0, before=0, after=20, line=240,
    ))
    out.append(para(
        [run("CNPJ 04.407.920/0001-80   ·   Representante legal: [a preencher]", size=18, color=COR_TEXTO)],
        align="center", indent_first=0, before=0, after=200, line=240,
    ))

    out.append(corpo([("DEVEDORA:", {"bold": True})]))
    out.append(para(
        [], align="center", indent_first=0, indent_left=2400, indent_right=2400,
        before=120, after=40, line=240,
        border_bottom=(COR_TEXTO, 1, 1),
    ))
    out.append(para(
        [run("SECRETARIA DE ESTADO DE SAÚDE DO AMAZONAS / SUSAM", size=22, bold=True, color=COR_TEXTO)],
        align="center", indent_first=0, before=0, after=20, line=240,
    ))
    out.append(para(
        [run("CNPJ 00.697.295/0001-05   ·   Representante legal: [a preencher]", size=18, color=COR_TEXTO)],
        align="center", indent_first=0, before=0, after=200, line=240,
    ))

    out.append(corpo([("INTERVENIENTE-MANDATÁRIO DA CREDORA:", {"bold": True})]))
    out.append(para(
        [], align="center", indent_first=0, indent_left=2400, indent_right=2400,
        before=120, after=40, line=240,
        border_bottom=(COR_TEXTO, 1, 1),
    ))
    out.append(para(
        [run("GABRIEL MAR", size=22, bold=True, color=COR_TEXTO)],
        align="center", indent_first=0, before=0, after=20, line=240,
    ))
    out.append(para(
        [run("OAB/AM 15.697   ·   Contrato de Inexigibilidade nº 002/2026", size=18, color=COR_TEXTO)],
        align="center", indent_first=0, before=0, after=20, line=240,
    ))
    out.append(para(
        [run("Brandão Ozores Advogados", size=20, bold=True, small_caps=True, color=COR_DOURADO)],
        align="center", indent_first=0, before=80, after=200, line=240,
    ))

    # ---- ANEXO I (referência ao memorial) ----
    out.append(separador_dourado())
    out.append(secao("Anexo I", "Memorial Preliminar de Cálculo"))
    out.append(corpo(
        "Constitui Anexo I deste Termo, com força de parte integrante e inseparável, o arquivo MEMORIAL_PRELIMINAR_SES_SUSAM_2026-05-12.md e sua versão XLSX, elaborados em 12/05/2026, contendo: fundamentação da atualização monetária (EC 113/2021, art. 406 CC, REsp 793.969/RJ); universo de 82 faturas com discriminação por tier (3 Tier 1 + 79 Tier 2); tabela fatura-a-fatura com NF, contrato, competência, vencimento, valor bruto, fator SELIC e valor atualizado; totais consolidados e fator SELIC médio ponderado; declaração de caráter preliminar do memorial (não pericial)."
    ))

    return "".join(out)


# ===========================================================================
# Pipeline principal
# ===========================================================================
def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

    print("=" * 70)
    print("GERAR TRD SES/SUSAM .docx — design-brandao-ozores v1.0")
    print("=" * 70)

    # [1] Hash ANTES
    print("\n[1] Verificando hash do template (ANTES)...")
    if not TEMPLATE.exists():
        print(f"    FAIL: template não existe em {TEMPLATE}")
        return 1
    hash_antes = hashlib.sha256(TEMPLATE.read_bytes()).hexdigest()
    if not verificacao_hash_template(TEMPLATE):
        print(f"    FAIL: hash inicial não bate. {hash_antes}")
        return 1
    print(f"    OK: {hash_antes[:32]}…")

    # [2-6] Geração via unpack/edit/repack
    print("\n[2-6] Pipeline unpack → edit → repack...")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        unpacked = Path(tmp) / "unpacked"
        unpacked.mkdir()

        # Unpack
        with zipfile.ZipFile(TEMPLATE, "r") as z:
            z.extractall(unpacked)
        print(f"    unpack OK")

        # Limpeza obrigatória
        rels_f = unpacked / "word" / "_rels" / "settings.xml.rels"
        if rels_f.exists():
            rels_f.unlink()
            print(f"    settings.xml.rels deletado")

        settings_f = unpacked / "word" / "settings.xml"
        if settings_f.exists():
            s = settings_f.read_text(encoding="utf-8")
            s_new = re.sub(r"<w:attachedTemplate[^/]*/>", "", s)
            if s != s_new:
                settings_f.write_text(s_new, encoding="utf-8")
                print(f"    attachedTemplate removido de settings.xml")

        # Substituir corpo do document.xml
        body_xml = montar_corpo()
        doc_f = unpacked / "word" / "document.xml"
        doc_xml = doc_f.read_text(encoding="utf-8")

        m = re.search(r"<w:sectPr[^>]*>.*?</w:sectPr>", doc_xml, re.DOTALL)
        if not m:
            print("    FAIL: sectPr não encontrado em document.xml")
            return 1
        sect_pr = m.group(0)

        new_body = f"<w:body>{body_xml}{sect_pr}</w:body>"
        doc_xml_new = re.sub(
            r"<w:body>.*</w:body>", new_body, doc_xml, flags=re.DOTALL
        )
        doc_f.write_text(doc_xml_new, encoding="utf-8")
        print(f"    document.xml atualizado ({len(body_xml):,} bytes de body)")

        # Substituir footer2.xml (se houver)
        footer_f = unpacked / "word" / "footer2.xml"
        if footer_f.exists():
            footer_f.write_text(footer_paginacao(), encoding="utf-8")
            print(f"    footer2.xml substituído")
        else:
            print(f"    footer2.xml não encontrado — preservando footer do template")

        # Repack via zipfile (sem pack.py externo)
        print("\n[7] Repack via zipfile...")
        if OUTPUT.exists():
            OUTPUT.unlink()
        with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as z:
            for f in unpacked.rglob("*"):
                if f.is_file():
                    z.write(f, f.relative_to(unpacked).as_posix())
        print(f"    repack OK: {OUTPUT}")
        print(f"    tamanho: {OUTPUT.stat().st_size:,} bytes")

    # [8] Hash DEPOIS
    print("\n[8] Verificando hash do template (DEPOIS)...")
    hash_depois = hashlib.sha256(TEMPLATE.read_bytes()).hexdigest()
    if not verificacao_hash_template(TEMPLATE):
        print(f"    FAIL: hash mudou! {hash_depois}")
        return 2
    if hash_antes != hash_depois:
        print(f"    FAIL: hash divergente! {hash_depois}")
        return 2
    print(f"    OK: template íntegro")

    print()
    print("=" * 70)
    print(f"TRD GERADO: {OUTPUT}")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
