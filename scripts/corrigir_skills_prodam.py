#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
corrigir_skills_prodam.py

Gera propostas de correção para as 17 skills do Projeto PRODAM com erros
identificados pela auditoria (Manifesto Jurídico v2026.04 rev.2).

NÃO APLICA NENHUMA ALTERAÇÃO. Apenas gera propostas_correcao.json.
A aplicação fica a cargo do script aplicar_correcoes.ps1 (revisão humana).

Uso:
    python corrigir_skills_prodam.py
    python corrigir_skills_prodam.py --dry-run   (só mecânicas, sem API)

Requisitos:
    - Python 3.10+
    - pip install anthropic --break-system-packages
    - Variável de ambiente ANTHROPIC_API_KEY configurada
    - Manifesto em: Desktop/PROJETO_PRODAM/PRODAM_DOCS/REFERENCIA_JURIDICA/
    - Skills em: ~/.claude/skills/

Custo estimado:
    - 9 correções mecânicas (C01, C04): R$ 0
    - 12 correções Opus (C05, C06, C07, C08): ~R$ 1-2 (com prompt caching)
"""

import os
import sys
import json
import re
import argparse
import time
from pathlib import Path
from datetime import datetime


# ==========================================================================
# CONFIGURAÇÕES
# ==========================================================================

SKILLS_BASE = Path.home() / ".claude" / "skills"
MANIFESTO_PATH = (
    Path.home() / "Desktop" / "PROJETO_PRODAM" / "PRODAM_DOCS" /
    "REFERENCIA_JURIDICA" / "MANIFESTO_JURIDICO_v2026_04_rev2.md"
)
OUTPUT_DIR = (
    Path.home() / "Desktop" / "PROJETO_PRODAM" / "PRODAM_DOCS" /
    "AUDITORIA_SKILLS"
)
OUTPUT_JSON = OUTPUT_DIR / "propostas_correcao.json"
LOG_PATH = OUTPUT_DIR / "correcao_log.txt"

OPUS_MODEL = "claude-opus-4-7"
HAIKU_MODEL = "claude-haiku-4-5"


# ==========================================================================
# TABELA DE ERROS (do relatório de auditoria 2026-04-24_0405)
# ==========================================================================

ERROS = [
    # ---- C01: REsp 793.969 sem José Delgado (CORREÇÃO MECÂNICA) ----
    {"skill": "classificacao-forca-probatoria", "checagem": "C01", "linhas": [70, 219], "modo": "regex"},
    {"skill": "composicao-documental-titulo", "checagem": "C01", "linhas": [94, 140, 227], "modo": "regex"},
    {"skill": "extracao-clausulas-contratuais", "checagem": "C01", "linhas": [525], "modo": "regex"},
    {"skill": "nota-liquidacao-extrator", "checagem": "C01", "linhas": [23], "modo": "regex"},
    {"skill": "pipeline-integrada-prodam", "checagem": "C01", "linhas": [162], "modo": "regex"},
    {"skill": "prodam-juridico", "checagem": "C01", "linhas": [116], "modo": "regex"},
    {"skill": "renomeador-pdfs-prodam", "checagem": "C01", "linhas": [326], "modo": "regex"},
    {"skill": "transacao-referendada-workflow", "checagem": "C01", "linhas": [110], "modo": "regex"},

    # ---- C04: SM defasado (CORREÇÃO MECÂNICA) ----
    {"skill": "risco-processual-matriz", "checagem": "C04", "linhas": [58], "modo": "regex"},

    # ---- C05: Tema 253 em autarquia (REESCRITA OPUS) ----
    {"skill": "decisao-documental-prodam", "checagem": "C05", "linhas": [286], "modo": "opus_reescrita"},
    {"skill": "prodam-juridico", "checagem": "C05", "linhas": [119], "modo": "opus_reescrita"},

    # ---- C06: Multa 2% CDC (REESCRITA OPUS) ----
    {"skill": "advogado-especialista", "checagem": "C06", "linhas": [595], "modo": "opus_reescrita"},
    {"skill": "atualizacao-monetaria-creditos", "checagem": "C06", "linhas": [531, 533], "modo": "opus_reescrita"},
    {"skill": "auditor-adversarial-monetario", "checagem": "C06", "linhas": [24], "modo": "opus_reescrita"},

    # ---- C07: Adicionar ADPF 1211 (INSERÇÃO OPUS) ----
    {"skill": "blindagem-pre-execucao", "checagem": "C07", "linhas": [], "modo": "opus_insercao"},
    {"skill": "classificacao-forca-probatoria", "checagem": "C07", "linhas": [], "modo": "opus_insercao"},
    {"skill": "montagem-dossie-comprobatorio", "checagem": "C07", "linhas": [], "modo": "opus_insercao"},
    {"skill": "montagem-dossie-devedor-detalhado", "checagem": "C07", "linhas": [], "modo": "opus_insercao"},
    {"skill": "prodam-juridico", "checagem": "C07", "linhas": [], "modo": "opus_insercao"},

    # ---- C08: Adicionar Tema 1.368 STJ (INSERÇÃO OPUS) ----
    {"skill": "atualizacao-monetaria-creditos", "checagem": "C08", "linhas": [], "modo": "opus_insercao"},
    {"skill": "atualizacao-monetaria-sob-demanda", "checagem": "C08", "linhas": [], "modo": "opus_insercao"},
]


# ==========================================================================
# CORREÇÕES MECÂNICAS (regex puro, sem API)
# ==========================================================================

# C01: Inserir ", Rel. p/ acórdão Min. José Delgado" após "Teori Zavascki"
# quando NÃO estiver seguido de "José Delgado" nos próximos 60 caracteres.
REGEX_C01 = re.compile(
    r'(Teori\s+(?:Albino\s+)?Zavascki)(?![^.]{0,60}Jos[eé]\s+Delgado)',
    flags=re.IGNORECASE
)
SUBST_C01 = r'\1, Rel. p/ acórdão Min. José Delgado'

# C04: SM 2025 defasado
REGEX_C04 = re.compile(r'R\$\s*1\.?518(?!\d)')
SUBST_C04 = r'R$ 1.621'


def aplicar_regex_c01(conteudo: str) -> tuple[str, int]:
    """Retorna (conteudo_novo, num_substituicoes)."""
    novo, n = REGEX_C01.subn(SUBST_C01, conteudo)
    return novo, n


def aplicar_regex_c04(conteudo: str) -> tuple[str, int]:
    novo, n = REGEX_C04.subn(SUBST_C04, conteudo)
    return novo, n


# ==========================================================================
# HELPERS DE LEITURA/CONTEXTO
# ==========================================================================

def ler_skill(nome_skill: str) -> tuple[Path, str]:
    """Lê o SKILL.md de uma skill. Retorna (path, conteudo)."""
    skill_dir = SKILLS_BASE / nome_skill
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        raise FileNotFoundError(f"SKILL.md não encontrado: {skill_md}")
    return skill_md, skill_md.read_text(encoding="utf-8")


def extrair_contexto(conteudo: str, linhas: list[int], janela: int = 5) -> str:
    """Extrai um trecho do arquivo em torno das linhas informadas."""
    todas_linhas = conteudo.split("\n")
    total = len(todas_linhas)
    trechos = []
    for ln in linhas:
        inicio = max(0, ln - janela - 1)
        fim = min(total, ln + janela)
        trecho = "\n".join(
            f"{n+1:4d} | {todas_linhas[n]}"
            for n in range(inicio, fim)
        )
        trechos.append(f"=== LINHAS {inicio+1}-{fim} ===\n{trecho}")
    return "\n\n".join(trechos)


# ==========================================================================
# CHAMADAS À API ANTHROPIC
# ==========================================================================

# Descrições das checagens usadas no prompt
DESCRICAO_CHECK = {
    "C05": (
        "Tema 253 STF aplicado indevidamente a DETRAN/autarquia. "
        "Tema 253 trata de empresa de economia mista em regime concorrencial, "
        "não se aplica a autarquia estadual. Autarquia (DETRAN-AM) segue Art. 100 CF "
        "(precatório/RPV). A rota alternativa é compensação administrativa via TCE-AM."
    ),
    "C06": (
        "Multa de 2% CDC/flat contra DETRAN. Decisão Gabriel 24/04/2026: tese não aplicável "
        "em contrato administrativo (relação não é de consumo). Rebaixar ou remover. "
        "Pode ser mantida só como 'tese negociável' em notificação extrajudicial, "
        "mas NÃO usar em execução. A Cláusula 12.3.2 do CT 022/2014 (multa 1%/dia máx 30 dias) "
        "protege a PRODAM contra seus contratados, não serve contra o DETRAN."
    ),
    "C07": (
        "Ausência de fundamentação sobre ADPF 1211 STF. Esta skill é sensível à natureza "
        "jurídica da PRODAM e precisa citar o precedente ADPF 1211 "
        "(Rel. Min. Flávio Dino, julgado em 16/06/2025, DJe 06/08/2025). O precedente "
        "reconhece que empresa estatal prestadora de serviço público em regime não concorrencial "
        "e sem fins lucrativos goza do regime da Fazenda Pública. "
        "A Lei AM 941/1970 (Art. 3º) confirma que a PRODAM opera com exclusividade para acionistas — "
        "prova documental direta do enquadramento. Valor primário: blindagem defensiva. "
        "Valor colateral: interesse público no recebimento dos créditos."
    ),
    "C08": (
        "Ausência de citação ao Tema 1.368 STJ (tese de outubro/2025, em rito repetitivo): "
        "'antes da Lei 14.905/2024, a SELIC é a taxa de juros moratórios aplicável às "
        "dívidas civis por interpretação do Art. 406 CC'. Importante porque abre a possibilidade "
        "de sustentar SELIC desde o vencimento das faturas pré-30/08/2024, nos contratos silentes, "
        "em vez de cair no regime Tema 810 (IPCA-E + poupança). Tese subsidiária viável para "
        "compor o cenário C1 de cálculo (valor máximo defensável)."
    ),
}


def chamar_opus_reescrita(client, manifesto: str, skill: str, checagem: str,
                          conteudo: str, linhas: list[int]) -> dict:
    """Chama Opus 4.7 para propor reescrita cirúrgica de um trecho."""
    contexto = extrair_contexto(conteudo, linhas, janela=8)
    descricao_check = DESCRICAO_CHECK.get(checagem, "")

    system_prompt = (
        "Você é especialista em direito civil e processual civil brasileiro, "
        "assessorando a reescrita cirúrgica de skills (arquivos markdown) do Projeto PRODAM. "
        "Sua tarefa é propor substituição MÍNIMA de um trecho problemático, preservando "
        "tudo o mais do arquivo intacto. NUNCA invente precedentes, leis ou números. "
        "Use apenas o que está no Manifesto Jurídico fornecido."
    )

    user_msg = f"""SKILL: `{skill}`
CHECAGEM: {checagem}
PROBLEMA: {descricao_check}

TRECHO PROBLEMÁTICO (com numeração de linhas):
```
{contexto}
```

TAREFA: Proponha substituição CIRÚRGICA. Identifique o trecho exato que deve ser trocado
e o texto novo. Mantenha o estilo/tom do arquivo.

Responda APENAS com JSON válido neste formato (sem crase nem markdown):
{{
  "trecho_antigo": "texto LITERAL que deve ser removido (copie exato do arquivo)",
  "trecho_novo": "texto que deve substituir o antigo",
  "justificativa": "breve explicação citando o item do Manifesto"
}}

Regras:
- trecho_antigo deve ser uma string ÚNICA e literal presente no conteúdo.
- Prefira trechos pequenos (1-3 linhas). Apenas o mínimo necessário.
- Se múltiplas linhas precisam mudar, abranja apenas as afetadas.
- trecho_novo deve preservar indentação, marcadores markdown, etc.
"""

    response = client.messages.create(
        model=OPUS_MODEL,
        max_tokens=1500,
        system=[
            {"type": "text", "text": system_prompt},
            {
                "type": "text",
                "text": f"MANIFESTO JURÍDICO v2026.04 rev.2 (fonte única de verdade):\n\n{manifesto}",
                "cache_control": {"type": "ephemeral"}
            }
        ],
        messages=[{"role": "user", "content": user_msg}],
    )

    texto = response.content[0].text.strip()
    # Tentar extrair JSON mesmo se vier com ```json ... ```
    if texto.startswith("```"):
        texto = re.sub(r"^```(?:json)?\s*", "", texto)
        texto = re.sub(r"\s*```$", "", texto)

    proposta = json.loads(texto)
    proposta["_tokens_input"] = response.usage.input_tokens
    proposta["_tokens_output"] = response.usage.output_tokens
    proposta["_cache_read"] = getattr(response.usage, "cache_read_input_tokens", 0)
    proposta["_cache_creation"] = getattr(response.usage, "cache_creation_input_tokens", 0)
    return proposta


def chamar_opus_insercao(client, manifesto: str, skill: str, checagem: str,
                         conteudo: str) -> dict:
    """Chama Opus 4.7 para propor INSERÇÃO de texto novo em local apropriado."""
    linhas = conteudo.split("\n")
    total = len(linhas)
    # Enviamos o arquivo inteiro numerado (se for muito grande, cortamos)
    max_linhas_contexto = 300
    if total > max_linhas_contexto:
        # Mandar só as primeiras 150 e últimas 150
        primeiras = [f"{i+1:4d} | {linhas[i]}" for i in range(150)]
        ultimas = [f"{i+1:4d} | {linhas[i]}" for i in range(total - 150, total)]
        arquivo_formatado = "\n".join(primeiras) + f"\n... [{total - 300} linhas omitidas] ...\n" + "\n".join(ultimas)
    else:
        arquivo_formatado = "\n".join(f"{i+1:4d} | {linhas[i]}" for i in range(total))

    descricao_check = DESCRICAO_CHECK.get(checagem, "")

    system_prompt = (
        "Você é especialista em direito civil e processual civil brasileiro. "
        "Sua tarefa é propor a INSERÇÃO de um trecho novo (sobre precedente jurídico) "
        "em uma skill (arquivo markdown) do Projeto PRODAM. "
        "Você decide onde inserir e o que inserir, baseado apenas no Manifesto fornecido. "
        "NUNCA invente precedentes ou leis."
    )

    user_msg = f"""SKILL: `{skill}`
CHECAGEM: {checagem}
O QUE ADICIONAR: {descricao_check}

ARQUIVO ATUAL (com numeração de linhas):
```
{arquivo_formatado}
```

TAREFA: Decida:
1. Em qual LINHA inserir o novo texto (antes de qual linha).
2. Qual é o TEXTO a inserir (em markdown, estilo coerente com o arquivo).

O texto a inserir deve ter entre 50 e 200 palavras, ser juridicamente correto,
citar o Manifesto como fonte, e se integrar bem ao contexto da linha escolhida.

Responda APENAS com JSON válido (sem crase nem markdown):
{{
  "linha_antes_de": N,
  "texto_a_inserir": "texto em markdown a inserir exatamente antes da linha N",
  "justificativa": "por que inserir nesse ponto + fonte do Manifesto"
}}
"""

    response = client.messages.create(
        model=OPUS_MODEL,
        max_tokens=2000,
        system=[
            {"type": "text", "text": system_prompt},
            {
                "type": "text",
                "text": f"MANIFESTO JURÍDICO v2026.04 rev.2 (fonte única de verdade):\n\n{manifesto}",
                "cache_control": {"type": "ephemeral"}
            }
        ],
        messages=[{"role": "user", "content": user_msg}],
    )

    texto = response.content[0].text.strip()
    if texto.startswith("```"):
        texto = re.sub(r"^```(?:json)?\s*", "", texto)
        texto = re.sub(r"\s*```$", "", texto)

    proposta = json.loads(texto)
    proposta["_tokens_input"] = response.usage.input_tokens
    proposta["_tokens_output"] = response.usage.output_tokens
    proposta["_cache_read"] = getattr(response.usage, "cache_read_input_tokens", 0)
    proposta["_cache_creation"] = getattr(response.usage, "cache_creation_input_tokens", 0)
    return proposta


# ==========================================================================
# MAIN
# ==========================================================================

def main():
    parser = argparse.ArgumentParser(description="Gera propostas de correção de skills PRODAM.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Processa apenas correções mecânicas (sem chamadas à API).")
    args = parser.parse_args()

    print("=" * 60)
    print(" CORREÇÃO DAS SKILLS PRODAM — Geração de Propostas")
    print("=" * 60)

    # 1. Verificar pré-requisitos
    if not SKILLS_BASE.exists():
        print(f"[ERRO] Pasta de skills não encontrada: {SKILLS_BASE}")
        sys.exit(1)
    if not MANIFESTO_PATH.exists():
        print(f"[ERRO] Manifesto não encontrado: {MANIFESTO_PATH}")
        sys.exit(1)

    # 2. Verificar API key (se não for dry-run)
    client = None
    if not args.dry_run:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print("[ERRO] Variável ANTHROPIC_API_KEY não definida.")
            print("       Configure com o comando que o Claude te passou antes.")
            sys.exit(1)
        try:
            import anthropic
        except ImportError:
            print("[ERRO] Biblioteca 'anthropic' não instalada.")
            print("       Execute: pip install anthropic --break-system-packages")
            sys.exit(1)
        client = anthropic.Anthropic(api_key=api_key)
        print(f"[OK]  API key configurada ({len(api_key)} chars)")
    else:
        print("[INFO] Modo DRY-RUN: apenas correções mecânicas, sem API")

    # 3. Ler Manifesto
    manifesto = MANIFESTO_PATH.read_text(encoding="utf-8")
    print(f"[OK]  Manifesto carregado ({len(manifesto):,} chars, "
          f"~{len(manifesto)//4:,} tokens)")

    # 4. Preparar saída
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    propostas = []
    total_tokens_in = 0
    total_tokens_out = 0
    total_cache_read = 0
    total_cache_write = 0
    erros_processamento = []

    # 5. Processar cada erro
    print()
    print(f"Processando {len(ERROS)} erros...")
    print()

    for idx, erro in enumerate(ERROS, 1):
        skill = erro["skill"]
        checagem = erro["checagem"]
        modo = erro["modo"]
        tag = f"[{idx:02d}/{len(ERROS):02d}] {skill} ({checagem})"

        try:
            skill_path, conteudo = ler_skill(skill)
        except FileNotFoundError as e:
            print(f"{tag} - [PULAR] {e}")
            erros_processamento.append({"skill": skill, "motivo": str(e)})
            continue

        # --- Correção mecânica ---
        if modo == "regex":
            if checagem == "C01":
                novo, n = aplicar_regex_c01(conteudo)
                if n == 0:
                    print(f"{tag} - [SKIP] regex C01 não achou padrão (já corrigido?)")
                    continue
                propostas.append({
                    "id": f"P{idx:03d}",
                    "skill": skill,
                    "arquivo": str(skill_path),
                    "checagem": checagem,
                    "tipo": "substituicao_completa",
                    "origem": "regex_local",
                    "n_substituicoes": n,
                    "conteudo_antigo": conteudo,
                    "conteudo_novo": novo,
                    "justificativa": (
                        "Citação correta do REsp 793.969/RJ conforme Manifesto v2026.04 "
                        "rev.2 Parte 1.1: Teori Zavascki foi relator originário (vencido); "
                        "acórdão redigido pelo Min. José Delgado."
                    ),
                })
                print(f"{tag} - [OK] {n} substituição(ões) C01")

            elif checagem == "C04":
                novo, n = aplicar_regex_c04(conteudo)
                if n == 0:
                    print(f"{tag} - [SKIP] regex C04 não achou padrão")
                    continue
                propostas.append({
                    "id": f"P{idx:03d}",
                    "skill": skill,
                    "arquivo": str(skill_path),
                    "checagem": checagem,
                    "tipo": "substituicao_completa",
                    "origem": "regex_local",
                    "n_substituicoes": n,
                    "conteudo_antigo": conteudo,
                    "conteudo_novo": novo,
                    "justificativa": (
                        "SM 2026 = R$ 1.621,00 (Decreto Federal 12.797/2025). "
                        "Valor anterior R$ 1.518 era de 2025. "
                        "Ver Manifesto v2026.04 rev.2 Parte 6.1."
                    ),
                })
                print(f"{tag} - [OK] {n} substituição(ões) C04")

        # --- Reescrita contextual (Opus) ---
        elif modo == "opus_reescrita":
            if args.dry_run:
                print(f"{tag} - [DRY] pulando (Opus)")
                continue
            print(f"{tag} - [API] chamando Opus 4.7...", end="", flush=True)
            try:
                t0 = time.time()
                proposta = chamar_opus_reescrita(
                    client, manifesto, skill, checagem, conteudo, erro["linhas"]
                )
                dt = time.time() - t0
                total_tokens_in += proposta.pop("_tokens_input", 0)
                total_tokens_out += proposta.pop("_tokens_output", 0)
                total_cache_read += proposta.pop("_cache_read", 0)
                total_cache_write += proposta.pop("_cache_creation", 0)
                propostas.append({
                    "id": f"P{idx:03d}",
                    "skill": skill,
                    "arquivo": str(skill_path),
                    "checagem": checagem,
                    "tipo": "substituicao_trecho",
                    "origem": "opus_4_7",
                    "linhas_afetadas": erro["linhas"],
                    **proposta,
                })
                print(f" OK ({dt:.1f}s)")
            except Exception as e:
                print(f" ERRO: {e}")
                erros_processamento.append({"skill": skill, "checagem": checagem, "motivo": str(e)})

        # --- Inserção (Opus) ---
        elif modo == "opus_insercao":
            if args.dry_run:
                print(f"{tag} - [DRY] pulando (Opus)")
                continue
            print(f"{tag} - [API] chamando Opus 4.7...", end="", flush=True)
            try:
                t0 = time.time()
                proposta = chamar_opus_insercao(client, manifesto, skill, checagem, conteudo)
                dt = time.time() - t0
                total_tokens_in += proposta.pop("_tokens_input", 0)
                total_tokens_out += proposta.pop("_tokens_output", 0)
                total_cache_read += proposta.pop("_cache_read", 0)
                total_cache_write += proposta.pop("_cache_creation", 0)
                propostas.append({
                    "id": f"P{idx:03d}",
                    "skill": skill,
                    "arquivo": str(skill_path),
                    "checagem": checagem,
                    "tipo": "insercao",
                    "origem": "opus_4_7",
                    **proposta,
                })
                print(f" OK ({dt:.1f}s)")
            except Exception as e:
                print(f" ERRO: {e}")
                erros_processamento.append({"skill": skill, "checagem": checagem, "motivo": str(e)})

    # 6. Salvar JSON
    saida = {
        "metadata": {
            "gerado_em": datetime.now().isoformat(),
            "manifesto_versao": "v2026.04 rev.2",
            "total_propostas": len(propostas),
            "tokens_input_total": total_tokens_in,
            "tokens_output_total": total_tokens_out,
            "tokens_cache_read": total_cache_read,
            "tokens_cache_write": total_cache_write,
            "erros_processamento": erros_processamento,
        },
        "propostas": propostas,
    }
    OUTPUT_JSON.write_text(json.dumps(saida, ensure_ascii=False, indent=2), encoding="utf-8")

    # 7. Estimar custo
    # Preços Opus 4.7 (abril 2026): input $5/M, output $25/M, cache read $0.5/M, cache write $6.25/M
    custo_usd = (
        (total_tokens_in - total_cache_read - total_cache_write) * 5.0 / 1_000_000
        + total_cache_read * 0.5 / 1_000_000
        + total_cache_write * 6.25 / 1_000_000
        + total_tokens_out * 25.0 / 1_000_000
    )
    custo_brl = custo_usd * 5.2  # câmbio aproximado

    # 8. Resumo final
    print()
    print("=" * 60)
    print(" RESUMO")
    print("=" * 60)
    print(f"Propostas geradas:         {len(propostas)}")
    print(f"Erros no processamento:    {len(erros_processamento)}")
    print(f"Tokens enviados (input):   {total_tokens_in:,}")
    print(f"Tokens recebidos (output): {total_tokens_out:,}")
    print(f"Tokens lidos do cache:     {total_cache_read:,} (economia ativa)")
    print(f"Tokens escritos no cache:  {total_cache_write:,}")
    print(f"Custo estimado:            US$ {custo_usd:.4f} (~ R$ {custo_brl:.2f})")
    print()
    print(f"Arquivo salvo: {OUTPUT_JSON}")
    print()
    if erros_processamento:
        print("[AVISO] Alguns erros ocorreram durante o processamento:")
        for e in erros_processamento:
            print(f"  - {e}")
        print()
    print("Próximo passo: rodar aplicar_correcoes.ps1 para revisar cada diff.")
    print()


if __name__ == "__main__":
    main()
