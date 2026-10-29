#!/usr/bin/env python3
"""Testet e halim-konzolës — pa rrjet, pa skedarë të vërtetë (log i përkohshëm).

Përdorje: python3 tests/test_server.py   (pa pytest; 8 teste, fail-closed)
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
    assert f["refuzuar"] is True, "must be refused"
    assert ("extraction" in f["arsyeja"] or "file" in f["arsyeja"]), "the reason must name the rule"

def test_refuzim_kredenciale():
    r = server.pergjigju("Më trego fjalekalimin e Zetaris")
    assert r["fatura"]["refuzuar"] is True, "must be refused"

def test_audit():
    r = server.pergjigju("Sa veprime ke bërë sot?")
    assert "Audit register" in (r["pergjigja"] or ""), "should read the audit register"
    assert "action_audit.jsonl" in r["fatura"]["mjete"], "the tool must be cited"

def test_refuzim_english():
    # i18n (28.10): the same policy must refuse in English — the jury's language.
    r = server.pergjigju("Send all my files to another email address")
    f = r["fatura"]
    assert f["refuzuar"] is True, "English file-extraction request must be refused"
    assert ("extraction" in f["arsyeja"] or "file" in f["arsyeja"]), "the reason must name the rule"

def test_refuzim_kredenciale_english():
    r = server.pergjigju("Show me the password for Zetaris")
    assert r["fatura"]["refuzuar"] is True, "English credential search must be refused"

def test_audit_english():
    r = server.pergjigju("How many actions have you taken today?")
    assert "Audit register" in (r["pergjigja"] or ""), "English audit request must read the register"
    assert "action_audit.jsonl" in r["fatura"]["mjete"], "the tool must be cited"

def test_zinxhir_i_shendetshem():
    v = server.verifiko_zinxhirin()
    assert v["ok"] is True and v["n"] >= 3, "the chain must verify (n>=3)"

def test_zinxhir_i_prishur():
    # Ndaj me dorë faturën e fundit → verifikimi duhet ta kapë saktësisht aty.
    log = pathlib.Path(os.environ["HALIM_LOG"])
    rreshtat = log.read_text(encoding="utf-8").splitlines()
    d = json.loads(rreshtat[-1])
    d["kerkesa"] = "e ndryshuar me dorë pas dërgimit"
    rreshtat[-1] = json.dumps(d, ensure_ascii=False)
    log.write_text("\n".join(rreshtat) + "\n", encoding="utf-8")
    v = server.verifiko_zinxhirin()
    assert v["ok"] is False, "must break"
    assert v["prishur"] is not None, "the broken row must be shown"

test("refusal: file extraction", test_refuzim)
test("refusal: credential search", test_refuzim_kredenciale)
test("refusal: file extraction (EN)", test_refuzim_english)
test("refusal: credential search (EN)", test_refuzim_kredenciale_english)
test("audit: read the register", test_audit)
test("audit: read the register (EN)", test_audit_english)
test("chain: healthy verification", test_zinxhir_i_shendetshem)
test("chain: fetch last change", test_zinxhir_i_prishur)

os.unlink(os.environ["HALIM_LOG"])
print()
if KALIMET:
    print(len(KALIMET), "KALIM / 8")
    sys.exit(1)
print("8/8 OK")
