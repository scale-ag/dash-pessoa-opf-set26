#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sondagem TEMPORARIA das planilhas do cliente (roda no runner do GitHub Actions,
que alcanca docs.google.com — o sandbox do agente nao alcanca).

v2: corrige o filtro de PII (que estava escondendo Campaign/Ad Set/Ad Name) e
a deteccao de abas/gids. Imprime SOMENTE metadados nao-sensiveis; nome, e-mail
e telefone de lead/comprador continuam omitidos.

Removido do repositorio depois da configuracao.
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

# Colunas do Meta Ads que PARECEM PII pelo nome ("...Name") mas nao sao.
ALLOW = ("campaign name", "ad set name", "ad name", "campaign", "ad set")
# Conteudo que nunca deve ser impresso (PII de lead/comprador).
PII = ("nome", "mail", "zap", "whats", "telefone", "celular", "cpf",
       "documento", "endereco", "address", "phone")


def get(url: str) -> tuple[str, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "dash-probe/1.0"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read().decode("utf-8", errors="replace"), r.geturl()


def dump_tabs(label: str, sid: str) -> None:
    print(f"\n{'=' * 78}\nABAS — {label}\n{'=' * 78}")
    for kind in ("htmlview", "edit", "pubhtml"):
        url = f"https://docs.google.com/spreadsheets/d/{sid}/{kind}"
        try:
            html, final = get(url)
        except Exception as e:                          # noqa: BLE001
            print(f"  [{kind}] falhou: {e}")
            continue
        print(f"  [{kind}] {len(html)} bytes; url final: {final[:110]}")
        pares = re.findall(r'href="#gid=(\d+)"[^>]*>([^<]{1,60})<', html)
        pares += [(g, n) for n, g in re.findall(r'\{"1":"([^"]{1,60})","2":(\d+)', html)]
        pares += [(g, n) for n, g in re.findall(r'"name"\s*:\s*"([^"]{1,60})"[^}]{0,80}?"gid"\s*:\s*"?(\d+)', html)]
        vistos = set()
        for gid, name in pares:
            if (gid, name) in vistos:
                continue
            vistos.add((gid, name))
            print(f"        gid={gid:<14} {name.strip()}")
        if not pares:
            achados = sorted(set(re.findall(r'gid[=":\s]{1,4}(\d{1,12})', html)))[:15]
            print(f"        (sem pares nome/gid; numeros perto de 'gid': {achados})")


def read_csv(url: str) -> list[list[str]]:
    txt, _ = get(url)
    return list(csv.reader(io.StringIO(txt)))


def col(rows: list[list[str]], i: int) -> list[str]:
    return [r[i].strip() for r in rows[1:] if i < len(r) and r[i].strip()]


def report(label: str, rows: list[list[str]], full: tuple[str, ...]) -> None:
    header = rows[0] if rows else []
    body = [r for r in rows[1:] if any((c or "").strip() for c in r)]
    print(f"\n### {label}: {len(header)} colunas, {len(body)} linhas com conteudo")
    for i, h in enumerate(header):
        hl = " ".join(h.split()).strip().lower()
        if not hl:
            continue
        rotulo = " ".join(h.split())[:70]
        if hl not in ALLOW and any(p in hl for p in PII):
            print(f"  [{i:>2}] {rotulo}: <omitido — PII>")
            continue
        vals = col(rows, i)
        if not vals:
            print(f"  [{i:>2}] {rotulo}: (vazia)")
            continue
        cnt = Counter(vals)
        limit = 60 if (hl in ALLOW or any(k in hl for k in full)) else 4
        print(f"  [{i:>2}] {rotulo}: {len(cnt)} distintos, {len(vals)} preenchidos")
        for v, n in cnt.most_common(limit):
            print(f"         {n:>5}x  {v[:100]}")
        if len(cnt) > limit:
            print(f"         ... (+{len(cnt) - limit} outros)")


def main() -> int:
    dump_tabs("planilha META ADS", META_ID)
    dump_tabs("planilha COMPRADORES", SALES_ID)

    print(f"\n{'=' * 78}\nMETA ADS (primeira aba)\n{'=' * 78}")
    try:
        mrows = read_csv(f"https://docs.google.com/spreadsheets/d/{META_ID}/export?format=csv")
        report("META ADS", mrows, ("day", "data"))
    except Exception as e:                              # noqa: BLE001
        print(f"ERRO: {e}")

    print(f"\n{'=' * 78}\nCOMPRADORES — comparando 1a aba x aba 'BASE COMPLETA' (gviz)\n{'=' * 78}")
    try:
        s1 = read_csv(f"https://docs.google.com/spreadsheets/d/{SALES_ID}/export?format=csv")
        print(f"1a aba: {len(s1[0])} colunas, {len(s1) - 1} linhas")
    except Exception as e:                              # noqa: BLE001
        print(f"ERRO 1a aba: {e}")
        s1 = []
    try:
        g = read_csv(f"https://docs.google.com/spreadsheets/d/{SALES_ID}"
                     "/gviz/tq?tqx=out:csv&sheet=BASE%20COMPLETA")
        print(f"BASE COMPLETA (gviz): {len(g[0])} colunas, {len(g) - 1} linhas")
        print(f"mesmo cabecalho da 1a aba? {bool(s1) and g[0] == s1[0]}")
    except Exception as e:                              # noqa: BLE001
        print(f"ERRO gviz BASE COMPLETA: {e}")

    if s1:
        report("COMPRADORES (1a aba)", s1, ("produto", "utm", "faturamento", "data",
                                            "order bump", "pagina", "form", "status"))
        # Linhas cruas SEM PII, para entender o significado de "Faturamento liquido".
        print("\n--- 8 primeiras linhas, apenas colunas nao-PII (0-14) ---")
        idx = [i for i, h in enumerate(s1[0][:15])
               if not any(p in " ".join(h.split()).lower() for p in PII)]
        print("    " + " | ".join(" ".join(s1[0][i].split())[:22] for i in idx))
        for r in s1[1:9]:
            print("    " + " | ".join((r[i].strip()[:22] if i < len(r) else "") for i in idx))
    return 0


if __name__ == "__main__":
    sys.exit(main())
