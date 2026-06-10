#!/usr/bin/env python3
"""
Cria a estrutura de pastas organizada com rastreabilidade completa
para todos os dashboards PRODAM.
"""
import os, shutil, json

BASE = "/home/ubuntu/RASTREABILIDADE_DASHBOARDS_PRODAM"

# Limpar se existir
if os.path.exists(BASE):
    shutil.rmtree(BASE)

# ============================================================
# ESTRUTURA DE PASTAS
# ============================================================
dirs = [
    # Raiz
    f"{BASE}",
    
    # 01 - Todos os dashboards por versão
    f"{BASE}/01_DASHBOARDS",
    f"{BASE}/01_DASHBOARDS/FASE_1_PROTOTIPOS",
    f"{BASE}/01_DASHBOARDS/FASE_2_CONSOLIDACAO_v4",
    f"{BASE}/01_DASHBOARDS/FASE_3_REDESIGN_v5",
    f"{BASE}/01_DASHBOARDS/FASE_4_CORPORATIVO_v6",
    f"{BASE}/01_DASHBOARDS/FASE_5_FINAL_v8",
    
    # 02 - Fontes de dados por tipo
    f"{BASE}/02_FONTES_DE_DADOS",
    f"{BASE}/02_FONTES_DE_DADOS/JSON",
    f"{BASE}/02_FONTES_DE_DADOS/CSV",
    f"{BASE}/02_FONTES_DE_DADOS/MARKDOWN",
    f"{BASE}/02_FONTES_DE_DADOS/SCRIPTS_PY",
    f"{BASE}/02_FONTES_DE_DADOS/SCRIPTS_JS",
    
    # 03 - Rastreabilidade por seção
    f"{BASE}/03_RASTREABILIDADE_POR_SECAO",
    
    # 04 - Rastreabilidade por devedor
    f"{BASE}/04_RASTREABILIDADE_POR_DEVEDOR",
    
    # 05 - Evolução entre versões
    f"{BASE}/05_EVOLUCAO_VERSOES",
    
    # 06 - Cadeia de custódia
    f"{BASE}/06_CADEIA_DE_CUSTODIA",
]

for d in dirs:
    os.makedirs(d, exist_ok=True)

# ============================================================
# COPIAR DASHBOARDS POR FASE
# ============================================================
dash_map = {
    "FASE_1_PROTOTIPOS": [
        ("/home/ubuntu/all_dashboards/DASHBOARD_PRODAM_CORPORATIVO.html", "DASHBOARD_PRODAM_CORPORATIVO.html"),
        ("/home/ubuntu/all_dashboards/DASHBOARD_PRODAM_SESSAO54_JURIDICO.html", "DASHBOARD_PRODAM_SESSAO54_JURIDICO.html"),
        ("/home/ubuntu/all_dashboards/dashboard_prodam_2026-04-09.html", "dashboard_prodam_2026-04-09.html"),
    ],
    "FASE_2_CONSOLIDACAO_v4": [
        ("/home/ubuntu/all_dashboards/DASHBOARD_PRODAM_v1_BRANDAO_OZORES.html", "DASHBOARD_PRODAM_v1_BRANDAO_OZORES.html"),
        ("/home/ubuntu/all_dashboards/DASHBOARD_PRODAM_v4_ENRIQUECIDO.html", "DASHBOARD_PRODAM_v4_ENRIQUECIDO.html"),
        ("/home/ubuntu/upload/pasted_file_nudVmu_DASHBOARD_PRODAM_v4.1_BRANDAO_OZORES.html", "DASHBOARD_PRODAM_v4.1_BRANDAO_OZORES.html"),
    ],
    "FASE_3_REDESIGN_v5": [
        ("/home/ubuntu/DASHBOARD_PRODAM_v5.0_BRANDAO_OZORES.html", "DASHBOARD_PRODAM_v5.0_BRANDAO_OZORES.html"),
        ("/home/ubuntu/DASHBOARD_PRODAM_v5.1_BRANDAO_OZORES.html", "DASHBOARD_PRODAM_v5.1_BRANDAO_OZORES.html"),
        ("/home/ubuntu/DASHBOARD_PRODAM_v5.2_BRANDAO_OZORES.html", "DASHBOARD_PRODAM_v5.2_BRANDAO_OZORES.html"),
        ("/home/ubuntu/DASHBOARD_PRODAM_v5.3_BRANDAO_OZORES.html", "DASHBOARD_PRODAM_v5.3_BRANDAO_OZORES.html"),
    ],
    "FASE_4_CORPORATIVO_v6": [
        ("/home/ubuntu/all_dashboards/DASHBOARD_PRODAM_v6.0_BRANDAO_OZORES.html", "DASHBOARD_PRODAM_v6.0_BRANDAO_OZORES.html"),
        ("/home/ubuntu/all_dashboards/DASHBOARD_PRODAM_v6.1_BRANDAO_OZORES.html", "DASHBOARD_PRODAM_v6.1_BRANDAO_OZORES.html"),
        ("/home/ubuntu/all_dashboards/DASHBOARD_PRODAM_v6.2_BRANDAO_OZORES.html", "DASHBOARD_PRODAM_v6.2_BRANDAO_OZORES.html"),
        ("/home/ubuntu/all_dashboards/DASHBOARD_PRODAM_v6.3_BRANDAO_OZORES.html", "DASHBOARD_PRODAM_v6.3_BRANDAO_OZORES.html"),
    ],
    "FASE_5_FINAL_v8": [
        ("/home/ubuntu/all_dashboards/DASHBOARD_PRODAM_v8.0_BRANDAO_OZORES.html", "DASHBOARD_PRODAM_v8.0_BRANDAO_OZORES.html"),
    ],
}

for fase, files in dash_map.items():
    for src, dst in files:
        if os.path.exists(src):
            shutil.copy2(src, f"{BASE}/01_DASHBOARDS/{fase}/{dst}")
            print(f"  ✓ Copiado {dst} → {fase}")

# ============================================================
# COPIAR FONTES DE DADOS POR TIPO
# ============================================================
# JSON
json_files = {
    "profiles_projeto_prodam.json": "/home/ubuntu/prodam_data/profiles.json",
    "profiles_spcf_mar2026.json": "/home/ubuntu/spcf_data/profiles.json",
    "DASHBOARD_DADOS_FINAIS_projeto_prodam.json": "/home/ubuntu/prodam_data/DASHBOARD_DADOS_FINAIS.json",
    "DASHBOARD_DADOS_FINAIS_spcf.json": "/home/ubuntu/spcf_data/DASHBOARD_DADOS_FINAIS.json",
    "BLOCO_B_SERIE_HISTORICA.json": "/home/ubuntu/spcf_data/BLOCO_B_SERIE_HISTORICA.json",
    "BLOCO_D_CONSOLIDACAO.json": "/home/ubuntu/spcf_data/BLOCO_D_CONSOLIDACAO.json",
    "BLOCO_D_EMPENHOS.json": "/home/ubuntu/spcf_data/BLOCO_D_EMPENHOS.json",
    "DADOS_NOVOS_POR_DEVEDOR.json": "/home/ubuntu/spcf_data/DADOS_NOVOS_POR_DEVEDOR.json",
    "BLOCO_A_CRUZAMENTOS_CANCELADAS.json": "/home/ubuntu/spcf_data/BLOCO_A_CRUZAMENTOS_CANCELADAS.json",
    "GRUPO1_CANCELADAS_RESULTADO.json": "/home/ubuntu/spcf_data/GRUPO1_CANCELADAS_RESULTADO.json",
    "reconciliacao_spcf_2026-03-30.json": "/home/ubuntu/upload/pasted_file_98c8R1_reconciliacao_spcf_2026-03-30.json",
    "reconciliacao_spcf_2026-04-01.json": "/home/ubuntu/upload/pasted_file_NJpcrb_reconciliacao_spcf_2026-04-01.json",
    "all_dashboards_analysis.json": "/home/ubuntu/all_dashboards_analysis.json",
}
for dst, src in json_files.items():
    if os.path.exists(src):
        shutil.copy2(src, f"{BASE}/02_FONTES_DE_DADOS/JSON/{dst}")
        print(f"  ✓ JSON: {dst}")

# CSV
csv_dirs = ["/home/ubuntu/prodam_data/faturas/", "/home/ubuntu/spcf_data/faturas/"]
for csv_dir in csv_dirs:
    if os.path.isdir(csv_dir):
        suffix = "projeto_prodam" if "prodam_data" in csv_dir else "spcf_mar2026"
        for f in os.listdir(csv_dir):
            if f.endswith('.csv'):
                shutil.copy2(os.path.join(csv_dir, f), f"{BASE}/02_FONTES_DE_DADOS/CSV/{f}")
                print(f"  ✓ CSV: {f}")

# Markdown
md_files = {
    "RECONCILIACAO_SPCF_MAR2026.md": "/home/ubuntu/upload/RECONCILIACAO_SPCF_MAR2026.md",
    "CHANGELOG_RECONCILIACAO_31_03_2026.md": "/home/ubuntu/upload/CHANGELOG_RECONCILIACAO_31_03_2026.md",
    "CHANGELOG_INTEGRACAO_EXAUSTIVA.md": "/home/ubuntu/upload/CHANGELOG_INTEGRACAO_EXAUSTIVA.md",
    "RESUMO_FATURAS_TOP20.md": "/home/ubuntu/upload/RESUMO_FATURAS_TOP20.md",
    "VERIFICACAO_EXTRAIDO_COMPLETO.md": "/home/ubuntu/upload/VERIFICACAO_EXTRAIDO_COMPLETO.md",
    "reconciliacao_spcf_2026-03-30.md": "/home/ubuntu/upload/pasted_file_Hyw69E_reconciliacao_spcf_2026-03-30.md",
    "reconciliacao_spcf_2026-04-01.md": "/home/ubuntu/upload/pasted_file_cZ7Ryz_reconciliacao_spcf_2026-04-01.md",
    "INDEX_ARQUIVOS.md": "/home/ubuntu/upload/INDEX_ARQUIVOS.md",
    "RASTREABILIDADE_FORENSE_v5.3.md": "/home/ubuntu/RASTREABILIDADE_FORENSE_DASHBOARD_v5.3.md",
    "MAPEAMENTO_COMPLETO_SPCF_MAR2026.md": "/home/ubuntu/MAPEAMENTO_COMPLETO_SPCF_MAR2026.md",
    "MAPEAMENTO_COMPLETO_PROJETO_PRODAM.md": "/home/ubuntu/MAPEAMENTO_COMPLETO_PROJETO_PRODAM.md",
    "DOSSIE_EXECUTIVO_PROJETO_PRODAM.md": "/home/ubuntu/DOSSIE_EXECUTIVO_PROJETO_PRODAM.md",
    "SCRIPT_APRESENTACAO_DASHBOARD_v5.3.md": "/home/ubuntu/SCRIPT_APRESENTACAO_DASHBOARD_v5.3.md",
}
for dst, src in md_files.items():
    if os.path.exists(src):
        shutil.copy2(src, f"{BASE}/02_FONTES_DE_DADOS/MARKDOWN/{dst}")
        print(f"  ✓ MD: {dst}")

# Scripts Python
py_files = {
    "build_dashboard_v50.py": "/home/ubuntu/build_dashboard.py",
    "inject_reconciliacao_v51.py": "/home/ubuntu/inject_reconciliacao.py",
    "build_dashboard_v52.py": "/home/ubuntu/build_dashboard_v52.py",
    "build_dashboard_v53.py": "/home/ubuntu/build_dashboard_v53.py",
    "analyze_prodam_data.py": "/home/ubuntu/analyze_prodam_data.py",
    "analyze_spcf_complete.py": "/home/ubuntu/analyze_spcf_complete.py",
    "analyze_all_dashboards.py": "/home/ubuntu/analyze_all_dashboards.py",
}
for dst, src in py_files.items():
    if os.path.exists(src):
        shutil.copy2(src, f"{BASE}/02_FONTES_DE_DADOS/SCRIPTS_PY/{dst}")
        print(f"  ✓ PY: {dst}")

# Scripts JS
js_files = {
    "dashboard_script_v50.js": "/home/ubuntu/dashboard_script.js",
}
for dst, src in js_files.items():
    if os.path.exists(src):
        shutil.copy2(src, f"{BASE}/02_FONTES_DE_DADOS/SCRIPTS_JS/{dst}")
        print(f"  ✓ JS: {dst}")

print("\n✓ Estrutura de pastas criada com sucesso!")
print(f"  Base: {BASE}")

# Contar
total = 0
for root, dirs_list, files_list in os.walk(BASE):
    total += len(files_list)
print(f"  Total de arquivos: {total}")
