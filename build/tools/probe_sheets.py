#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sondagem v3 — identifica os gids das abas (roda no runner do Actions)."""
from __future__ import annotations

import csv
import io
import re
import sys
import urllib.request

META_ID = "1BLv_PQ3eHD0hPQjUckx5SkkUTpHLaU-ODAHWA_biKpU"
SALES_ID = "1DXw8stvgyBo7AO-7hf2TSX1nt34v7yroJHmfge3bnPI"


def get(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "dash-probe/1.0"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read().decode("utf-8", errors="replace")


def shape(sid: str, gid: str | None) -> str:
    """Dimensoes + primeiros cabecalhos da aba (nada de conteudo de linha)."""
    url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv"
    if gid is not None:
        url += f"&gid={gid}"
    try:
        rows = list(csv.reader(io.StringIO(get(url))))
    except Exception as e:                              # noqa: BLE001
        return f"ERRO: {e}"
    head = rows[0] if rows else []
    corpo = [r for r in rows[1:] if any((c or "").strip() for c in r)]
    prim = " | ".join(" ".join(h.split())[:26] for h in head[:6])
    return f"{len(head):>3} colunas, {len(corpo):>4} linhas | {prim}"


def candidatos(sid: str) -> list[str]:
    try:
        html = get(f"https://docs.google.com/spreadsheets/d/{sid}/htmlview")
    except Exception as e:                              # noqa: BLE001
        print(f"  (htmlview falhou: {e})")
        return []
    return sorted(set(re.findall(r'gid[=":\s]{1,4}(\d{1,12})', html)))


for label, sid in (("META ADS", META_ID), ("COMPRADORES", SALES_ID)):
    print(f"\n{'=' * 78}\n{label}  ({sid})\n{'=' * 78}")
    print(f"  export SEM gid (1a aba)      -> {shape(sid, None)}")
    cands = ["0"] + [g for g in candidatos(sid) if g != "0"]
    for gid in cands:
        print(f"  gid={gid:<12} -> {shape(sid, gid)}")

sys.exit(0)
