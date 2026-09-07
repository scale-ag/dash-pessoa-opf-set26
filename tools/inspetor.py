#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FERRAMENTA TEMPORARIA — passo 2: analisa a aba 'Novas Vendas' (gid 659512725)
especificamente, compara com a aba 'Vendas' (gid 0) e quebra o Meta por sigla
de funil. SOMENTE LEITURA."""
from __future__ import annotations

import csv, io, re, sys, unicodedata, urllib.request
from collections import Counter, defaultdict

META_ID = "1oXEzPBmdYVGD-2gplchyHK0t6nz4JdtlDTnB5skqZPY"
SALES_ID = "18OmJKQHTcjyz3z2i1cisQL9WJGRt27lxU97LRA4Znak"
GID_VENDAS, GID_NOVAS = "0", "659512725"
UA = {"User-Agent": "Mozilla/5.0 (compatible; dash-inspetor/1.0)"}


def rows(sid: str, gid: str) -> list[list[str]]:
    url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid={gid}"
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=90) as r:
        return list(csv.reader(io.StringIO(r.read().decode("utf-8", "replace"))))


def norm(s) -> str:
    s = "".join(c for c in unicodedata.normalize("NFKD", str(s or "")) if not unicodedata.combining(c))
    return s.strip().lower()


def num(v: str) -> float:
    v = (v or "").strip().replace("R$", "").replace(" ", "")
    if not v:
        return 0.0
    if "," in v and "." in v:
        v = v.replace(".", "").replace(",", ".")
    elif "," in v:
        v = v.replace(",", ".")
    try:
        return float(v)
    except ValueError:
        return 0.0


def cnt(rs, i, rot, lim=30):
    c = Counter((r[i] if i < len(r) else "").strip() for r in rs[1:])
    del c[""]
    print(f"  {rot}: {len(c)} distintos")
    for v, n in c.most_common(lim):
        print(f"      {n:>4}x  {v!r}")
    return c


def datas(rs, i):
    ds = sorted({(r[i] if i < len(r) else "")[:10] for r in rs[1:] if (r[i] if i < len(r) else "").strip()})
    return (ds[0], ds[-1], len(ds)) if ds else ("-", "-", 0)


# ---------------- META ----------------
m = rows(META_ID, "0")
mh = m[0]
print("=" * 78, "\nMETA ADS — periodo e quebra por SIGLA DE FUNIL\n", "=" * 78, sep="")
d0, d1, nd = datas(m, 0)
print(f"  periodo: {d0} .. {d1}  ({nd} dias distintos)   linhas={len(m)-1}")
por_sigla: dict[str, dict] = defaultdict(lambda: {"linhas": 0, "gasto": 0.0, "camps": set()})
for r in m[1:]:
    camp = (r[1] if len(r) > 1 else "").strip()
    if not camp:
        continue
    sigla = camp.split("|")[0].strip()
    b = por_sigla[sigla]
    b["linhas"] += 1
    b["gasto"] += num(r[8] if len(r) > 8 else "")
    b["camps"].add(camp)
print(f"\n  {'sigla':<8}{'linhas':>8}{'gasto R$':>13}  campanhas")
for s, b in sorted(por_sigla.items(), key=lambda kv: -kv[1]["gasto"]):
    print(f"  {s:<8}{b['linhas']:>8}{b['gasto']:>13,.2f}  {len(b['camps'])}")
    for c in sorted(b["camps"]):
        print(f"           - {c}")
gasto_total = sum(b["gasto"] for b in por_sigla.values())
print(f"\n  GASTO TOTAL no periodo: R$ {gasto_total:,.2f}")

ads_meta = {norm(r[3]) for r in m[1:] if len(r) > 3 and r[3].strip()}
camps_meta = {norm(r[1]) for r in m[1:] if len(r) > 1 and r[1].strip()}
# sigla -> ad names
ads_por_sigla = defaultdict(set)
for r in m[1:]:
    if len(r) > 3 and r[1].strip():
        ads_por_sigla[r[1].split("|")[0].strip()].add(r[3].strip())

# ---------------- COMPRADORES: as duas abas ----------------
for gid, nome in ((GID_VENDAS, "Vendas (gid 0)"), (GID_NOVAS, "Novas Vendas (gid 659512725)")):
    s = rows(SALES_ID, gid)
    sh = s[0]
    print("\n" + "=" * 78, f"\nCOMPRADORES — aba {nome}: {len(s)-1} linhas, {len(sh)} colunas\n", "=" * 78, sep="")
    d0, d1, nd = datas(s, 4)
    print(f"  periodo (col 'Data'): {d0} .. {d1}  ({nd} dias)")
    cnt(s, 1, "PRODUTO")
    cnt(s, 11, "STATUS")
    cnt(s, 12, "CANAL", 10)
    cnt(s, 14, "utm_source", 10)
    fat = sum(num(r[8]) for r in s[1:] if len(r) > 8)
    fat_ok = sum(num(r[8]) for r in s[1:] if len(r) > 11 and norm(r[11]) == "approved")
    print(f"  Faturamento (col 8): total R$ {fat:,.2f} | so 'approved' R$ {fat_ok:,.2f}")
    print(f"  Ticket medio (approved): R$ {fat_ok / max(1, sum(1 for r in s[1:] if len(r) > 11 and norm(r[11]) == 'approved')):,.2f}")

    print("\n  --- cruzamento UTM x META nesta aba ---")
    for j, utm, alvo, rot in ((17, "utm_campaign", camps_meta, "Campaign Name"),
                              (18, "utm_content", ads_meta, "Ad Name"),
                              (16, "utm_term", ads_meta, "Ad Name")):
        vals = [(r[j] if j < len(r) else "").strip() for r in s[1:]]
        vals = [v for v in vals if v]
        hit = sum(1 for v in vals if norm(v) in alvo)
        print(f"    {utm:<14} preenchidas={len(vals):>4}  casam com {rot}: {hit}")
    # match completo campanha+anuncio (o que o build.py exige)
    par = 0
    pares_meta = {(norm(r[1]), norm(r[3])) for r in m[1:] if len(r) > 3}
    for r in s[1:]:
        c_ = norm(r[17] if len(r) > 17 else "")
        a_ = norm(r[18] if len(r) > 18 else "")
        if (c_, a_) in pares_meta:
            par += 1
    print(f"    match COMPLETO (utm_campaign + utm_content) com o Meta: {par} de {len(s)-1} linhas")
    # produtos x sigla da campanha
    print("\n  --- PRODUTO x sigla da utm_campaign ---")
    tab = defaultdict(Counter)
    for r in s[1:]:
        prod = (r[1] if len(r) > 1 else "").strip() or "(sem produto)"
        uc = (r[17] if len(r) > 17 else "").strip()
        sig = uc.split("|")[0].strip() if "|" in uc else ("(sem utm)" if not uc else uc[:22])
        tab[prod][sig] += 1
    for prod, c in tab.items():
        print(f"    {prod!r}: {dict(c.most_common(6))}")

print("\n\nANUNCIOS POR SIGLA (Meta):")
for s_, a in ads_por_sigla.items():
    print(f"  {s_}: {sorted(a)}")
