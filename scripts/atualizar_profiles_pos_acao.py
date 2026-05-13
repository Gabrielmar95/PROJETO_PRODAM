"""Sincronizador de estado pós-ação em profiles.json.

Uso:
    # Inspecionar estado atual (read-only):
    python scripts/atualizar_profiles_pos_acao.py --devedor "SES/SUSAM" --inspecionar

    # Simular (default — NAO grava):
    python scripts/atualizar_profiles_pos_acao.py --devedor "SES/SUSAM" --acao TRD_PROTOCOLADO --data 2026-05-13 --evidencia "PRODAM_DOCS/SES_SUSAM/TRD_protocolo.pdf"

    # Gravar de verdade (exige confirmacao interativa "OK"):
    python scripts/atualizar_profiles_pos_acao.py --devedor "SES/SUSAM" --acao TRD_PROTOCOLADO --data 2026-05-13 --evidencia "PRODAM_DOCS/SES_SUSAM/TRD_protocolo.pdf" --apply
"""

from __future__ import annotations
import argparse, json, os, shutil, sys
from datetime import date, datetime
from pathlib import Path

PROFILES = Path("profiles.json")
LOG_FILE = Path("_BACKUPS") / "profile_changes.log"

# REVISAR contra a definição real de F0..F8 no projeto antes do primeiro uso.
TRANSICOES: dict[str, dict[str, str]] = {
    "TRD_GERADO": {
        "status": "TRD pronto",
        "proximo_passo": "ENVIAR_TRD",
        "fase_atual": "F3",
    },
    "TRD_PROTOCOLADO": {
        "status": "TRD protocolado",
        "proximo_passo": "AGUARDAR_RESPOSTA_30D",
        "fase_atual": "F4",
    },
    "NOTIFICACAO_PROTOCOLADA": {
        "status": "Notificacao protocolada",
        "proximo_passo": "AGUARDAR_RESPOSTA_15D",
        "fase_atual": "F2",
    },
    "RESPOSTA_RECEBIDA": {"proximo_passo": "ANALISAR_RESPOSTA"},
    "MONITORIA_PROTOCOLADA": {
        "status": "Monitoria ajuizada",
        "proximo_passo": "AGUARDAR_CITACAO",
        "fase_atual": "F6",
    },
}

CAMPOS_SNAPSHOT = [
    "nome",
    "status",
    "proximo_passo",
    "fase_atual",
    "data_protocolo",
    "ultima_interacao",
    "val_atualizado",
    "evidencia_protocolo",
]


def carregar():
    raw = PROFILES.read_text(encoding="utf-8")
    return json.loads(raw), raw


def localizar(data, alvo):
    alvo_norm = alvo.upper().replace(" ", "").replace("/", "")

    def bate(nome):
        return alvo_norm in str(nome).upper().replace(" ", "").replace("/", "")

    if isinstance(data, dict):
        for k, v in data.items():
            nome = v.get("nome", k) if isinstance(v, dict) else k
            if bate(nome):
                return v, k
    elif isinstance(data, list):
        for i, v in enumerate(data):
            if isinstance(v, dict) and bate(v.get("nome", "")):
                return v, i
    return None, None


def aplicar(perfil, acao, data_iso, evidencia):
    if acao not in TRANSICOES:
        raise SystemExit(f"Acao desconhecida: {acao}. Disponiveis: {list(TRANSICOES)}")
    hoje = date.today().isoformat()
    delta = dict(TRANSICOES[acao])
    delta["ultima_interacao"] = data_iso or hoje
    if "PROTOCOLAD" in acao:
        delta["data_protocolo"] = data_iso or hoje
        if evidencia:
            delta["evidencia_protocolo"] = evidencia
    antes = {k: perfil.get(k) for k in delta}
    perfil.update(delta)
    return {"antes": antes, "depois": delta}


def gravar(data, raw_original):
    backup = PROFILES.with_suffix(f".json.bak.{datetime.now():%Y%m%d_%H%M%S}")
    backup.write_text(raw_original, encoding="utf-8")
    tmp = PROFILES.with_suffix(".json.tmp")
    tmp.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8"
    )
    shutil.move(str(tmp), str(PROFILES))
    return backup


def logar(devedor, acao, diff, backup_path, args_raw):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "devedor": devedor,
        "acao": acao,
        "diff": diff,
        "backup": str(backup_path),
        "cmd": " ".join(args_raw),
        "cwd": os.getcwd(),
    }
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--devedor", required=True)
    ap.add_argument("--inspecionar", action="store_true")
    ap.add_argument("--acao", choices=list(TRANSICOES))
    ap.add_argument("--data", help="ISO yyyy-mm-dd; default = hoje")
    ap.add_argument("--evidencia", help="Path do PDF/print do protocolo")
    ap.add_argument(
        "--apply",
        action="store_true",
        help="GRAVA de verdade. Sem essa flag, apenas simula.",
    )
    ap.add_argument(
        "--yes",
        action="store_true",
        help="Pula confirmacao interativa (para uso em automacao).",
    )
    ap.add_argument(
        "--dry-run", action="store_true", help="(deprecated; simulacao ja e o default)"
    )
    args = ap.parse_args()

    data, raw = carregar()
    perfil, _ = localizar(data, args.devedor)
    if perfil is None:
        sys.exit(f"Devedor nao encontrado: {args.devedor}")

    if args.inspecionar or not args.acao:
        snap = {c: perfil.get(c) for c in CAMPOS_SNAPSHOT}
        print(json.dumps(snap, indent=2, ensure_ascii=False, default=str))
        return

    diff = aplicar(perfil, args.acao, args.data, args.evidencia)
    print("DIFF PROPOSTO:")
    print(json.dumps(diff, indent=2, ensure_ascii=False, default=str))

    if not args.apply:
        print("\n[SIMULACAO — nada gravado. Use --apply para gravar.]")
        return

    if not args.yes:
        resp = input('\nGravar? Digite exatamente "OK" para confirmar: ').strip()
        if resp != "OK":
            print("Abortado.")
            sys.exit(1)

    backup = gravar(data, raw)
    logar(args.devedor, args.acao, diff, backup, sys.argv)
    print(f"\nGravado. Backup: {backup}")
    print(f"Log:     {LOG_FILE}")


if __name__ == "__main__":
    main()
