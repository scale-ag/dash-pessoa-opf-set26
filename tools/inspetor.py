#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FERRAMENTA TEMPORARIA (nao faz parte da engine).

Roda no runner do GitHub Actions - que alcanca docs.google.com, o que o sandbox
do agente nao alcanca (ver CLAUDE.md, problema conhecido #4).

Objetivo: descobrir, para as planilhas de um cliente novo:
  - nome de cada aba + gid correspondente
  - cabecalho completo (todas as colunas, com indice) de cada aba usada
  - Campaign Names distintos  -> sigla do funil
  - Produtos distintos        -> MAIN_PRODUCT_PREFIX
  - cruzamento UTM x Meta     -> AD_UTM_COLUMN (o erro que zera atribuicao)

SOMENTE LEITURA. Nunca escreve nas planilhas.
"""
from __future__ import annotations

import csv
import io
import re
import sys
import unicodedata
import urllib.request
import zipfile
from collections import Counter

META_ID = "1oXEzPBmdYVGD-2gplchyHK0t6nz4JdtlDTnB5skqZPY"
SALES_ID = "18OmJKQHTcjyz3z2i1cisQL9WJGRt27lxU97LRA4Znak"
ABA_VENDAS = "novas vendas"          # aba pedida pelo cliente (normalizada)

UA = {"User-Agent": "Mozilla/5.0 (compatible; dash-inspetor/1.0)"}


def get(url: str, timeout: int = 90) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def norm(s) -> str:
    s = "".join(c for c in unicodedata.normalize("NFKD", str(s or ""))
                if not unicodedata.combining(c))
    return s.strip().lower()


def head(txt: str, n: int = 200) -> str:
    return txt[:n].replace("\n", " ")


def sheet_names_via_xlsx(sid: str) -> list[str]:
    """Nomes das abas, na ordem, lidos do proprio .xlsx (sem dependencia externa)."""
    raw = get(f"https://docs.google.com/spreadsheets/d/{sid}/export?format=xlsx")
    if raw[:2] != b"PK":
        raise RuntimeError("resposta nao e um xlsx (planilha pode nao estar publica): "
                           + head(raw[:300].decode("utf-8", "replace")))
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        wb = z.read("xl/workbook.xml").decode("utf-8", "replace")
    return re.findall(r'<sheet[^>]*name="([^"]*)"', wb)


def gids_via_html(sid: str) -> list[str]:
    """Todos os gids que aparecem na pagina da planilha, na ordem de 1a aparicao."""
    found: list[str] = []
    for path in ("edit", "htmlview"):
        try:
            html = get(f"https://docs.google.com/spreadsheets/d/{sid}/{path}").decode("utf-8", "replace")
        except Exception as e:                     # noqa: BLE001
            print(f"    (aviso: /{path} falhou: {e})")
            continue
        for pat in (r'"gid":"?(\d+)"?', r'gid=(\d+)', r'#rangeid=(\d+)'):
            for g in re.findall(pat, html):
                if g not in found:
                    found.append(g)
    return found


def csv_rows(sid: str, gid: str) -> list[list[str]] | None:
    url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid={gid}"
    try:
        raw = get(url).decode("utf-8", "replace")
    except Exception as e:                          # noqa: BLE001
        print(f"    gid={gid}: ERRO {e}")
        return None
    if raw.lstrip()[:1] == "<":
        print(f"    gid={gid}: veio HTML (sem permissao/gid inexistente)")
        return None
    return list(csv.reader(io.StringIO(raw)))


def mapear_planilha(rotulo: str, sid: str) -> dict[str, list[list[str]]]:
    """Imprime abas/gids e devolve {gid: rows} para cada gid legivel."""
    print(f"\n{'='*78}\n{rotulo}  —  https://docs.google.com/spreadsheets/d/{sid}\n{'='*78}")
    try:
        nomes = sheet_names_via_xlsx(sid)
        print(f"  Abas (ordem real, via xlsx): {nomes}")
    except Exception as e:                          # noqa: BLE001
        print(f"  !! nao consegui ler os nomes das abas: {e}")
        nomes = []

    gids = gids_via_html(sid)
    print(f"  gids encontrados na pagina: {gids}")

    out: dict[str, list[list[str]]] = {}
    for gid in gids:
        rows = csv_rows(sid, gid)
        if rows is None:
            continue
        hdr = rows[0] if rows else []
        n = max(0, len(rows) - 1)
        out[gid] = rows
        print(f"    gid={gid:>12}  linhas={n:<6} colunas={len(hdr):<4} header[:6]={hdr[:6]}")
    return out


def escolher(mapa: dict[str, list[list[str]]], nome_alvo: str | None,
             nomes_abas: list[str]) -> tuple[str, list[list[str]]]:
    """Escolhe o gid da aba desejada: casa pelo nome quando da, senao o maior."""
    if nome_alvo:
        for gid, rows in mapa.items():
            hdr = [norm(h) for h in (rows[0] if rows else [])]
            if any(nome_alvo in h for h in hdr):
                return gid, rows
    # heuristica: a aba de dados e a que tem mais linhas
    gid = max(mapa, key=lambda g: len(mapa[g]))
    return gid, mapa[gid]


def dump_header(rotulo: str, rows: list[list[str]]) -> None:
    hdr = rows[0] if rows else []
    print(f"\n--- {rotulo}: {len(hdr)} colunas, {max(0, len(rows)-1)} linhas de dados ---")
    for i, h in enumerate(hdr):
        print(f"    [{i:>2}] {h!r}")
    print("  amostra (ate 3 linhas, cada celula truncada em 40 chars):")
    for row in rows[1:4]:
        print("    " + " | ".join(head(str(c), 40) for c in row[:20]))


def distintos(rows: list[list[str]], idx: int | None, rotulo: str, limite: int = 40) -> Counter:
    c: Counter = Counter()
    if idx is None:
        print(f"  {rotulo}: coluna ausente")
        return c
    for row in rows[1:]:
        v = (row[idx] if idx < len(row) else "").strip()
        if v:
            c[v] += 1
    print(f"  {rotulo}: {len(c)} valores distintos")
    for v, n in c.most_common(limite):
        print(f"      {n:>5}x  {v!r}")
    return c


def col(hdr: list[str], *nomes: str) -> int | None:
    hn = [norm(h) for h in hdr]
    for nome in nomes:
        a = norm(nome)
        for i, h in enumerate(hn):
            if h == a:
                return i
    for nome in nomes:                              # 2a passada: substring
        a = norm(nome)
        for i, h in enumerate(hn):
            if a and a in h:
                return i
    return None


def main() -> int:
    meta_mapa = mapear_planilha("PLANILHA META ADS", META_ID)
    sales_mapa = mapear_planilha("PLANILHA COMPRADORES", SALES_ID)
    if not meta_mapa or not sales_mapa:
        print("\n!! nao consegui ler alguma das planilhas — confira se estao "
              "compartilhadas como 'qualquer pessoa com o link pode ver'.")
        return 1

    meta_gid, meta_rows = escolher(meta_mapa, "campaign", [])
    sales_gid, sales_rows = escolher(sales_mapa, None, [])

    # a aba pedida e "Novas Vendas": tenta casar por nome de aba->gid via xlsx
    print(f"\n>>> GID escolhido para META ADS   : {meta_gid}")
    print(f">>> GID escolhido para COMPRADORES: {sales_gid}  (verificar se e a aba 'Novas Vendas')")

    dump_header("META ADS", meta_rows)
    dump_header("COMPRADORES", sales_rows)

    mh = meta_rows[0]
    i_camp = col(mh, "campaign name", "campaign")
    i_adset = col(mh, "ad set name", "ad set", "adset")
    i_ad = col(mh, "ad name")
    print("\n===== META ADS: valores distintos =====")
    camps = distintos(meta_rows, i_camp, "Campaign Name")
    adsets = distintos(meta_rows, i_adset, "Ad Set Name", 25)
    ads = distintos(meta_rows, i_ad, "Ad Name", 40)

    sh = sales_rows[0]
    print("\n===== COMPRADORES: valores distintos =====")
    i_prod = col(sh, "produto", "product")
    distintos(sales_rows, i_prod, "PRODUTO")
    i_status = col(sh, "status")
    distintos(sales_rows, i_status, "STATUS", 20)

    print("\n  colunas candidatas a RECEITA:")
    for i, h in enumerate(sh):
        if any(k in norm(h) for k in ("faturamento", "valor", "preco", "amount", "value", "receita", "total")):
            amostra = [ (r[i] if i < len(r) else "") for r in sales_rows[1:6] ]
            print(f"      [{i:>2}] {h!r}  amostra={amostra}")

    # ---------- cruzamento UTM x Meta (define AD_UTM_COLUMN) ----------
    print(f"\n{'='*78}\nCRUZAMENTO UTM x META  (define AD_UTM_COLUMN)\n{'='*78}")
    alvos = {"Campaign Name": {norm(v) for v in camps},
             "Ad Set Name": {norm(v) for v in adsets},
             "Ad Name": {norm(v) for v in ads}}
    print(f"{'coluna UTM':<16}{'preench.':>9} | " + " | ".join(f"{k:>14}" for k in alvos))
    print("-" * 78)
    achou_utm = False
    for utm in ("utm_campaign", "utm_medium", "utm_term", "utm_content", "utm_source"):
        i = col(sh, utm, utm.replace("_", " "))
        if i is None:
            print(f"{utm:<16}{'AUSENTE':>9} |")
            continue
        achou_utm = True
        vals = [(r[i] if i < len(r) else "").strip() for r in sales_rows[1:]]
        vals = [v for v in vals if v]
        linha = f"{utm:<16}{len(vals):>9} | "
        linha += " | ".join(f"{sum(1 for v in vals if norm(v) in alvo):>14}" for alvo in alvos.values())
        print(linha)
        print(f"    amostra {utm}: {sorted({v for v in vals})[:6]}")
    if not achou_utm:
        print("  !! nenhuma coluna utm_* encontrada na planilha de Compradores.")

    print("\n>>> Leia a tabela: a coluna UTM que carrega o Ad Name e a que bate")
    print(">>> quase 100% na coluna 'Ad Name'. Casar pela errada zera a atribuicao.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
