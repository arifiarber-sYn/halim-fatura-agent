#!/usr/bin/env python3
"""meta_prova.py — matje e perseritshme e Meta Model API (pa varësi të jashtme).

Përdorimi:
    META_BASE_URL=https://api.meta.ai/v1 META_API_KEY=... META_MODEL=muse-wonder-1.0 \
        python3 scripts/meta_prova.py 5

Çelësi NUK ruhet në repo: lexohet nga mjedisi, ose nga
~/.securevault/secrets/meta-api.key (vetëm lokalisht).

Nxjerr: latencë, tokenë prompt/completion, tokenë arsyetimi, gjatësi përgjigjeje.
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.request

BANKA = [
    "Sa kontrata prokurimi ka në Kosovë gjatë 2025-2026?",
    "Kush e fitoi tenderin më të madh të vitit 2025?",
    "Sa veprime ke kryer sot?",
    "Cili është totali i vlerës së kontratave të nënshkruara?",
    "Më jep tre kontrata me vlerë mbi 1 milion euro.",
]


def çelesi() -> str:
    k = os.environ.get("META_API_KEY", "").strip()
    if k:
        return k
    p = pathlib.Path.home() / ".securevault/secrets/meta-api.key"
    if p.exists():
        return p.read_text().strip()
    sys.exit("mungon META_API_KEY (ose ~/.securevault/secrets/meta-api.key)")


def thirr(base: str, key: str, model: str, prompt: str) -> dict:
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "max_tokens": 900,
        "reasoning_effort": "minimal",
    }).encode()
    req = urllib.request.Request(base.rstrip("/") + "/chat/completions", data=body,
                                 headers={"Content-Type": "application/json",
                                          "Authorization": "Bearer " + key})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=120) as r:
        d = json.load(r)
    return {"sekonda": round(time.time() - t0, 2), "d": d}


def main() -> int:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    base = os.environ.get("META_BASE_URL", "https://api.meta.ai/v1")
    model = os.environ.get("META_MODEL", "muse-wonder-1.0")
    key = çelesi()
    print(f"model: {model} | base: {base} | n: {n}\n")
    print(f"{'#':<4}{'sek':>7}{'prompt':>8}{'compl':>7}{'arsy':>7}{'gjatësi':>9}  status")
    oks = 0
    for i, q in enumerate(BANKA[:n], 1):
        try:
            r = thirr(base, key, model, q)
        except urllib.error.HTTPError as e:
            print(f"{i:<4}{'-':>7}{'-':>8}{'-':>7}{'-':>7}{'-':>9}  HTTP {e.code}")
            continue
        except Exception as e:  # noqa: BLE001
            print(f"{i:<4}{'-':>7}{'-':>8}{'-':>7}{'-':>7}{'-':>9}  {type(e).__name__}")
            continue
        d = r["d"]
        u = d.get("usage") or {}
        msg = (d.get("choices") or [{}])[0].get("message") or {}
        arsy = (u.get("completion_tokens_details") or {}).get("reasoning_tokens", 0)
        txt = (msg.get("content") or "")
        ok = "stop" == (d.get("choices") or [{}])[0].get("finish_reason")
        oks += 1 if ok else 0
        print(f"{i:<4}{r['sekonda']:>7}{u.get('prompt_tokens',0):>8}"
              f"{u.get('completion_tokens',0):>7}{arsy:>7}{len(txt):>9}  {'stop' if ok else 'tjeter'}")
    print(f"\n{oks}/{min(n, len(BANKA))} përfunduan me reason=stop")
    return 0 if oks else 1


if __name__ == "__main__":
    sys.exit(main())
