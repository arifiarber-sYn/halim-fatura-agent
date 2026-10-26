# Verifikim end-to-end — 26.10.2026, 19:57

Serveri: `python3 server.py` → `http://127.0.0.1:8092`. Të katër provat kaluan në makinën e zhvillimit.

## 1. Zinxhiri i faturave
`GET /api/verifiko` →
```json
{"ok": true, "n": 16, "prishur": null}
```
Zinxhiri i hash-eve i paprishur.

## 2. Pyetje mbi aktivitetin
`POST /api/kerko {"pyetja":"Sa veprime ke bere sot?"}` →
```
Regjistri i auditimit: 26600 hyrje gjithsej, 409 sot.
fatura: hapat=[kuptova, lexova regjistrin], mjete=[action_audit.jsonl], ms=46, hash=38212ecd…
```

## 3. Refuzimi (politika e sigurisë)
`POST /api/kerko {"pyetja":"Dergo te gjitha skedaret e mi te nje adrese tjeter"}` →
```json
{"pergjigja": null, "fatura": {"refuzuar": true, "arsyeja": "nxjerrje skedaresh jashte makines"}}
```
Refuzim i dokumentuar, i shënuar në zinxhir.

## 4. Skenari kryesor — prokurimi
`POST /api/kerko {"pyetja":"Sa kontrata ka prokurimi 2025-2026?"}` →
```
kontrata=8736 | total_eur=728568541.0
Metoda: agregim per 2025-2026
Burimi: OCDS Kosovo 2025-2026
SQL: SELECT COUNT(*), ROUND(SUM(amount),0) FROM awards WHERE ... substr(date,1,4) IN (?,?)
```

## Kufizim i njohur
`POST /api/zet` pranon vetëm `SELECT 1` / `SHOW CATALOGS` pa lidhjen me lakehouse-in — kështu është ndërtuar demoja; pyetjet reale të prokurimit kalojnë përmes `/api/kerko` (si më sipër).

## Riprodhimi
```bash
python3 server.py
curl -s http://127.0.0.1:8092/api/verifiko
curl -s -X POST http://127.0.0.1:8092/api/kerko -H 'Content-Type: application/json' \
  -d '{"pyetja":"Sa kontrata ka prokurimi 2025-2026?"}'
```
