#!/usr/bin/env python3
"""test_sql_meta.py — prova se modeli i dyte NUK shton pushtet.

4 prova: flamuri i fikur nuk ben rrjet; porta refuzon SQL te rrezikshem;
porta lejon SELECT 1; pastrimi i rrethimave markdown.
"""
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
os.environ.pop("HALIM_SQL_MODEL", None)
import sql_meta as s

OK = 0
FAIL = 0


def kontroll(nome, gjendja, arsye=""):
    global OK, FAIL
    if gjendja:
        OK += 1
        print("OK     " + nome)
    else:
        FAIL += 1
        print("FAIL   " + nome + (" — " + arsye if arsye else ""))


kontroll("flamuri i fikur -> None (pa rrjet)", s.propozo("sa kontrata ka") is None)
kontroll("DROP refuzohet nga porta", s.lejohet("DROP TABLE x")[0] is False)
kontroll("SELECT 1 lejohet", s.lejohet("SELECT 1 AS one")[0] is True)
kontroll("pastro nxjerr SQL nga rrethimi", s.pastro("provo\n" + s.BT + "sql\nSELECT 1 AS one;\n" + s.BT).lower().startswith("select 1"))

print()
if FAIL:
    print("DESHTIM: %d nga %d" % (FAIL, OK + FAIL))
    sys.exit(1)
print("TE GJITHA KALUAN (%d)" % OK)
