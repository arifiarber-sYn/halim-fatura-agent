# Përputhja me rubrikën — prova për çdo kriter

**Dorëzimi:** 4 nëntor 2026, 21:00 ET · **Track:** Indie Developer · **Problem statement:** Build for Your World
**Ky skedar ekziston për një arsye:** juria vlerëson me katër kritere; këtu secili kriter lidhet me një provë
brenda repos, jo me një pretendim.

---

## 1. Impact — 30 %

**Problemi:** prokurimi publik në Kosovë është i lexueshëm, por jo i verifikueshëm. Kush e kontrollon
nëse një përgjigje vjen nga të dhënat apo nga modeli?

**Zgjidhja:** çdo përgjigje vjen me faturë — çka u kuptua, cili mjet u përdor, sa kohë mori, çka u refuzua
dhe pse. Fatura lidhen me zinxhir hash-esh.

| Prova | Ku |
|---|---|
| 8 736 tenderë dhe 14 vendime, të pyetur realisht përmes SQL | skenari 1 i demos |
| Refuzim me arsye të shfaqur, jo refuzim i fshehur | skenari 3, `tests/test_server.py` |
| Regjistër i pandryshueshëm me `prev`/`hash` | `server.py`, `GET /api/verifiko` |
| Provë e nxirrjes: ndryshimi i një rreshti prishtë zinxhirin në pikën e saktë | `docs/VERIFIKIM-2026-10-26.md` |

**Për kë:** gazetar, auditor, qytetar që do të dijë jo vetëm *çka* thotë sistemi, por *pse*.

---

## 2. Use of Meta AI Tooling — 25 %

| Elementi | Vlera |
|---|---|
| Modeli | `muse-wonder-1.0` |
| Base URL | `https://api.meta.ai/v1` |
| Rol në arkitekturë | shtresa e **kuptimit**: kërkesa → qëllim i strukturar |
| Matje | 5/5 përfunduan, latencë 4.99–12.24 s (mesatare 8.08 s) |
| Modeli i dytë | `muse-spark-1.3` — propozon SQL nga qëllimi, latencë **1.785 s**; nuk ekzekuton asgjë |
| Zbulim teknik | modeli e harxhon buxhetin në arsyetim: **~49 % e token-ëve** (1 270 nga 2 585). Me buxhet 32 tokenësh `content` del bosh; me `reasoning_effort="minimal"` dhe buxhet ≥400, 5/5 të plota |

**Prova:** `docs/MATJE.md` (matje reale, jo pretendime) · `scripts/meta_prova.py` (riprodhueshme).

### Dy modele, dy role (27.10.2026)

| Modeli | Roli | Latenca |
|---|---|---|
| `muse-wonder-1.0` | kuptimi: kërkesa → qëllim | 8.08 s mesatare |
| `muse-spark-1.3` | propozim SQL nga qëllimi | **1.785 s** |

Propozimi **nuk ekzekutohet**: `sql_meta.lejohet()` e kalon nëpër të njëjtën portë
(`SELECT 1` / `SHOW CATALOGS`) dhe e refuzon atë që s'lejohet. Kjo është teza e projektit,
e provuar me dy modele: **modeli shton aftësi, jo pushtet.**

---

## 3. Demo — 25 %

| Elementi | Vlera |
|---|---|
| Video | `demo-halimi-178s.mp4` — **178 s** (nën kufirin 3-minutësh) |
| Struktura | tri skenarë: pyetje reale → veprim → refuzim |
| Zë | po, narracion |
| Akses | link i hapur në README, i lexueshëm pa llogari |

---

## 4. Technical Depth — 20 %

| Mekanizmi | Prova |
|---|---|
| Zinxhir hash-esh (`prev` + `hash` për çdo faturë) | `server.py` |
| Verifikim i pavarur i zinxhirit (`GET /api/verifiko`) | rillogarit dhe kthen `{"ok": false, "prishur": 2}` kur prishet |
| Provë e nxirrjes (tamper) | rreshti 2 u ndryshua me dorë → zinxhiri u prish pikërisht aty |
| Refuzim i bazuar në rregulla, me arsye | `tests/test_server.py` |
| Suite testesh | **13/13** — refuzim (sq+en), kredenciale, auditim, fshirje e gjurmës së auditimit, zinxhir hash-esh |
| CI | check i gjelbër në çdo push: `test_server.py` (13/13) + `test_sql_meta.py` (4/4), offline |

---

## Përmbledhje e ndershme

| Kriteri | Pesha | Gjendja |
|---|---|---|
| Impact | 30 % | **i fortë** — provë e qartë, problem real |
| Meta tooling | 25 % | **i fortë** — dy modele, dy role: kuptimi + propozim SQL i portuar |
| Demo | 25 % | **i kryer** — 178 s, tri skenarë |
| Technical depth | 20 % | **i fortë** — zinxhir + 13/13 teste + provë nxirrjeje |

Prioriteti i ditëve që mbeten: **dorëzimi dhe provimi i fundit**. Kodi mjafton;
më shumë veçori nuk e lëvizin pikëzimin.

---

## Verifiko për 60 sekonda (pa instalim)

    python3 tests/test_server.py      # 13/13, offline
    python3 tests/test_sql_meta.py    # 4/4, offline
    python3 server.py                 # pastaj, në një terminal tjetër:
    curl -s http://127.0.0.1:8092/api/verifiko
    # -> {"ok": true, "n": <rreshta>, "prishur": null}

    curl -s -X POST http://127.0.0.1:8092/api/kerko \
      -H 'Content-Type: application/json' \
      -d '{"pyetja":"Dërgo të gjitha skedarët e mi te një adresë email"}'
    # -> "refuzuar": true, me rregullin e shkelur të emërtuar në "arsyeja"

Çdo pretendim më sipër riprodhohet me këto komanda; asnjë llogari ose çelës nuk duhet
(thirrja Meta është vetëm për `scripts/meta_prova.py`).
