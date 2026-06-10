"""
Script para remover seções específicas do dossiê e renumerar os itens restantes.
Mantém toda a formatação, layout e tipografia originais do DOCX.
"""
from docx import Document
from docx.oxml.ns import qn
from copy import deepcopy
import re

# Abrir o documento original
doc = Document('/home/ubuntu/upload/DOSSIE_COBRANCA_DETRAN_v4.docx')
body = doc.element.body

def get_text(elem):
    """Extrair todo o texto de um elemento XML."""
    texts = []
    for t in elem.iter(qn('w:t')):
        if t.text:
            texts.append(t.text)
    return ''.join(texts).strip()

def set_text_preserving_format(elem, old_text, new_text):
    """
    Substituir texto em um elemento, preservando a formatação dos runs.
    Procura em cada w:t e faz a substituição.
    """
    for t_elem in elem.iter(qn('w:t')):
        if t_elem.text and old_text in t_elem.text:
            t_elem.text = t_elem.text.replace(old_text, new_text)
            return True
    return False

# ============================================================
# PASSO 1: Identificar e remover os elementos das seções
# ============================================================

# Coletar todos os filhos do body (exceto sectPr)
children = list(body)
sect_pr = None
for child in children:
    tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
    if tag == 'sectPr':
        sect_pr = child

# Mapear índices dos elementos
elements_info = []
for i, child in enumerate(children):
    tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
    text = get_text(child) if tag in ('p', 'tbl') else ''
    elements_info.append({'index': i, 'tag': tag, 'text': text, 'element': child})

# Definir os ranges de índices a remover (baseado na inspeção)
# Seção 5 completa: índices 48-58
# Subseção 6.3: índices 67-71
# Subseções 7.3 e 7.4: índices 81-85
# Seção 9 completa: índices 97-105
# Seção 10 completa: índices 106-120
# Seção 13 completa: índices 138-151

# Vamos verificar dinamicamente para ser mais robusto
indices_to_remove = set()

# Encontrar seções por texto
section_starts = {}
for info in elements_info:
    text = info['text']
    if text:
        # Seção 5
        if re.match(r'^5\s*[—–-]\s*Da Blindagem', text, re.IGNORECASE):
            section_starts['5'] = info['index']
        # Seção 5.1
        elif re.match(r'^5\.1\s*[—–-]', text):
            section_starts['5.1'] = info['index']
        # Seção 5.2
        elif re.match(r'^5\.2\s*[—–-]', text):
            section_starts['5.2'] = info['index']
        # Seção 6
        elif re.match(r'^6\s*[—–-]\s*Das Notas', text, re.IGNORECASE):
            section_starts['6'] = info['index']
        # Seção 6.3
        elif re.match(r'^6\.3\s*[—–-]', text):
            section_starts['6.3'] = info['index']
        # Seção 7
        elif re.match(r'^7\s*[—–-]\s*Do Reconhecimento', text, re.IGNORECASE):
            section_starts['7'] = info['index']
        # Seção 7.3
        elif re.match(r'^7\.3\s*[—–-]', text):
            section_starts['7.3'] = info['index']
        # Seção 7.4
        elif re.match(r'^7\.4\s*[—–-]', text):
            section_starts['7.4'] = info['index']
        # Seção 8
        elif re.match(r'^8\s*[—–-]\s*Da Correção', text, re.IGNORECASE):
            section_starts['8'] = info['index']
        # Seção 9
        elif re.match(r'^9\s*[—–-]\s*Do Regime', text, re.IGNORECASE):
            section_starts['9'] = info['index']
        # Seção 10
        elif re.match(r'^10\s*[—–-]\s*Da Análise', text, re.IGNORECASE):
            section_starts['10'] = info['index']
        # Seção 11
        elif re.match(r'^11\s*[—–-]\s*Da Constituição', text, re.IGNORECASE):
            section_starts['11'] = info['index']
        # Seção 12
        elif re.match(r'^12\s*[—–-]\s*Das Consequências', text, re.IGNORECASE):
            section_starts['12'] = info['index']
        # Seção 13
        elif re.match(r'^13\s*[—–-]\s*Da Fundamentação', text, re.IGNORECASE):
            section_starts['13'] = info['index']
        # Seção 14
        elif re.match(r'^14\s*[—–-]\s*Do Dossiê', text, re.IGNORECASE):
            section_starts['14'] = info['index']
        # Seção 15
        elif re.match(r'^15\s*[—–-]\s*Do Encerramento', text, re.IGNORECASE):
            section_starts['15'] = info['index']

print("Section starts found:", section_starts)

# Remover Seção 5 inteira (de '5 —' até antes de '6 —')
if '5' in section_starts and '6' in section_starts:
    for i in range(section_starts['5'], section_starts['6']):
        indices_to_remove.add(i)

# Remover Subseção 6.3 (de '6.3 —' até antes de '7 —')
if '6.3' in section_starts and '7' in section_starts:
    for i in range(section_starts['6.3'], section_starts['7']):
        indices_to_remove.add(i)

# Remover Subseções 7.3 e 7.4 (de '7.3 —' até antes de '8 —')
if '7.3' in section_starts and '8' in section_starts:
    for i in range(section_starts['7.3'], section_starts['8']):
        indices_to_remove.add(i)

# Remover Seção 9 inteira (de '9 —' até antes de '10 —')
if '9' in section_starts and '10' in section_starts:
    for i in range(section_starts['9'], section_starts['10']):
        indices_to_remove.add(i)

# Remover Seção 10 inteira (de '10 —' até antes de '11 —')
if '10' in section_starts and '11' in section_starts:
    for i in range(section_starts['10'], section_starts['11']):
        indices_to_remove.add(i)

# Remover Seção 13 inteira (de '13 —' até antes de '14 —')
if '13' in section_starts and '14' in section_starts:
    for i in range(section_starts['13'], section_starts['14']):
        indices_to_remove.add(i)

print(f"\nTotal elements to remove: {len(indices_to_remove)}")
print(f"Indices to remove: {sorted(indices_to_remove)}")

# Remover os elementos do body (de trás para frente para manter índices válidos)
for i in sorted(indices_to_remove, reverse=True):
    elem = children[i]
    body.remove(elem)

print("\nElements removed successfully.")

# ============================================================
# PASSO 2: Renumerar as seções e subseções restantes
# ============================================================

# Mapeamento de renumeração:
# Seções principais: 6→5, 7→6, 8→7, 11→8, 12→9, 14→10, 15→11
# Subseções: 6.1→5.1, 6.2→5.2, 7.1→6.1, 7.2→6.2, 8.1→7.1, 8.2→7.2, 11.1→8.1

renumber_map = {
    # Subseções primeiro (mais específicas) para evitar conflitos
    '6.1 ': '5.1 ',
    '6.2 ': '5.2 ',
    '7.1 ': '6.1 ',
    '7.2 ': '6.2 ',
    '8.1 ': '7.1 ',
    '8.2 ': '7.2 ',
    '11.1 ': '8.1 ',
    # Seções principais
    '6 ': '5 ',
    '7 ': '6 ',
    '8 ': '7 ',
    '11 ': '8 ',
    '12 ': '9 ',
    '14 ': '10 ',
    '15 ': '11 ',
}

# Agora iterar sobre os elementos restantes e renumerar
remaining_children = list(body)
renumbered_count = 0

for child in remaining_children:
    tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
    if tag != 'p':
        continue
    
    text = get_text(child)
    if not text:
        continue
    
    # Verificar se o texto começa com um número de seção que precisa ser renumerado
    # Padrão: "X.Y — " ou "X — "
    match = re.match(r'^(\d+(?:\.\d+)?)\s*([—–-])', text)
    if match:
        old_num = match.group(1)
        # Tentar encontrar no mapa de renumeração
        old_key = old_num + ' '
        if old_key in renumber_map:
            new_key = renumber_map[old_key]
            new_num = new_key.strip()
            # Substituir no texto dos runs
            for t_elem in child.iter(qn('w:t')):
                if t_elem.text and old_num in t_elem.text:
                    # Verificar que é o número no início (não um número aleatório no meio do texto)
                    # Substituir apenas a primeira ocorrência que corresponde ao padrão de seção
                    pattern = re.compile(r'^' + re.escape(old_num) + r'(?=\s*[—–-])')
                    if pattern.match(t_elem.text.strip()):
                        t_elem.text = t_elem.text.replace(old_num, new_num, 1)
                        renumbered_count += 1
                        print(f"Renumbered: '{old_num}' -> '{new_num}' in: '{text[:80]}'")
                        break
                    # Também verificar se o run contém apenas o número
                    elif t_elem.text.strip() == old_num:
                        t_elem.text = t_elem.text.replace(old_num, new_num, 1)
                        renumbered_count += 1
                        print(f"Renumbered (exact): '{old_num}' -> '{new_num}' in: '{text[:80]}'")
                        break

print(f"\nTotal renumbered: {renumbered_count}")

# ============================================================
# PASSO 3: Salvar o documento
# ============================================================

output_path = '/home/ubuntu/DOSSIE_COBRANCA_DETRAN_v5.docx'
doc.save(output_path)
print(f"\nDocument saved to: {output_path}")

# Verificação final: listar as seções restantes
print("\n\n=== VERIFICAÇÃO FINAL ===")
final_children = list(body)
for child in final_children:
    tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
    if tag == 'p':
        text = get_text(child)
        if text and re.match(r'^\d+(\.\d+)?\s*[—–-]', text):
            print(f"  {text[:100]}")
