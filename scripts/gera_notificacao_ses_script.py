#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gera_notificacao_ses.py - Notificação Extrajudicial Modelo A para SES/SUSAM
"""

import json
import zipfile
import shutil
import os
import re
import tempfile
from pathlib import Path
from datetime import datetime
from decimal import Decimal

if os.environ.get("PRODAM_FREEZE_EMISSAO"):
    import sys; sys.exit("[FREEZE] Emissão de peças bloqueada durante auditoria DE. Remover PRODAM_FREEZE_EMISSAO para destravar.")
# ============================================================
# BLOQUEIO MANUAL — adicionado em 2026-05-10
# Motivo: numeração "NOT/001/2026" hardcoded colide com a NE 001/2026
# DETRAN já protocolada via ICP-Brasil em 20/04/2026.
# Para destravar: substituir todas as ocorrências de "NOT/001/2026"
# por numeração SES não conflitante e remover este bloqueio.
# ============================================================
import sys
sys.exit("[BLOQUEADO] Numeração NOT/001/2026 colide com NE DETRAN. Ver bloco de comentário no topo do arquivo.")

# Configurações
TEMPLATE_PATH = Path(r"C:\Users\gabri\AppData\Roaming\Claude\local-agent-mode-sessions\ca3c1d7d-30ad-43bd-aa7d-43e556ee3c2f\3efad0a3-b9bb-4019-a643-63925c649af6\local_4dcc6802-8b8f-4f7a-8796-e5fcc556cd5f\uploads\Papel Timbrado Brandao Ozores.docx")
OUTPUT_DIR = Path(r"C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS\_SKILLS\dossie-juridico-prodam-workspace\iteration-1\eval-2-notificacao-ses\with_skill\outputs")
PROFILES_PATH = Path(r"C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS\profiles.json")

# Cores e fontes
FONT = "Dupincel Text"
COR_PRINCIPAL = "2D2D2D"
COR_DOURADA = "B8963E"
COR_AZUL = "1F3864"

def escape_xml(text):
    if not text:
        return ""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

def rpr(size=22, bold=False, italic=False, caps=False, smallCaps=False, color=COR_PRINCIPAL, spacing=None):
    x = f'<w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:cs="{FONT}"/>'
    x += f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>'
    x += f'<w:color w:val="{color}"/>'
    if bold: x += '<w:b/><w:bCs/>'
    if italic: x += '<w:i/><w:iCs/>'
    if caps: x += '<w:caps/>'
    if smallCaps: x += '<w:smallCaps/>'
    if spacing: x += f'<w:spacing w:val="{spacing}"/>'
    x += '</w:rPr>'
    return x

def run(text, **kw):
    r = rpr(**kw)
    t = escape_xml(text)
    sp = ' xml:space="preserve"' if t.startswith(' ') or t.endswith(' ') else ''
    return f'<w:r>{r}<w:t{sp}>{t}</w:t></w:r>'

def para(runs_list, align="both", indent_first=709, line=360, before=0, after=140):
    jc = f'<w:jc w:val="{align}"/>' if align else ''
    ind = f'<w:ind w:firstLine="{indent_first}"/>' if indent_first else ''
    sp_b = f' w:before="{before}"' if before else ''
    sp_a = f' w:after="{after}"' if after else ''
    sp = f'<w:spacing w:line="{line}" w:lineRule="auto"{sp_b}{sp_a}/>'
    ppr = f'<w:pPr>{sp}{ind}{jc}</w:pPr>'
    return f'<w:p>{ppr}{"".join(runs_list)}</w:p>'

def titulo(text):
    return para([run(text, size=28, bold=True, caps=True, spacing=60, color=COR_AZUL)],
                align="center", indent_first=0, after=100)

def separador():
    return para([run("————————————————————", size=16, color=COR_DOURADA)],
                align="center", indent_first=0, after=200)

def secao(text):
    return para([run(text, bold=True, smallCaps=True, color=COR_AZUL)],
                align="both", indent_first=0, before=300, after=140)

def corpo(text, indent=True):
    return para([run(text)], indent_first=709 if indent else 0)

def corpo_destacado(segments, indent=True):
    runs = []
    for seg in segments:
        if isinstance(seg, str):
            runs.append(run(seg))
        else:
            runs.append(run(seg["t"],
                bold=seg.get("b", False),
                italic=seg.get("i", False),
                smallCaps=seg.get("sc", False),
                color=seg.get("color", COR_PRINCIPAL)))
    return para(runs, indent_first=709 if indent else 0)

def alinea(letra, text):
    runs_list = [run(letra + " ", bold=True), run(text)]
    ppr = '<w:pPr><w:spacing w:line="360" w:lineRule="auto" w:after="100"/>'
    ppr += '<w:ind w:left="720" w:hanging="360"/><w:jc w:val="both"/></w:pPr>'
    return f'<w:p>{ppr}{"".join(runs_list)}</w:p>'

def unpack_docx(docx_path: Path, dest: Path):
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(docx_path, 'r') as z:
        z.extractall(dest)

def limpar_template(unpacked: Path):
    rels = unpacked / "word/_rels/settings.xml.rels"
    if rels.exists():
        os.remove(rels)
    settings = unpacked / "word/settings.xml"
    if settings.exists():
        s = settings.read_text(encoding='utf-8')
        s = re.sub(r'<w:attachedTemplate[^/]*/>', '', s)
        settings.write_text(s, encoding='utf-8')

def injetar_body(unpacked: Path, body_xml: str):
    SECT_PR = '''<w:sectPr>
  <w:headerReference w:type="even" r:id="rId7"/>
  <w:headerReference w:type="default" r:id="rId8"/>
  <w:footerReference w:type="even" r:id="rId9"/>
  <w:footerReference w:type="default" r:id="rId10"/>
  <w:headerReference w:type="first" r:id="rId11"/>
  <w:footerReference w:type="first" r:id="rId12"/>
  <w:pgSz w:w="11910" w:h="16840"/>
  <w:pgMar w:top="3460" w:right="900" w:bottom="1400" w:left="1020"
           w:header="659" w:footer="1218" w:gutter="0"/>
  <w:cols w:space="720"/>
</w:sectPr>'''

    doc_path = unpacked / "word/document.xml"
    doc = doc_path.read_text(encoding='utf-8')
    new_body = f'<w:body>{body_xml}{SECT_PR}</w:body>'
    doc = re.sub(r'<w:body>.*?</w:body>', new_body, doc, flags=re.DOTALL)
    doc_path.write_text(doc, encoding='utf-8')

def repack_docx(unpacked: Path, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(unpacked):
            for file in files:
                abs_path = Path(root) / file
                arc_name = abs_path.relative_to(unpacked)
                zf.write(abs_path, arc_name)

def meses_pt(data_str):
    """Converte data para português"""
    meses = {
        "January": "janeiro",
        "February": "fevereiro",
        "March": "março",
        "April": "abril",
        "May": "maio",
        "June": "junho",
        "July": "julho",
        "August": "agosto",
        "September": "setembro",
        "October": "outubro",
        "November": "novembro",
        "December": "dezembro"
    }
    for en, pt in meses.items():
        data_str = data_str.replace(en, pt)
    return data_str

def gerar_notificacao():
    # Carregar dados
    with open(PROFILES_PATH, 'r', encoding='utf-8') as f:
        profiles = json.load(f)
    dados = profiles.get("SES/SUSAM", {})

    # Dados
    data_emissao = datetime.now()
    data_emissao_fmt = meses_pt(data_emissao.strftime("%d de %B de %Y"))

    val_exig = Decimal(str(dados.get("val_exig", "14748048.96")))
    val_exig_fmt = f"R$ {val_exig:,.2f}".replace(",", ".")

    cnpj_devedor = dados.get("cnpj", "00.697.295/0001-05")
    cnpj_prodam = "04.407.920/0001-80"

    body_parts = []

    # Conteúdo
    body_parts.append(titulo("NOTIFICAÇÃO EXTRAJUDICIAL"))
    body_parts.append(separador())

    body_parts.append(para([
        run(f"NOT/", bold=True),
        run("001"),
        run(f"/2026", bold=True)
    ], align="center", indent_first=0, after=100))

    body_parts.append(para([
        run(f"Manaus, {data_emissao_fmt}.")
    ], align="right", indent_first=0, after=200))

    body_parts.append(secao("Destinatário"))
    body_parts.append(corpo_destacado([
        {"t": "Secretaria de Saúde do Amazonas / Fundação de Medicina Tropical", "b": True},
        "\n",
        "CNPJ: " + cnpj_devedor,
        "\nManaus, Amazonas"
    ]))

    body_parts.append(secao("Assunto"))
    body_parts.append(corpo("Notificação para pagamento de dívida vencida conforme art. 784 do Código de Processo Civil."))

    body_parts.append(secao("Conteúdo"))

    body_parts.append(corpo_destacado([
        "A ",
        {"t": "Gabriel Mar Sociedade Individual de Advocacia", "sc": True},
        ", agindo como representante legal de ",
        {"t": "PRODAM S.A.", "b": True},
        " (CNPJ ",
        {"t": cnpj_prodam, "b": True},
        "), vem, por este meio, "
    ]))

    body_parts.append(corpo_destacado([
        {"t": "NOTIFICAR", "b": True},
        " a ",
        {"t": "SES/SUSAM", "b": True},
        " do débito em aberto de "
    ]))

    body_parts.append(corpo_destacado([
        {"t": f"{val_exig_fmt} (quatorze milhões, setecentos e quarenta e oito mil, quarenta e oito reais e noventa e seis centavos)", "b": True},
        ", referente a faturas vencidas não pagas, resultante de contratações legítimas de serviços.",
    ]))

    body_parts.append(secao("Fundamentos Jurídicos"))
    body_parts.append(alinea("I.", "A notificação fundamenta-se no art. 784 do Código de Processo Civil, que admite execução extrajudicial contra devedor que reconhece a dívida, bem como no reconhecimento tácito evidenciado por empenhos, notas de liquidação e aceites técnicos."))
    body_parts.append(alinea("II.", "O valor referido encontra-se devidamente atualizado conforme índice SELIC, em conformidade com a Lei 14.905/2024 e os arts. 404 a 406 do Código Civil."))
    body_parts.append(alinea("III.", "A composição documental (contrato + empenho + nota de liquidação + aceite) constitui título executivo extrajudicial, conforme jurisprudência consolidada (REsp 793.969/RJ, Rel. p/ acórdão Min. José Delgado; Teori Zavascki vencido)."))

    body_parts.append(secao("Prazo para Pagamento"))
    body_parts.append(corpo_destacado([
        "Fica a ",
        {"t": "SES/SUSAM", "b": True},
        " notificada para que proceda ao pagamento da dívida no prazo de ",
        {"t": "15 (quinze) dias úteis", "b": True},
        " contados do recebimento desta notificação, sob pena de ajuizamento de ação executiva.",
    ]))

    body_parts.append(secao("Alerta — Prescrição Iminente"))
    body_parts.append(corpo_destacado([
        {"t": "ATENÇÃO:", "b": True},
        " O direito de PRODAM prescreve em ",
        {"t": "13 de maio de 2026", "b": True},
        " (em ",
        {"t": "29 dias", "b": True},
        "). Passada esta data, a cobrança será prejudicada pela fluência do prazo prescricional de 5 (cinco) anos contado do vencimento das faturas (art. 206, §5º, I do CC).",
    ]))

    body_parts.append(secao("Consequências do Não Pagamento"))
    body_parts.append(alinea("1.", "Sem resposta em 15 dias úteis: ajuizamento de ação executiva perante o Tribunal de Justiça do Estado do Amazonas, com todos os ônus processuais (custas, honorários, multa de 10%)."))
    body_parts.append(alinea("2.", "Perda da prescrição: caso o prazo de prescrição se complete (31/08/2026), PRODAM perderia todo e qualquer direito de cobrança, sem direito a regressão."))
    body_parts.append(alinea("3.", "Regime de execução: como entidade da administração direta, a execução se dará via precatório ou Requisição de Pequeno Valor (RPV), conforme art. 100 CF."))

    body_parts.append(secao("Possibilidade de Acordo"))
    body_parts.append(corpo("PRODAM permanece aberta a negociações. Manifestações ou propostas de pagamento devem ser encaminhadas a este escritório no prazo supracitado."))

    body_parts.append(secao("Foro Competente"))
    body_parts.append(corpo("Fica reservado o direito de PRODAM de promover execução judicial perante o Tribunal de Justiça do Estado do Amazonas (Foro de Manaus)."))

    body_parts.append(para([], before=400, after=0))
    body_parts.append(corpo_destacado([
        "Respeitosamente apresentado,",
    ], indent=False))
    body_parts.append(para([], before=400, after=0))

    # Assinatura
    body_parts.append(para([], indent_first=0, before=600, after=0))
    body_parts.append(para([run("Gabriel Mar", bold=True)], align="center", indent_first=0, after=40))
    body_parts.append(para([run("OAB/AM 15.697")], align="center", indent_first=0, after=40))
    body_parts.append(para([run("Advogado")], align="center", indent_first=0, after=40))
    body_parts.append(para([run("Gabriel Mar Sociedade Individual de Advocacia", bold=True, smallCaps=True)],
                          align="center", indent_first=0, after=40))
    body_parts.append(para([run("Em nome de Brandão Ozores Advogados")],
                          align="center", indent_first=0, after=0))

    return "".join(body_parts)

def main():
    print("[*] Gerando notificação...")
    body_xml = gerar_notificacao()

    print("[*] Unpackando template...")
    temp_dir = Path(tempfile.gettempdir()) / "notificacao_ses_temp"
    unpack_docx(TEMPLATE_PATH, temp_dir)

    print("[*] Limpando template...")
    limpar_template(temp_dir)

    print("[*] Injetando conteúdo...")
    injetar_body(temp_dir, body_xml)

    print("[*] Repackando .docx...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / "NOT_SES_SUSAM_001_2026.docx"
    repack_docx(temp_dir, output_file)

    print(f"\n[✓] Sucesso! Arquivo salvo em:")
    print(f"    {output_file}")

    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    main()
