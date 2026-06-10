from docx import Document
from docx.oxml.ns import qn
import re

doc = Document('/home/ubuntu/upload/DOSSIE_COBRANCA_DETRAN_v4.docx')

body = doc.element.body

def get_text(elem):
    """Extract all text from an element"""
    texts = []
    for t in elem.iter(qn('w:t')):
        if t.text:
            texts.append(t.text)
    return ''.join(texts).strip()

# List all direct children of body with their type and key text
for i, child in enumerate(body):
    tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
    if tag == 'p':
        text = get_text(child)
        if text:
            print(f"[{i}] PARA: '{text[:150]}'")
        else:
            print(f"[{i}] PARA: (empty)")
    elif tag == 'tbl':
        rows = child.findall(qn('w:tr'))
        first_row_text = ""
        if rows:
            cells = rows[0].findall(qn('w:tc'))
            cell_texts = [get_text(c) for c in cells]
            first_row_text = " | ".join(cell_texts)
        print(f"[{i}] TABLE ({len(rows)} rows): '{first_row_text[:150]}'")
    elif tag == 'sectPr':
        print(f"[{i}] SECTION PROPERTIES")
    else:
        print(f"[{i}] {tag}")
