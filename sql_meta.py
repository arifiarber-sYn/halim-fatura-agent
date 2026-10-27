#!/usr/bin/env python3
"""sql_meta.py — shtresa e dytë Meta: modeli PROPOZON SQL, porta vendos.

Ideja qendrore e projektit: propozim != leje. Modeli nuk ekzekuton asgjë; jep një
deklaratë, dhe e njëjta listë e lejuar (SELECT 1 / SHOW CATALOGS) vendos nëse ajo
preket fare. Kështu modeli i dytë shton aftësi pa shtuar pushtet.

Ndezja: HALIM_SQL_MODEL=meta. Pa flamurin kthen None dhe sjellja mbetet si më parë.
"""
from __future__ import annotations

import json
import os
import pathlib
import time
import urllib.request

LEJUAR_KUFI = ("select 1", "show catalogs")
BT = chr(96) * 3


def aktiv() -> bool:
    return os.environ.get("HALIM_SQL_MODEL", "").strip().lower() == "meta"


def _celes() -> str:
    k = os.environ.get("META_API_KEY", "").strip()
    if k:
        return k
    p = pathlib.Path.home() / ".securevault/secrets/meta-api.key"
    return p.read_text().strip() if p.exists() else ""


def lejohet(sql: str):
    n = " ".join((sql or "").lower().split())
    if not n:
        return False, "SQL bosh"
    if not any(n.startswith(x) for x in LEJUAR_KUFI):
        return False, "vetem SELECT 1 dhe SHOW CATALOGS lejohen ne demo"
    return True, ""


def pastro(txt: str) -> str:
    """Nxjerr deklaratën SQL, edhe kur modeli e mbyll në bllok markdown."""
    t = (txt or "").strip()
    rreshta = []
    for pjese in (t.split(BT) if BT in t else [t]):
        rreshta.extend(pjese.splitlines())
    for line in rreshta:
        s = line.strip().rstrip(";")
        if s.lower().startswith(("select", "show", "with")):
            return s
    for line in rreshta:
        if line.strip():
            return line.strip()
    return ""


def propozo(kerkesa: str):
    """None kur flamuri s'eshte ndezur — sjellja e vjeter, pa rrjet."""
    if not aktiv():
        return None
    key = _celes()
    if not key:
        return {"ok": False, "sql": "", "arsye": "pa celes META_API_KEY", "model": ""}
    base = os.environ.get("META_BASE_URL", "https://api.meta.ai/v1")
    model = os.environ.get("META_SQL_MODEL", "muse-spark-1.3")
    prompt = (
        "Kthe VETEM nje deklarate SQL, pa shpjegim dhe pa markdown. "
        "Skema: AVOKATIM.ocds_awards(id, buyer, supplier, value, date), "
        "AVOKATIM.s2_decisions(id, case, outcome, date). "
        "Pyetja: " + (kerkesa or "").strip()[:400]
    )
    body = json.dumps({"model": model,
                       "messages": [{"role": "user", "content": prompt}],
                       "temperature": 0, "max_tokens": 400,
                       "reasoning_effort": "minimal"}).encode()
    req = urllib.request.Request(base.rstrip("/") + "/chat/completions", data=body,
                                 headers={"Content-Type": "application/json",
                                          "Authorization": "Bearer " + key})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            d = json.load(r)
    except Exception as exc:
        return {"ok": False, "sql": "", "arsye": type(exc).__name__, "model": model}
    msg = (d.get("choices") or [{}])[0].get("message") or {}
    sql = pastro(msg.get("content") or "")
    return {"ok": bool(sql), "sql": sql, "model": model,
            "ms": int((time.time() - t0) * 1000),
            "arsye": "" if sql else "pa permbajtje"}
