#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sondagem TEMPORARIA das planilhas do cliente (roda no runner do GitHub Actions,
que alcanca docs.google.com — o sandbox do agente nao alcanca).

Imprime SOMENTE metadados nao-sensiveis: nomes de abas/gids, cabecalhos,
valores distintos de campanha/conjunto/anuncio/produto/UTM/status e contagens.
NUNCA imprime nome, e-mail, telefone ou documento de comprador.

Este arquivo e removido do repositorio depois da configuracao.
"""
from __future__ import annotations

import csv
import io
import re
import sys
import urllib.request
from collections import Counter

META_ID = "1BLv_PQ3eHD0hPQjUckx5SkkUTpHLaU-ODAHWA_biKpU"
SALES_ID = "1DXw8stvgyBo7AO-7hf2TSX1nt34v7yroJHmfge3bnPI"

# Colunas cujo conteudo NUNCA deve ser impresso (PII de comprador).
PII = ("nome", "name", "mail", "telefone", "phone", "cpf", "documento", "doc",
       "endereco", "address", "cliente", "comprador", "celular", "whats")


def get(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "dash-probe/1.0"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read().decode("utf-8", errors="replace")


def tabs(sid: str) -> list[tuple[str, str]]:
    """Nome da aba -> gid, via htmlview (menu de abas) com fallback no edit."""
    out: list[tuple[str, str]] = []
    for url in (f"https://docs.google.com/spreadsheets/d/{sid}/htmlview",
                f"https://docs.google.com/spreadsheets/d/{sid}/edit"):
        try:
            html = get(url)
        except Exception as e:                      # noqa: BLE001
            print(f"    (falha em {url.rsplit('/', 1)[-1]}: {e})")
            continue
        # htmlview: <li id="sheet-button-123"><a href="#gid=123">Nome</a></li>
        for gid, name in re.findall(r'href="#gid=(\d+)"[^>]*>([^<]{1,80})<', html):
            out.append((name.strip(), gid))
        # edit: {"name":"Nome",...,"gid":"123"} / sheetId numerico
        if not out:
            for name, gid in re.findall(r'\{"1":"([^"]{1,80})","2":(\d+)', html):
                out.append((name.strip(), gid))
        if out:
            break
    # dedup preservando ordem
    seen, uniq = set(), []
    for name, gid in out:
        if (name, gid) not in seen:
            seen.add((name, gid))
            uniq.append((name, gid))
    return uniq


def rows_by_gid(sid: str, gid: str) -> list[list[str]]:
    url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid={gid}"
    return list(csv.reader(io.StringIO(get(url))))


def rows_first(sid: str) -> list[list[str]]:
    url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv"
    return list(csv.reader(io.StringIO(get(url))))


def col(rows: list[list[str]], i: int) -> list[str]:
    return [r[i].strip() for r in rows[1:] if i < len(r) and r[i].strip()]


def report(label: str, rows: list[list[str]], full_cols: tuple[str, ...] = ()) -> None:
    header = rows[0] if rows else []
    body = [r for r in rows[1:] if any((c or "").strip() for c in r)]
    print(f"\n### {label}: {len(header)} colunas, {len(body)} linhas com conteudo")
    print("--- CABECALHO (indice | nome) ---")
    for i, h in enumerate(header):
        print(f"  [{i:>2}] {h}")
    print("--- VALORES DISTINTOS (colunas nao-PII) ---")
    for i, h in enumerate(header):
        hl = h.strip().lower()
        if not hl:
            continue
        if any(p in hl for p in PII):
            print(f"  [{i:>2}] {h}: <omitido — coluna de PII>")
            continue
        vals = col(rows, i)
        if not vals:
            print(f"  [{i:>2}] {h}: (vazia)")
            continue
        cnt = Counter(vals)
        # Colunas pedidas por inteiro (campanha/produto/UTM); resto so amostra.
        limit = 200 if any(k in hl for k in full_cols) else 6
        top = cnt.most_common(limit)
        print(f"  [{i:>2}] {h}: {len(cnt)} distintos, {len(vals)} preenchidos")
        for v, n in top:
            print(f"         {n:>6}x  {v[:110]}")
        if len(cnt) > limit:
            print(f"         ... (+{len(cnt) - limit} outros)")


def main() -> int:
    print("=" * 78)
    print("ABAS — planilha META ADS")
    print("=" * 78)
    meta_tabs = tabs(META_ID)
    for name, gid in meta_tabs:
        print(f"  gid={gid:<14} {name}")

    print("\n" + "=" * 78)
    print("ABAS — planilha COMPRADORES")
    print("=" * 78)
    sales_tabs = tabs(SALES_ID)
    for name, gid in sales_tabs:
        print(f"  gid={gid:<14} {name}")

    FULL_META = ("campaign", "campanha", "ad set", "adset", "conjunto", "ad name", "anuncio")
    FULL_SALES = ("produto", "product", "utm", "status", "origem", "fonte", "oferta")

    # --- META ADS ---
    try:
        gid = meta_tabs[0][1] if meta_tabs else ""
        mrows = rows_by_gid(META_ID, gid) if gid else rows_first(META_ID)
        print(f"\n(meta lido com gid={gid or 'PRIMEIRA ABA'})")
        report("META ADS", mrows, FULL_META)
    except Exception as e:                          # noqa: BLE001
        print(f"ERRO ao ler META ADS: {e}")

    # --- COMPRADORES / BASE COMPLETA ---
    alvo = [(n, g) for n, g in sales_tabs if "base completa" in n.strip().lower()]
    try:
        if alvo:
            name, gid = alvo[0]
            srows = rows_by_gid(SALES_ID, gid)
            print(f"\n(compradores lido da aba '{name}', gid={gid})")
        else:
            srows = rows_first(SALES_ID)
            print("\n(ATENCAO: aba 'BASE COMPLETA' nao localizada — lida a PRIMEIRA aba)")
        report("COMPRADORES", srows, FULL_SALES)
    except Exception as e:                          # noqa: BLE001
        print(f"ERRO ao ler COMPRADORES: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
