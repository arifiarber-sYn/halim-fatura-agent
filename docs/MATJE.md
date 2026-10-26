# Matje reale — Meta Model API

**Data:** 26 tetor 2026 · **Modeli:** muse-wonder-1.0 · **Base:** https://api.meta.ai/v1
**Parametrat:** temperature 0, max_tokens 900, reasoning_effort "minimal"
**Burimi i pyetjeve:** banka e testeve (META-BANKA-50), 5 pyetjet e para.

| ID | Latenca | Prompt tok | Completion tok | Ndera arsyetim | Gjatësia e përgjigjes |
|---|---|---|---|---|---|
| Q-01 | 9.88 s | 24 | 506 | 214 | 892 |
| Q-02 | 7.76 s | 26 | 491 | 242 | 760 |
| Q-03 | 4.99 s | 35 | 440 | 352 | 219 |
| Q-04 | 5.52 s | 21 | 380 | 246 | 386 |
| Q-05 | 12.24 s | 16 | 768 | 216 | 1584 |

## Përmbledhje

- **Latenca:** min 4.99 s · mesatare 8.08 s · max 12.24 s (5/5 përfunduan me finish_reason=stop).
- **Tokenë:** 122 prompt · 2,585 completion · 1,270 prej tyre arsyetim (~49%).
- **Përfundim praktik:** me reasoning_effort=minimal dhe buxhet ≥400 tokenësh, përgjigjja del e plotë; me buxhet 32 tokenësh content del bosh (e provuar: 32/32 në arsyetim).

## Përsëritja

    META_BASE_URL=https://api.meta.ai/v1 META_API_KEY=<nga thesari> META_MODEL=muse-wonder-1.0 \
      python3 scripts/meta_prova.py 5

Çelësi nuk ruhet në repo: lexohet nga thesari lokal ose nga mjedisi.