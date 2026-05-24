"""
renomeador.py — Renomeia PDFs do Projeto PRODAM com padrão canônico.

Consome:
    - um CSV de entrada gerado por `inventario_classificacao_global.py` (campos
      `caminho_original`, `nome_original`, `tipo`, `numero`, `orgao`, `data`, ...)
    - OU uma pasta de origem + classificação direta pelo filename.

Gera:
    - pasta destino (modo cópia) OU rename in-place (modo avançado).
    - CSV de mapeamento (13 campos, UTF-8 BOM, separador `;`).
    - Log em stdout.

Modos:
    copia   — DEFAULT, seguro: mantém original intocado; escreve em `<pasta>/_RENOMEADO/`.
    in_place — avançado: renomeia arquivo original. Exige `--confirm` e:
               (a) grava CSV ANTES de tocar em qualquer arquivo (roll-back manual),
               (b) calcula SHA-256 antes/depois para cada rename (detecta corrupção).

Regra jurídica absoluta (CLAUDE.md §16):
    PDFs são provas jurídicas — NUNCA apagar o arquivo; só alterar o nome.
    O modo `in_place` apenas renomeia via `Path.rename`, sem remover bytes.

Exit codes:
    0 — tudo ok
    1 — erro parcial (alguns arquivos falharam; ver CSV)
    2 — erro fatal (argumentos inválidos, pasta não existe, etc.)

Uso típico (PowerShell):
    py -3.12 renomeador.py --pasta "C:\\Caminho\\SEDUC" --devedor SEDUC --dry-run
    py -3.12 renomeador.py --input-csv "renomear_proposto.csv" --modo copia
    py -3.12 renomeador.py --pasta "..." --modo in_place --devedor DETRAN --confirm
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import shutil
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional

# Importa do módulo irmão. Quando este script é chamado direto, `sys.path`
# inclui o diretório atual; quando importado como `from scripts.renomeador`,
# a import relativa funciona.
try:
    from padroes import (
        MapaDevedor,
        MAPAS_POR_DEVEDOR,
        TIPOS_DOCUMENTO,
        asciificar,
        objeto_ta,
        parse_competencia,
        parse_ct_num,
        parse_data_br,
        parse_ne_num,
        parse_nf_num,
        parse_nl_num,
        parse_oficio_cobranca,
        parse_ta_ordinal,
        parse_tipo_doc,
        subtipo_extracao_spcf,
        tipo_certidao,
    )
except ImportError:
    from .padroes import (  # type: ignore[no-redef]
        MapaDevedor,
        MAPAS_POR_DEVEDOR,
        TIPOS_DOCUMENTO,
        asciificar,
        objeto_ta,
        parse_competencia,
        parse_ct_num,
        parse_data_br,
        parse_ne_num,
        parse_nf_num,
        parse_nl_num,
        parse_oficio_cobranca,
        parse_ta_ordinal,
        parse_tipo_doc,
        subtipo_extracao_spcf,
        tipo_certidao,
    )

# ============================================================================
# 1. GERADOR DE NOME CANÔNICO
# ============================================================================


@dataclass
class Mapeamento:
    """Linha de mapeamento entre nome original e nome canônico."""
    caminho_original: str
    nome_original: str
    nome_canonico: str
    caminho_novo: str
    tipo: str
    contrato: str
    numero: str
    objeto: str
    sha256: str
    tamanho_bytes: int
    confianca: float
    data_renomeacao: str
    modo: str

    def as_dict(self) -> dict[str, str]:
        """Retorna dict string-formatado pronto para o CSV."""
        return {
            "caminho_original": self.caminho_original,
            "nome_original": self.nome_original,
            "nome_canonico": self.nome_canonico,
            "caminho_novo": self.caminho_novo,
            "tipo": self.tipo,
            "contrato": self.contrato,
            "numero": self.numero,
            "objeto": self.objeto,
            "sha256": self.sha256,
            "tamanho_bytes": str(self.tamanho_bytes),
            "confianca": f"{self.confianca:.2f}",
            "data_renomeacao": self.data_renomeacao,
            "modo": self.modo,
        }


def gerar_nome_canonico(
    nome_original: str,
    mapa: MapaDevedor,
    orgao_hint: str = "",
    texto_ocr: str = "",
    tipo_hint: str = "",
    numero_hint: str = "",
    data_hint: str = "",
) -> dict[str, object]:
    """Gera o nome canônico para um PDF dado seu nome original + hints.

    Args:
        nome_original: nome do arquivo (com extensão).
        mapa: `MapaDevedor` do órgão em processamento.
        orgao_hint: órgão identificado pelo classificador (reforço).
        texto_ocr: conteúdo OCR das primeiras páginas (reforço).
        tipo_hint: tipo vindo do CSV de classificação (se disponível).
        numero_hint: número vindo do CSV (se disponível).
        data_hint: data vinda do CSV (se disponível).

    Returns:
        Dict com chaves: `novo_nome`, `tipo`, `contrato`, `numero`, `objeto`,
        `fora_escopo`, `confianca`.
    """
    tipo = (tipo_hint or parse_tipo_doc(nome_original, texto_ocr)).strip()
    if tipo not in TIPOS_DOCUMENTO:
        tipo = parse_tipo_doc(nome_original, texto_ocr)

    ct = parse_ct_num(nome_original, mapa)
    confianca = _estimar_confianca(nome_original, tipo, ct, numero_hint)

    # ---- Casos FORA DE ESCOPO (DIRAF) -------------------------------------
    if "DIRAF" in nome_original.upper():
        return {
            "novo_nome": "OFICIO-DIRAF_FORA-DE-ESCOPO.pdf",
            "tipo": "Oficio-DIRAF",
            "contrato": "",
            "numero": "",
            "objeto": "Oficio-DIRAF-fora-de-escopo-contratos",
            "fora_escopo": True,
            "confianca": 0.95,
        }

    # ---- NE ---------------------------------------------------------------
    if tipo == "NE":
        ne = parse_ne_num(nome_original)
        ct_tag = _ct_tag(ct) if ct else "CT-indefinido"
        ano_ne = (ne[0] if ne else "") or "AAAA"
        num_ne = (ne[1] if ne else "") or "XXXXX"
        tipo_ne = _classificar_tipo_ne(nome_original)
        novo = f"NE-{ano_ne}-{num_ne}_{ct_tag}_{tipo_ne}.pdf"
        return {
            "novo_nome": asciificar(novo),
            "tipo": tipo,
            "contrato": _contrato_pretty(ct),
            "numero": f"{ano_ne}NE{num_ne}" if ano_ne != "AAAA" else num_ne,
            "objeto": tipo_ne,
            "fora_escopo": ct is None,
            "confianca": confianca,
        }

    # ---- NL ---------------------------------------------------------------
    if tipo == "NL":
        nl = parse_nl_num(nome_original)
        ct_tag = _ct_tag(ct) if ct else "CT-indefinido"
        ano_nl = (nl[0] if nl else "") or "AAAA"
        num_nl = (nl[1] if nl else "") or "XXXXX"
        refs = _extrair_refs_ne(nome_original, texto_ocr)
        novo = f"NL-{ano_nl}-{num_nl}_{ct_tag}_Refs-{refs}.pdf"
        return {
            "novo_nome": asciificar(novo),
            "tipo": tipo,
            "contrato": _contrato_pretty(ct),
            "numero": f"{ano_nl}NL{num_nl}" if ano_nl != "AAAA" else num_nl,
            "objeto": f"Refs-{refs}",
            "fora_escopo": ct is None,
            "confianca": confianca,
        }

    # ---- NF ---------------------------------------------------------------
    if tipo == "NF":
        num_nf = parse_nf_num(nome_original) or (numero_hint or "XXXXX")
        ct_tag = _ct_tag(ct) if ct else "CT-indefinido"
        orgao = asciificar(orgao_hint or mapa.nome)
        comp = parse_competencia(nome_original, texto_ocr) or "AAAA-MM"
        novo = f"NF-{num_nf}_{ct_tag}_{orgao}_{comp}.pdf"
        return {
            "novo_nome": asciificar(novo),
            "tipo": tipo,
            "contrato": _contrato_pretty(ct),
            "numero": num_nf,
            "objeto": f"Competencia-{comp}",
            "fora_escopo": ct is None,
            "confianca": confianca,
        }

    # ---- Fatura -----------------------------------------------------------
    if tipo == "Fatura":
        fat_num = _parse_fatura_num(nome_original) or (numero_hint or "XXX")
        fat_ano = _parse_fatura_ano(nome_original) or (data_hint[:4] if data_hint else "AAAA")
        ct_tag = _ct_tag(ct) if ct else "CT-indefinido"
        comp = parse_competencia(nome_original, texto_ocr) or "AAAA-MM"
        novo = f"FAT-{fat_num}-{fat_ano}_{ct_tag}_{comp}.pdf"
        return {
            "novo_nome": asciificar(novo),
            "tipo": tipo,
            "contrato": _contrato_pretty(ct),
            "numero": f"{fat_num}/{fat_ano}",
            "objeto": f"Competencia-{comp}",
            "fora_escopo": ct is None,
            "confianca": confianca,
        }

    # ---- Aceite -----------------------------------------------------------
    if tipo == "Aceite":
        nf_ref = parse_nf_num(nome_original) or (numero_hint or "XXXXX")
        ct_tag = _ct_tag(ct) if ct else "CT-indefinido"
        fiscal = _extrair_nome_fiscal(texto_ocr) or "Fiscal-NI"
        novo = f"ACEITE-{nf_ref}_{ct_tag}_Fiscal-{fiscal}.pdf"
        return {
            "novo_nome": asciificar(novo),
            "tipo": tipo,
            "contrato": _contrato_pretty(ct),
            "numero": nf_ref,
            "objeto": f"Fiscal-{fiscal}",
            "fora_escopo": ct is None,
            "confianca": confianca,
        }

    # ---- Cobrança ---------------------------------------------------------
    if tipo == "Cobranca":
        of = parse_oficio_cobranca(nome_original)
        of_num = of[0] if of else "XXX"
        of_ano = of[1] if of else "AAAA"
        ct_tag = _ct_tag(ct) if ct else "CT-indefinido"
        data_iso = parse_data_br(texto_ocr or nome_original) or "AAAA-MM-DD"
        novo = f"COBRANCA-{of_num}-{of_ano}_{ct_tag}_{data_iso}.pdf"
        return {
            "novo_nome": asciificar(novo),
            "tipo": tipo,
            "contrato": _contrato_pretty(ct),
            "numero": f"{of_num}/{of_ano}" if of else "",
            "objeto": f"Data-{data_iso}",
            "fora_escopo": ct is None,
            "confianca": confianca,
        }

    # ---- Certidão ---------------------------------------------------------
    if tipo == "Certidao":
        subtipo = tipo_certidao(nome_original, texto_ocr)
        orgao = asciificar(orgao_hint or mapa.nome)
        data_iso = parse_data_br(texto_ocr or nome_original) or "AAAA-MM-DD"
        novo = f"CERTIDAO-{subtipo}_{orgao}_{data_iso}.pdf"
        return {
            "novo_nome": asciificar(novo),
            "tipo": tipo,
            "contrato": "",
            "numero": subtipo,
            "objeto": f"Data-{data_iso}",
            "fora_escopo": True,
            "confianca": confianca,
        }

    # ---- Extração SPCF ----------------------------------------------------
    if tipo == "Extracao-SPCF" and ct:
        sub = subtipo_extracao_spcf(nome_original)
        ct_tag = _ct_tag(ct)
        novo = f"{ct_tag}_Extracao-SPCF_{sub}_DUPLICATA.pdf"
        return {
            "novo_nome": asciificar(novo),
            "tipo": tipo,
            "contrato": _contrato_pretty(ct),
            "numero": "",
            "objeto": sub,
            "fora_escopo": False,
            "confianca": confianca,
        }

    # ---- Contrato-Base ----------------------------------------------------
    if tipo == "Contrato-Base" and ct:
        obj = mapa.objeto_contrato.get(ct, "Contrato-Base")
        regime = mapa.regime.get(ct, "")
        reg_tag = f"_Regime-{regime}" if regime else ""
        ct_tag = _ct_tag(ct)
        novo = f"{ct_tag}_Contrato-Base_{obj}{reg_tag}.pdf"
        return {
            "novo_nome": asciificar(novo),
            "tipo": tipo,
            "contrato": _contrato_pretty(ct),
            "numero": "",
            "objeto": obj,
            "fora_escopo": False,
            "confianca": confianca,
        }

    # ---- Proposta ---------------------------------------------------------
    if tipo == "Proposta" and ct:
        ct_tag = _ct_tag(ct)
        novo = f"{ct_tag}_Proposta-Comercial.pdf"
        return {
            "novo_nome": asciificar(novo),
            "tipo": tipo,
            "contrato": _contrato_pretty(ct),
            "numero": "",
            "objeto": "Proposta-Comercial",
            "fora_escopo": False,
            "confianca": confianca,
        }

    # ---- TA ---------------------------------------------------------------
    if tipo == "TA" and ct:
        ord_ta = parse_ta_ordinal(nome_original) or "XX"
        obj = objeto_ta(nome_original)
        ct_tag = _ct_tag(ct)
        if "- NE" in nome_original.upper() or "NE -" in nome_original.upper():
            novo = f"{ct_tag}_TA-{ord_ta}_NE-Cobertura.pdf"
            obj = f"NE-Cobertura_TA-{ord_ta}"
        else:
            novo = f"{ct_tag}_TA-{ord_ta}_{obj}.pdf"
        return {
            "novo_nome": asciificar(novo),
            "tipo": tipo,
            "contrato": _contrato_pretty(ct),
            "numero": ord_ta,
            "objeto": obj,
            "fora_escopo": False,
            "confianca": confianca,
        }

    # ---- Fallback ---------------------------------------------------------
    fallback_stem = asciificar(nome_original.rsplit(".", 1)[0])[:100]
    novo = f"INDEFINIDO_{fallback_stem}.pdf"
    return {
        "novo_nome": novo,
        "tipo": tipo or "Indefinido",
        "contrato": _contrato_pretty(ct) if ct else "",
        "numero": numero_hint,
        "objeto": "indefinido",
        "fora_escopo": True,
        "confianca": max(confianca * 0.5, 0.10),
    }


# ---- Helpers internos ------------------------------------------------------

def _ct_tag(ct: tuple[str, str]) -> str:
    """('006', '2021') → 'CT-006.2021'."""
    return f"CT-{ct[0]}.{ct[1]}"


def _contrato_pretty(ct: Optional[tuple[str, str]]) -> str:
    """('006', '2021') → '006/2021' (forma humana para o CSV)."""
    return f"{ct[0]}/{ct[1]}" if ct else ""


def _classificar_tipo_ne(nome: str) -> str:
    """Infere subtipo de NE pelo nome: Cobertura-Financeira / Cobertura-TA / RAP / Ordinario."""
    n = nome.upper()
    if "TA" in n and "NE" in n:
        return "Cobertura-TA"
    if "RAP" in n:
        return "RAP-Processado"
    if "COBERTURA" in n:
        return "Cobertura-Financeira"
    return "Ordinario"


def _extrair_refs_ne(nome: str, texto_ocr: str) -> str:
    """Extrai NEs referenciadas por uma NL. Retorna 'NE1+NE2' ou 'SEM-REFS'."""
    import re as _re
    refs: list[str] = []
    combinado = f"{nome} {texto_ocr}"
    for m in _re.finditer(r"(\d{4})NE(\d{5,7})", combinado, _re.IGNORECASE):
        refs.append(f"{m.group(1)}NE{m.group(2)}")
        if len(refs) >= 3:  # limite: 3 refs no nome (senão fica ilegível)
            break
    return "+".join(refs) if refs else "SEM-REFS"


def _extrair_nome_fiscal(texto_ocr: str) -> str:
    """Heurística: busca nome do fiscal responsável no atesto. Abreviado ASCII.

    Padrões comuns: "Fiscal: NOME COMPLETO", "Atestado por NOME", "Responsável: NOME".
    """
    import re as _re
    if not texto_ocr:
        return ""
    padroes = [
        r"fiscal[\s:]+([A-Z][A-Z\s\.]{5,40})",
        r"atestad[oa]\s+por[\s:]+([A-Z][A-Z\s\.]{5,40})",
        r"respons[áa]vel[\s:]+([A-Z][A-Z\s\.]{5,40})",
    ]
    for pad in padroes:
        m = _re.search(pad, texto_ocr, _re.IGNORECASE)
        if m:
            nome = asciificar(m.group(1).strip())
            # Abrevia: pega primeiro+último nome
            tokens = [t for t in nome.split("-") if len(t) > 1]
            if len(tokens) >= 2:
                return f"{tokens[0]}-{tokens[-1]}"
            return "-".join(tokens) if tokens else ""
    return ""


def _parse_fatura_num(nome: str) -> Optional[str]:
    """Extrai número da fatura (formato FAT-NNN-AAAA)."""
    import re as _re
    m = _re.search(r"(?:FAT|FATURA)[\s_:No°\.]*0*(\d{1,5})", nome, _re.IGNORECASE)
    return m.group(1).zfill(3) if m else None


def _parse_fatura_ano(nome: str) -> Optional[str]:
    """Extrai ano da fatura."""
    import re as _re
    m = _re.search(r"(?:FAT|FATURA)[\s_:No°\.]*\d{1,5}[\.\-/](\d{2,4})", nome, _re.IGNORECASE)
    if not m:
        return None
    ano = m.group(1)
    if len(ano) == 2:
        ano = ("20" if int(ano) < 80 else "19") + ano
    return ano


def _estimar_confianca(
    nome: str, tipo: str, ct: Optional[tuple[str, str]], numero_hint: str
) -> float:
    """Heurística 0.0–1.0 para confiança na renomeação.

    - 1.0  → tipo identificado + contrato parseado + número no nome
    - 0.8  → tipo identificado + contrato parseado
    - 0.6  → tipo identificado sem contrato
    - 0.4  → tipo indefinido mas com número
    - 0.2  → fallback total
    """
    score = 0.0
    if tipo != "Indefinido":
        score += 0.50
    if ct is not None:
        score += 0.30
    if numero_hint or _tem_numero_no_nome(nome):
        score += 0.20
    return round(min(score, 1.0), 2)


def _tem_numero_no_nome(nome: str) -> bool:
    """True se o stem do filename tem ≥3 dígitos consecutivos."""
    import re as _re
    stem = nome.rsplit(".", 1)[0]
    return bool(_re.search(r"\d{3,}", stem))


# ============================================================================
# 2. CLASSE PRINCIPAL
# ============================================================================


class Renomeador:
    """Orquestra a renomeação em lote de PDFs do Projeto PRODAM.

    Args:
        pasta_origem: pasta raiz com os PDFs. Busca recursiva.
        modo: `"copia"` (default, seguro) ou `"in_place"` (avançado).
        mapas_devedor: `MapaDevedor` do devedor em processamento.
        dry_run: se True, não toca em disco — só gera mapeamento + CSV.

    Uso:
        >>> r = Renomeador(Path("C:/.../DETRAN"), "copia", MAPAS_POR_DEVEDOR["DETRAN"], dry_run=True)
        >>> lista_pdfs = r.varrer_pdfs()
        >>> mapeamento = r.renomear_lote(lista_pdfs)
        >>> r.gerar_csv_mapeamento(Path("mapeamento.csv"), mapeamento)
        >>> r.aplicar_mudancas(mapeamento, confirmado=True)
    """

    def __init__(
        self,
        pasta_origem: Path,
        modo: str = "copia",
        mapas_devedor: Optional[MapaDevedor] = None,
        dry_run: bool = False,
    ) -> None:
        if modo not in ("copia", "in_place"):
            raise ValueError(f"Modo inválido: {modo!r}. Use 'copia' ou 'in_place'.")
        self.pasta_origem = Path(pasta_origem)
        self.modo = modo
        self.mapas = mapas_devedor or MAPAS_POR_DEVEDOR.get("DETRAN", next(iter(MAPAS_POR_DEVEDOR.values())))
        self.dry_run = dry_run
        self.pasta_destino = self.pasta_origem / "_RENOMEADO" if modo == "copia" else self.pasta_origem
        self._nomes_usados: set[str] = set()
        self._erros: list[str] = []

    # ---- Varredura -----------------------------------------------------

    def varrer_pdfs(self) -> list[Path]:
        """Enumera PDFs .pdf / .PDF na pasta de origem (recursivo)."""
        if not self.pasta_origem.exists():
            raise FileNotFoundError(f"Pasta não existe: {self.pasta_origem}")
        pdfs: list[Path] = []
        for ext in ("*.pdf", "*.PDF"):
            pdfs.extend(self.pasta_origem.rglob(ext))
        # Dedup por caminho absoluto normalizado (Windows case-insensitive)
        unicos: dict[str, Path] = {}
        for p in pdfs:
            unicos.setdefault(str(p.resolve()).lower(), p)
        return sorted(unicos.values())

    # ---- Loop de renomeação -------------------------------------------

    def renomear_lote(
        self,
        lista_pdfs: Iterable[Path],
        hints_por_caminho: Optional[dict[str, dict[str, str]]] = None,
    ) -> list[Mapeamento]:
        """Gera mapeamento sem tocar em disco (exceto SHA-256).

        Args:
            lista_pdfs: iterável de Paths.
            hints_por_caminho: dict `{caminho: {"tipo": ..., "numero": ..., ...}}`
                vindo de `renomear_proposto.csv` (classificação prévia). Opcional.

        Returns:
            Lista de `Mapeamento` — um por PDF processado.
        """
        hints_por_caminho = hints_por_caminho or {}
        registros: list[Mapeamento] = []
        agora = datetime.now().isoformat(timespec="seconds")

        for pdf in lista_pdfs:
            try:
                hints = hints_por_caminho.get(str(pdf), {})
                meta = gerar_nome_canonico(
                    nome_original=pdf.name,
                    mapa=self.mapas,
                    orgao_hint=hints.get("orgao", ""),
                    texto_ocr=hints.get("texto_ocr", ""),
                    tipo_hint=hints.get("tipo", ""),
                    numero_hint=hints.get("numero", ""),
                    data_hint=hints.get("data", ""),
                )
                nome_canonico = self._deduplicate(str(meta["novo_nome"]))
                sha = self._sha256(pdf)
                destino = self.pasta_destino / nome_canonico

                registros.append(Mapeamento(
                    caminho_original=str(pdf),
                    nome_original=pdf.name,
                    nome_canonico=nome_canonico,
                    caminho_novo=str(destino),
                    tipo=str(meta["tipo"]),
                    contrato=str(meta["contrato"]),
                    numero=str(meta["numero"]),
                    objeto=str(meta["objeto"]),
                    sha256=sha,
                    tamanho_bytes=pdf.stat().st_size,
                    confianca=float(meta["confianca"]),
                    data_renomeacao=agora,
                    modo=self.modo,
                ))
            except Exception as e:  # noqa: BLE001 — queremos capturar tudo no log
                self._erros.append(f"{pdf}: {e}")
                print(f"  [ERRO] {pdf.name}: {e}", file=sys.stderr)

        return registros

    def _deduplicate(self, nome: str) -> str:
        """Retorna nome único; se colidir, sufixa `_dup-02`, `_dup-03`, ..."""
        if nome not in self._nomes_usados:
            self._nomes_usados.add(nome)
            return nome
        if "." not in nome:
            stem, ext = nome, ""
        else:
            stem, ext = nome.rsplit(".", 1)
            ext = f".{ext}"
        i = 2
        while True:
            cand = f"{stem}_dup-{i:02d}{ext}"
            if cand not in self._nomes_usados:
                self._nomes_usados.add(cand)
                return cand
            i += 1

    # ---- Aplicação em disco ------------------------------------------

    def aplicar_mudancas(
        self, mapeamento: list[Mapeamento], confirmado: bool = False
    ) -> tuple[int, int]:
        """Aplica cópia ou rename em disco.

        Args:
            mapeamento: saída de `renomear_lote`.
            confirmado: obrigatório `True` para modo `in_place`.

        Returns:
            Tupla (n_ok, n_erros).

        Raises:
            RuntimeError: se `in_place` sem `confirmado=True`.
        """
        if self.dry_run:
            print(f"[DRY-RUN] {len(mapeamento)} operações simuladas — nada escrito em disco.")
            return len(mapeamento), 0

        if self.modo == "in_place" and not confirmado:
            raise RuntimeError(
                "modo in_place exige confirmado=True — risco de renomear originais."
            )

        if self.modo == "copia":
            self.pasta_destino.mkdir(parents=True, exist_ok=True)

        n_ok = n_erro = 0
        for m in mapeamento:
            origem = Path(m.caminho_original)
            destino = Path(m.caminho_novo)
            try:
                if self.modo == "copia":
                    shutil.copy2(origem, destino)
                    # Verifica integridade (SHA-256 pós-cópia)
                    sha_copia = self._sha256(destino)
                    if sha_copia != m.sha256:
                        raise RuntimeError(
                            f"SHA-256 divergente após cópia: "
                            f"orig={m.sha256[:8]} copia={sha_copia[:8]}"
                        )
                elif self.modo == "in_place":
                    # Regra jurídica: nunca apagar — só rename.
                    # Se destino já existir, dedup já garantiu nome único.
                    origem.rename(destino)
                    sha_pos = self._sha256(destino)
                    if sha_pos != m.sha256:
                        raise RuntimeError(
                            f"SHA-256 divergente após rename: "
                            f"pre={m.sha256[:8]} pos={sha_pos[:8]}"
                        )
                n_ok += 1
                if n_ok % 25 == 0:
                    print(f"  ... {n_ok} processados")
            except Exception as e:  # noqa: BLE001
                n_erro += 1
                self._erros.append(f"{origem}: {e}")
                print(f"  [ERRO] {origem.name}: {e}", file=sys.stderr)

        return n_ok, n_erro

    # ---- CSV ---------------------------------------------------------

    @staticmethod
    def gerar_csv_mapeamento(path: Path, mapeamento: list[Mapeamento]) -> None:
        """Salva mapeamento em CSV UTF-8 BOM com separador `;`.

        13 campos fixos (regra do projeto — CLAUDE.md):
            caminho_original, nome_original, nome_canonico, caminho_novo, tipo,
            contrato, numero, objeto, sha256, tamanho_bytes, confianca,
            data_renomeacao, modo.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        campos = [
            "caminho_original", "nome_original", "nome_canonico", "caminho_novo",
            "tipo", "contrato", "numero", "objeto", "sha256", "tamanho_bytes",
            "confianca", "data_renomeacao", "modo",
        ]
        with path.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=campos, delimiter=";", extrasaction="ignore")
            w.writeheader()
            for m in mapeamento:
                w.writerow(m.as_dict())

    # ---- Utilidades --------------------------------------------------

    @staticmethod
    def _sha256(path: Path) -> str:
        """SHA-256 do arquivo, em blocos de 1 MiB (baixo uso de memória)."""
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()

    def relatorio(self, mapeamento: list[Mapeamento]) -> None:
        """Imprime resumo no stdout (contagens + erros)."""
        por_tipo: dict[str, int] = {}
        for m in mapeamento:
            por_tipo[m.tipo] = por_tipo.get(m.tipo, 0) + 1
        print()
        print("=" * 60)
        print(f"RENOMEADOR PRODAM — modo={self.modo} dry_run={self.dry_run}")
        print(f"  Total       : {len(mapeamento)}")
        print(f"  Erros       : {len(self._erros)}")
        print()
        print("  Por tipo:")
        for tipo, n in sorted(por_tipo.items(), key=lambda kv: -kv[1]):
            print(f"    {tipo:<20} {n}")
        if self._erros:
            print()
            print("  Erros (primeiros 5):")
            for erro in self._erros[:5]:
                print(f"    - {erro}")
        print("=" * 60)


# ============================================================================
# 3. CLI
# ============================================================================


def _ler_hints_csv(path: Path) -> dict[str, dict[str, str]]:
    """Lê `renomear_proposto.csv` e retorna `{caminho: {tipo, numero, orgao, data}}`.

    Esperado (separador `;`, UTF-8 BOM): campos `caminho_original`, `tipo`,
    `numero`, `orgao`, `data`, `confianca`.
    """
    hints: dict[str, dict[str, str]] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f, delimiter=";")
        for row in r:
            caminho = row.get("caminho_original", "").strip()
            if not caminho:
                continue
            hints[caminho] = {
                "tipo": row.get("tipo", ""),
                "numero": row.get("numero", ""),
                "orgao": row.get("orgao", ""),
                "data": row.get("data", ""),
                "texto_ocr": row.get("texto_ocr", ""),
            }
    return hints


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Renomeia PDFs do Projeto PRODAM com padrão canônico.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--pasta", type=str, default="",
        help="Pasta de origem com PDFs (busca recursiva). Obrigatório se --input-csv não usado.",
    )
    parser.add_argument(
        "--modo", choices=("copia", "in_place"), default="copia",
        help="copia: mantém originais em _RENOMEADO/. in_place: renomeia (exige --confirm).",
    )
    parser.add_argument(
        "--devedor", type=str, default="DETRAN",
        help="Nome do devedor (chave em MAPAS_POR_DEVEDOR). Default: DETRAN.",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Simula execução sem tocar em disco; só gera CSV de mapeamento.",
    )
    parser.add_argument(
        "--confirm", action="store_true",
        help="Confirmação obrigatória para modo in_place (salvaguarda).",
    )
    parser.add_argument(
        "--input-csv", type=str, default="",
        help="CSV de entrada (renomear_proposto.csv). Alternativa a --pasta.",
    )
    parser.add_argument(
        "--output-csv", type=str, default="",
        help="Destino do CSV de mapeamento. Default: <pasta>/_MAPEAMENTO_<ts>.csv.",
    )
    args = parser.parse_args()

    # Resolve pasta
    if args.input_csv:
        input_csv = Path(args.input_csv)
        if not input_csv.exists():
            print(f"[FATAL] CSV de entrada não existe: {input_csv}", file=sys.stderr)
            return 2
        hints = _ler_hints_csv(input_csv)
        # Pasta = parent comum dos caminhos (heurística)
        caminhos = [Path(k) for k in hints]
        if not caminhos:
            print("[FATAL] CSV vazio.", file=sys.stderr)
            return 2
        pasta = Path(args.pasta) if args.pasta else caminhos[0].parent
    else:
        if not args.pasta:
            print("[FATAL] Forneça --pasta ou --input-csv.", file=sys.stderr)
            return 2
        pasta = Path(args.pasta)
        hints = {}

    # Resolve mapa
    mapa = MAPAS_POR_DEVEDOR.get(args.devedor.upper())
    if mapa is None:
        print(
            f"[FATAL] Devedor {args.devedor!r} não está em MAPAS_POR_DEVEDOR. "
            f"Disponíveis: {list(MAPAS_POR_DEVEDOR)}",
            file=sys.stderr,
        )
        return 2

    # Instancia renomeador
    try:
        r = Renomeador(pasta, args.modo, mapa, dry_run=args.dry_run)
    except (ValueError, FileNotFoundError) as e:
        print(f"[FATAL] {e}", file=sys.stderr)
        return 2

    # Enumera PDFs
    if hints:
        pdfs = [Path(k) for k in hints if Path(k).exists()]
        print(f"[INFO] {len(pdfs)} PDFs do CSV de hints existem em disco.")
    else:
        pdfs = r.varrer_pdfs()
        print(f"[INFO] {len(pdfs)} PDFs encontrados em {pasta}")

    if not pdfs:
        print("[WARN] Nenhum PDF encontrado — nada a fazer.")
        return 0

    # Renomeia (gera mapeamento)
    t0 = time.time()
    mapeamento = r.renomear_lote(pdfs, hints_por_caminho=hints)
    print(f"[INFO] Mapeamento gerado em {time.time()-t0:.1f}s ({len(mapeamento)} linhas)")

    # Decide path do CSV
    if args.output_csv:
        csv_path = Path(args.output_csv)
    else:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = pasta / f"_MAPEAMENTO_{args.devedor.upper()}_{ts}.csv"

    # Grava CSV ANTES de aplicar (segurança — roll-back manual possível)
    Renomeador.gerar_csv_mapeamento(csv_path, mapeamento)
    print(f"[INFO] CSV de mapeamento salvo em {csv_path}")

    # Aplica (ou simula)
    if args.modo == "in_place" and not args.confirm and not args.dry_run:
        print(
            "[FATAL] modo in_place requer --confirm (salvaguarda).",
            file=sys.stderr,
        )
        return 2

    n_ok, n_erro = r.aplicar_mudancas(mapeamento, confirmado=args.confirm)
    r.relatorio(mapeamento)
    print(f"[INFO] Concluído — OK: {n_ok} | Erros: {n_erro}")

    return 0 if n_erro == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
