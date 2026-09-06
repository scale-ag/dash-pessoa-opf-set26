#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analise TEMPORARIA do cruzamento UTM x Meta Ads (roda no runner do Actions,
que alcanca docs.google.com — o sandbox do agente nao alcanca).

Nao assume nenhum mapeamento: mede, para CADA coluna UTM, quantos valores
batem com Campaign Name / Ad Set Name / Ad Name do Meta. Isso mostra qual
coluna carrega o que, em vez de confiar na convencao.

Imprime so metadados nao-sensiveis (nomes de campanha/conjunto/anuncio e UTMs).
Removido do repositorio depois da analise.
"""
from __future__ import annotations

import csv
import io
import sys
import unicodedata
import urllib.request
from collections import Counter

sys.path.insert(0, "build")
import config as cfg  # noqa: E402

EXPORT = "https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid={gid}"


def norm(s):
    s = (s or "").strip().lower()
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "dash-probe/1.0"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return list(csv.reader(io.StringIO(r.read().decode("utf-8", errors="replace"))))


def idx(header, *names):
    hn = [norm(h) for h in header]
    for n in names:
        n = norm(n)
        for i, h in enumerate(hn):
            if h == n:
                return i
        for i, h in enumerate(hn):
            if n and n in h:
                return i
    return None


def col(rows, i):
    if i is None:
        return []
    return [r[i].strip() for r in rows[1:] if i < len(r) and r[i].strip()]


meta = fetch(EXPORT.format(sid=cfg.SPREADSHEET_ID, gid=cfg.GID_META))
sales = fetch(EXPORT.format(sid=cfg.SPREADSHEET_ID_SALES, gid=cfg.GID_SALES))
mh, sh = meta[0], sales[0]
mbody = [r for r in meta[1:] if any((c or "").strip() for c in r)]
sbody = [r for r in sales[1:] if any((c or "").strip() for c in r)]

i_camp, i_adset, i_ad = idx(mh, "campaign name"), idx(mh, "ad set name"), idx(mh, "ad name")
print(f"META ADS : {len(mbody)} linhas | Day de {min(col(meta, idx(mh,'day')) or ['?'])} "
      f"a {max(col(meta, idx(mh,'day')) or ['?'])}")
print(f"VENDAS   : {len(sbody)} linhas\n")

SETS = {
    "Campaign Name": {norm(v) for v in col(meta, i_camp)},
    "Ad Set Name":   {norm(v) for v in col(meta, i_adset)},
    "Ad Name":       {norm(v) for v in col(meta, i_ad)},
}
for k, v in SETS.items():
    print(f"Meta · {k}: {len(v)} valores distintos")
    for x in sorted(v)[:8]:
        print(f"      {x[:88]}")
print()

UTMS = ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"]
print("=" * 78)
print("CADA COLUNA UTM x CADA CAMPO DO META  (quantos valores batem exatamente)")
print("=" * 78)
print(f"{'coluna UTM':14} {'preench.':>9} {'distintos':>10} " +
      " ".join(f"{k:>14}" for k in SETS))
for u in UTMS:
    i = idx(sh, u)
    vals = col(sales, i)
    if i is None:
        print(f"{u:14} {'(coluna ausente)':>9}")
        continue
    nvals = [norm(v) for v in vals]
    hits = [sum(1 for v in nvals if v in s) for s in SETS.values()]
    print(f"{u:14} {len(vals):>9} {len(set(nvals)):>10} " +
          " ".join(f"{h:>14}" for h in hits))

print("\n--- valores distintos por coluna UTM (ate 12) ---")
for u in UTMS:
    i = idx(sh, u)
    vals = col(sales, i)
    c = Counter(vals)
    print(f"\n{u} ({len(vals)} preenchidos, {len(c)} distintos):")
    for v, n in c.most_common(12):
        print(f"   {n:>5}x  {v[:92]}")

# ---- taxa de casamento campanha+anuncio sob cada hipotese ----
print("\n" + "=" * 78)
print("TAXA DE CASAMENTO (campanha + anuncio), por hipotese de coluna do anuncio")
print("=" * 78)
ad_map = {(norm(r[i_camp]), norm(r[i_ad])) for r in mbody
          if i_camp < len(r) and i_ad < len(r)}
i_ucamp = idx(sh, "utm_campaign")
for hip in ("utm_content", "utm_term", "utm_medium"):
    i_u = idx(sh, hip)
    ok = tot = 0
    for r in sbody:
        c = norm(r[i_ucamp]) if i_ucamp is not None and i_ucamp < len(r) else ""
        a = norm(r[i_u]) if i_u is not None and i_u < len(r) else ""
        if not c and not a:
            continue
        tot += 1
        if (c, a) in ad_map:
            ok += 1
    print(f"  anuncio = {hip:12} -> {ok} casamentos de {tot} linhas com UTM "
          f"(de {len(sbody)} vendas)")
print("\n(ad_map do Meta tem", len(ad_map), "pares campanha+anuncio distintos)")
