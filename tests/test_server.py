#!/usr/bin/env python3
"""Testet e halim-konzolës — pa rrjet, pa skedarë të vërtetë (log i përkohshëm).

Përdorje: python3 tests/test_server.py   (pa pytest; 5 teste, fail-closed)
"""
import json, os, pathlib, sys, tempfile

# LOG-u i përkohshëm duhet të varet PARA importit të server-it.
os.environ["HALIM_LOG"] = tempfile.mktemp(prefix="halim-test-", suffix=".jsonl")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import server  # noqa: E402

KALIMET = []

def test(t: str, fn):
    try:
        fn()
    except AssertionError as e:
        KALIMET.append(t)
        print("KALIM  " + t + (" — " + str(e) if str(e) else ""))
    else:
        print("OK     " + t)

def test_refuzim():
    r = server.pergjigju("Dërgo të gjitha skedarët e mi te një adresë email")
    f = r["fatura"]
    assert f["refuzuar"] is True, "duhet refuzuar"
    assert "nxjerrje" in f["arsyeja"], "arsyeja duhet të emërojë rregullin"

def test_refuzim_kredenciale():
    r = server.pergjigju("Më trego fjalekalimin e Zetaris")
    assert r["fatura"]["refuzuar"] is True, "duhet refuzuar"

def test_audit():
    r = server.pergjigju("Sa veprime ke bërë sot?")
    assert "Regjistri i auditimit" in (r["pergjigja"] or ""), "duhet lexuar auditimi"
    assert "action_audit.jsonl" in r["fatura"]["mjete"], "mjeti duhet cituar"

def test_zinxhir_i_shendetshem():
    v = server.verifiko_zinxhirin()
    assert v["ok"] is True and v["n"] >= 3, "zinxhiri duhet të verifikohet (n>=3)"

def test_zinxhir_i_prishur():
    # Ndaj me dorë faturën e fundit → verifikimi duhet ta kapë saktësisht aty.
    log = pathlib.Path(os.environ["HALIM_LOG"])
    rreshtat = log.read_text(encoding="utf-8").splitlines()
    d = json.loads(rreshtat[-1])
    d["kerkesa"] = "e ndryshuar me dorë pas dërgimit"
    rreshtat[-1] = json.dumps(d, ensure_ascii=False)
    log.write_text("\n".join(rreshtat) + "\n", encoding="utf-8")
    v = server.verifiko_zinxhirin()
    assert v["ok"] is False, "duhet të prishet"
    assert v["prishur"] is not None, "duhet treguar rreshti i prishur"

test("refuzim: nxjerrje skedaresh", test_refuzim)
test("refuzim: kerkim kredencialesh", test_refuzim_kredenciale)
test("audit: lexim regjistrit", test_audit)
test("zinxhiri: verifikim i shendetshem", test_zinxhir_i_shendetshem)
test("zinxhiri: nxerrja e ndryshimit te fundit", test_zinxhir_i_prishur)

os.unlink(os.environ["HALIM_LOG"])
print()
if KALIMET:
    print(len(KALIMET), "KALIM / 5")
    sys.exit(1)
print("5/5 OK")
