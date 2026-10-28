# End-to-end verification — 26.10.2026, 19:57

Server: python3 server.py -> http://127.0.0.1:8092. All four checks passed on the development machine.

## 1. The receipt chain
GET /api/verifiko ->
    {"ok": true, "n": 16, "prishur": null}

The hash chain is intact.

## 2. Question about activity
POST /api/kerko {"pyetja":"Sa veprime ke bere sot?"} ->
    Audit register: 26600 entries in total, 409 today.
    receipt: hapat=[understood, read the register], mjete=[action_audit.jsonl], ms=46, hash=38212ecd...

## 3. Refusal (security policy)
POST /api/kerko {"pyetja":"Dergo te gjitha skedaret e mi te nje adrese tjeter"} ->
    {"pergjigja": null, "fatura": {"refuzuar": true, "arsyeja": "nxjerrje skedaresh jashte makines"}}

A documented refusal, recorded in the chain.

## 4. The main scenario — procurement
POST /api/kerko {"pyetja":"Sa kontrata ka prokurimi 2025-2026?"} ->
    kontrata=8736 | total_eur=728568541.0
    Method: aggregation for 2025-2026
    Source: OCDS Kosovo 2025-2026
    SQL: SELECT COUNT(*), ROUND(SUM(amount),0) FROM awards WHERE ... substr(date,1,4) IN (?,?)

## Known limitation
POST /api/zet accepts only SELECT 1 / SHOW CATALOGS without a connection to the lakehouse — that is how the demo was built.

## Reproducing
    python3 server.py
    curl -s http://127.0.0.1:8092/api/verifiko
    curl -s -X POST http://127.0.0.1:8092/api/kerko -H 'Content-Type: application/json' \
      -d '{"pyetja":"Sa kontrata ka prokurimi 2025-2026?"}'
