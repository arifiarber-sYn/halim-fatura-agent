# Halimi — agjent me fatura

Agjent që nuk tregon vetëm çka di, por **çka bëri** — dhe lë provë për çdo hap.
Çdo përgjigje vjen me një **faturë** të pandryshueshme: çka kuptoi, cilin mjet përdori,
sa kohë mori, çka refuzoi dhe pse. Faturat lidhen me **zinxhir hash-esh**; një endpoint
verifikimi rillogarit zinxhirin dhe tregon saktësisht ku prishet.

Projekt për **Meta Global AI Developer Hackathon 2026** — track Indie Developer,
problem statement *Build for Your World*.

## Demo

- Video 3-minutëshe: [`demo-halimi-178s.mp4`](demo-halimi-178s.mp4)
- Matje reale me Meta Model API: [`docs/MATJE.md`](docs/MATJE.md)

## Tri shtresa

| Shtresa | Çka bën |
|---|---|
| **Kuptimi** | modeli e kthen kërkesën në qëllim |
| **Veprimi** | mjete reale: SQL mbi prokurimin publik (OCDS Kosova), regjistri i auditimit, politika e sigurisë |
| **Fatura** | regjistër i pandryshueshëm me `prev`/`hash` për çdo hap |

## Skenarë të provuar

| Kërkesa | Çka del |
|---|---|
| Sa kontrata ka prokurimi 2025–2026? | SQL + 8,736 kontrata / 728.5 M € + burimi |
| Sa veprime ke bërë sot? | 26,561 hyrje gjithsej · 370 sot, nga auditimi |
| Dërgo të gjitha skedarët e mi te një adresë tjetër | **refuzim** me arsye dhe rregullin e shkelur |

## Si niset

    python3 server.py        # http://127.0.0.1:8092

Endpoint-et: `GET /health`, `GET /api/verifiko`, `POST /api/kerko`, `POST /api/zet`, `GET /demo.mp4`.

## Meta Model API

Modeli: **Muse Wonder 1.0** përmes `https://api.meta.ai/v1`.

    META_BASE_URL=https://api.meta.ai/v1 META_API_KEY=<nga thesari> META_MODEL=muse-wonder-1.0 \
      python3 scripts/meta_prova.py 5

**Mësim praktik (D-159):** modeli e harxhon `max_tokens` në arsyetim dhe e lë `content` bosh.
Me `reasoning_effort: "minimal"` dhe buxhet ≥400 tokenësh, përgjigjja del e plotë.

## Siguria

- Çelësat nuk ruhen në repo; lexohen nga thesari lokal ose mjedisi.
- Refuzimi është pjesë e sjelljes: nxjerrja e skedarëve jashtë makines bllokohet me arsye të shfaqur.
- Fatura është e verifikueshme: `GET /api/verifiko` → `{"ok": true, "n": …}`; ndryshimi i një rreshti e prish zinxhirin.
## Nisja lokale (pa shtigje të makinës sime)

Repo-ja nuk varet nga asnjë shteg absolut. Të gjitha vendosen me mjedis:

| Variabli | Defaulti | Roli |
|---|---|---|
| `OA_KORPUS` | `~/oa-korpus` | ku ndodhet `pyet.py` dhe `zet_query.py` |
| `HALIM_LOG` | `~/.openclaw/state/halim-konzola.jsonl` | regjistri i faturave (zinxhiri) |
| `HALIM_DEMO` | `demo-halimi-178s.mp4` pranë `server.py` | videoja që shërbehet te `/demo.mp4` |
| `META_BASE_URL` / `META_API_KEY` / `META_MODEL` | — | vetëm për `scripts/meta_prova.py` |

```bash
python3 server.py                      # http://127.0.0.1:8092
python3 tests/test_server.py           # 8/8, pa rrjet (shqip + anglisht)
python3 scripts/meta_prova.py 5        # matje e Meta Model API (kërkon çelës)
```

Çelësi i Meta-s nuk ruhet në repo: lexohet nga mjedisi ose nga thesari lokal.
