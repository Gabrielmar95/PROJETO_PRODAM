import csv, calendar
from datetime import datetime
from collections import Counter
from decimal import Decimal

path = r'PRODAM_DOCS\_WORKFLOW_IMPORTADO\FATURAS_POR_DEVEDOR\SEJUSC_FATURAS_CRUZADAS.csv'
with open(path, encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f, delimiter=';'))

print(f'Total linhas CSV: {len(rows)}')

today = datetime(2026, 5, 12)

# Filtros
zero_val = []   # valor_liquido = 0 (sem cobranca)
canceladas = []
perdas = []
faturas_efetivas = []  # com valor real

for r in rows:
    val_liq_str = (r.get('valor_liquido') or '0').replace(',', '.')
    try:
        val_liq = float(val_liq_str)
    except:
        val_liq = 0.0
    cancel = (r.get('cancelada') or '').upper() == 'TRUE'
    perda = (r.get('em_perdas') or '').upper() == 'TRUE'

    if cancel:
        canceladas.append(r)
    elif perda:
        perdas.append(r)
    elif val_liq <= 0:
        zero_val.append(r)
    else:
        faturas_efetivas.append(r)

print(f'\n=== TRIAGEM ===')
print(f'  Valor zero/sem cobranca: {len(zero_val)}')
print(f'  Canceladas: {len(canceladas)}')
print(f'  Em perdas: {len(perdas)}')
print(f'  Com valor liquido > 0: {len(faturas_efetivas)}')

# Para faturas efetivas, recalcular prescricao per-fatura
prescritas = []
exigiveis = []
sem_competencia = []

for r in faturas_efetivas:
    comp = r.get('competencia') or ''
    nf = r.get('numero_fatura') or r.get('pref') or '?'
    val_str = (r.get('valor_liquido') or '0').replace(',', '.')
    try:
        val = float(val_str)
    except:
        val = 0.0
    ct = r.get('contrato', '?')
    emp = r.get('empenho_vinculado') or ''
    data_emp = r.get('data_empenho') or ''
    qtd_emp = r.get('qtd_empenhos') or '0'

    if not comp or '/' not in comp:
        sem_competencia.append({'nf': nf, 'val': val, 'ct': ct})
        continue

    try:
        m, y = comp.split('/')
        m, y = int(m), int(y)
        # Vencimento = ultimo dia do mes seguinte a competencia
        if m == 12:
            _, last = calendar.monthrange(y + 1, 1)
            venc = datetime(y + 1, 1, last)
        else:
            _, last = calendar.monthrange(y, m + 1)
            venc = datetime(y, m + 1, last)
        prescr = venc.replace(year=venc.year + 5)
        d_plus = (prescr - today).days

        entry = {
            'nf': nf, 'comp': comp, 'ct': ct, 'val': val,
            'venc': venc.strftime('%Y-%m-%d'),
            'prescr': prescr.strftime('%Y-%m-%d'),
            'd_plus': d_plus,
            'emp': emp,
            'data_emp': data_emp,
            'qtd_emp': qtd_emp,
        }

        if d_plus < 0:
            prescritas.append(entry)
        else:
            exigiveis.append(entry)
    except Exception as ex:
        print(f'  ERRO parsing comp={comp} nf={nf}: {ex}')

print(f'\n=== PRESCRICAO (recalculada per-fatura, sem considerar marco do empenho) ===')
print(f'  Prescritas (vencimento+5y < hoje): {len(prescritas)}')
print(f'  Exigiveis (vencimento+5y >= hoje): {len(exigiveis)}')
print(f'  Sem competencia parseavel: {len(sem_competencia)}')

if exigiveis:
    earliest = min(exigiveis, key=lambda e: e['d_plus'])
    latest = max(exigiveis, key=lambda e: e['d_plus'])
    val_exig = sum(e['val'] for e in exigiveis)
    print(f'\n  Valor exigivel TOTAL: R$ {val_exig:,.2f}')
    print(f'  Prescricao mais proxima: NF {earliest["nf"]}, comp {earliest["comp"]}, ct {earliest["ct"]}')
    print(f'    prescr {earliest["prescr"]}, D+{earliest["d_plus"]}, val R$ {earliest["val"]:,.2f}')
    print(f'    empenho: "{earliest["emp"]}" (data: "{earliest["data_emp"]}", qtd: {earliest["qtd_emp"]})')
    print(f'  Prescricao mais distante: D+{latest["d_plus"]} ({latest["prescr"]})')

# Distribuicao por competencia (exigiveis)
print(f'\n=== EXIGIVEIS por competencia (top 10 mais urgentes) ===')
for e in sorted(exigiveis, key=lambda x: x['d_plus'])[:10]:
    has_emp = 'EMPENHO' if e['emp'] else '(sem emp)'
    print(f'  comp {e["comp"]:8s} ct {str(e["ct"]):20s} D+{e["d_plus"]:5d} val R${e["val"]:>12,.2f} {has_emp}')

# Faturas exigíveis SEM empenho (alto risco — sem marco interruptivo)
sem_emp = [e for e in exigiveis if not e['emp']]
com_emp = [e for e in exigiveis if e['emp']]
val_sem_emp = sum(e['val'] for e in sem_emp)
val_com_emp = sum(e['val'] for e in com_emp)
print(f'\n=== MARCOS INTERRUPTIVOS (Art. 202 VI CC) ===')
print(f'  Exigiveis SEM empenho vinculado: {len(sem_emp)} fat, R$ {val_sem_emp:,.2f}')
print(f'  Exigiveis COM empenho vinculado: {len(com_emp)} fat, R$ {val_com_emp:,.2f}')

# Valor das prescritas
val_prescr = sum(e['val'] for e in prescritas)
print(f'\n=== PERDAS ESTIMADAS ===')
print(f'  Valor prescrito: R$ {val_prescr:,.2f}')
print(f'  Valor zero/cancel/perda (CSV): R$ ' +
      f'{sum(float((r.get("valor_liquido") or "0").replace(",", ".")) for r in zero_val + canceladas + perdas):,.2f}')

# Recalcular considerando interrupcao por empenho (Art. 202 VI + unicidade Art. 202 caput)
# Marco interruptivo = data do empenho mais recente. Reinicia integral (CC) ou metade (Decreto 20.910 para Fazenda)
print(f'\n=== EXIGIVEIS QUE PASSAM A PRESCRITAS SE NAO HOUVE MARCO POS-VENCIMENTO ===')
print(f'  (faturas com d_plus<730 em risco real se nao houver outro marco)')
risk_zone = [e for e in exigiveis if e['d_plus'] < 365]
print(f'  D+ < 365 dias: {len(risk_zone)} fat, R$ {sum(e["val"] for e in risk_zone):,.2f}')
risk_imm = [e for e in exigiveis if e['d_plus'] < 90]
print(f'  D+ < 90 dias (URGENTE): {len(risk_imm)} fat, R$ {sum(e["val"] for e in risk_imm):,.2f}')
for e in risk_imm[:10]:
    print(f'    NF {e["nf"]} comp {e["comp"]} ct {e["ct"]} D+{e["d_plus"]} R${e["val"]:,.2f} emp={e["emp"]!r}')
