#!/usr/bin/env python3
"""Verifikues i PAVARUR i faturave (receipts).

Nuk importon serverin, nuk hap databazë, nuk kërkon rrjet. Merret vetëm me
skedarin .jsonl dhe e rindërton zinxhirin nga zero:

    hash_i = sha256(JSON kanonik i faturës PA fushën "hash")
    prev_i = hash_{i-1}   (për rreshtin e parë: 64 zero)

Kështu çdokush — juri, auditor, klient — mund ta kontrollojë provën pa na
besuar neve dhe pa ekzekutuar kodin tonë.

Përdorimi:
    python3 scripts/verify_receipts.py ~/.openclaw/state/halim-konzola.jsonl
    python3 scripts/verify_receipts.py audit.jsonl --json
    python3 scripts/verify_receipts.py audit.jsonl --tamper-demo 3

Kodet e daljes: 0 = zinxhiri i paprekur · 2 = i thyer (ose skedar i palexim).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import shutil
import sys
import tempfile

GENESIS = "0" * 64


def hash_i_fatures(d: dict) -> str:
    """E njëjta rregull si serveri: JSON me çelësa të renditur, UTF-8, pa 'hash'."""
    pa_hash = {k: v for k, v in d.items() if k != "hash"}
    return hashlib.sha256(
        json.dumps(pa_hash, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def verifiko(rruga: pathlib.Path) -> dict:
    if not rruga.exists():
        return {"ok": False, "n": 0, "prishur": None, "arsye": f"skedari nuk ekziston: {rruga}"}

    para = GENESIS
    n = 0
    for i, rresht in enumerate(rruga.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if not rresht.strip():
            continue
        try:
            d = json.loads(rresht)
        except Exception:
            return {"ok": False, "n": n, "prishur": i, "arsye": "json i pavlefshem"}
        if not isinstance(d, dict):
            return {"ok": False, "n": n, "prishur": i, "arsye": "rresht jo-objekt"}
        if d.get("prev") != para:
            return {"ok": False, "n": n, "prishur": i, "arsye": "lidhja 'prev' nuk perputhet me hash-in e meparshem"}
        if hash_i_fatures(d) != d.get("hash"):
            return {"ok": False, "n": n, "prishur": i, "arsye": "hash i fatures nuk perputhet me permbajtjen"}
        para = d["hash"]
        n += 1
    return {"ok": True, "n": n, "prishur": None, "krye": para}


def demo_ndryshimi(rruga: pathlib.Path, rreshti: int) -> int:
    """Kopjon skedarin, ndryshon NJË fushë në një rresht, dhe tregon zbulimin."""
    if not rruga.exists():
        print(f"nuk ka skedar: {rruga}")
        return 2
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="fatura-provë-")) / "ndryshuar.jsonl"
    shutil.copy2(rruga, tmp)
    rreshtat = tmp.read_text(encoding="utf-8").splitlines()
    indeks = None
    for i, r in enumerate(rreshtat, 1):
        if not r.strip():
            continue
        if i == rreshti or indeks is None:
            try:
                d = json.loads(r)
            except Exception:
                continue
            if i == rreshti or rreshti <= 0:
                indeks = i
                # ndryshim minimal: një karakter në arsyen e refuzimit ose në kohëzgjatje
                if "arsyeja" in d and isinstance(d["arsyeja"], str):
                    d["arsyeja"] = d["arsyeja"] + "."
                else:
                    d["ms"] = int(d.get("ms") or 0) + 1
                rreshtat[i - 1] = json.dumps(d, ensure_ascii=False)
                break
    if indeks is None:
        print("skedari s'ka rreshta për demonstrim")
        return 2
    tmp.write_text("\n".join(rreshtat) + "\n", encoding="utf-8")

    print(f"1) zinxhiri origjinal  -> {verifiko(rruga)}")
    rez = verifiko(tmp)
    print(f"2) pas ndryshimit te nje bajti ne rreshtin {indeks} -> {rez}")
    if rez["ok"]:
        print("DËSHTIM: ndryshimi nuk u zbulua")
        return 2
    print(f"OK: ndryshimi u zbulua ne rreshtin {rez['prishur']} ({rez['arsye']})")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Verifikues i pavarur i zinxhirit te faturave")
    ap.add_argument("skedar", type=pathlib.Path)
    ap.add_argument("--json", action="store_true", help="dalje JSON e plote")
    ap.add_argument("--tamper-demo", type=int, nargs="?", const=0, default=None,
                    metavar="RRESHTI", help="ndrysho nje rresht ne nje kopje dhe provo zbulimin")
    a = ap.parse_args()

    if a.tamper_demo is not None:
        return demo_ndryshimi(a.skedar, a.tamper_demo)

    rez = verifiko(a.skedar)
    if a.json:
        print(json.dumps(rez, ensure_ascii=False, indent=2))
    else:
        if rez["ok"]:
            print(f"ZINXHIRI I PAPREKUR — {rez['n']} fatura, krye: {rez['krye'][:24]}...")
        else:
            print(f"I THYER — {rez['n']} fatura te mira, rreshti {rez['prishur']}: {rez['arsye']}")
    return 0 if rez["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
