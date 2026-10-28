# Matching the rubric — evidence for each criterion

**Submission:** 4 November 2026, 21:00 ET · **Track:** Indie Developer · **Theme:** Build for Your World
**Why this file exists:** the jury scores against criteria; here each criterion is tied to evidence
inside the repository, not to a claim.

---

## 1. Impact — 30 %

**The problem:** public procurement in Kosovo is readable but not verifiable. Who checks
whether an answer comes from the data or from the model?

**The solution:** every answer carries a receipt — what was understood, which tool was used, how long
it took, what was refused and why. Receipts are linked in a hash chain.

| Evidence | Where |
|---|---|
| 8,736 tenders and 14 decisions, actually queried through SQL | demo scenario 1 |
| Refusal with the reason shown, not a hidden refusal | scenario 3, tests/test_server.py |
| Immutable register with prev/hash | server.py, GET /api/verifiko |
| Tamper proof: changing one row breaks the chain at that point | scenario 4 |

---

## 2. Use of Meta AI Tooling — 25 %

| Element | Value |
|---|---|
| Model | muse-wonder-1.0 |
| Base URL | https://api.meta.ai/v1 |
| Role in the architecture | the **understanding** layer: request -> structured intent |
| Measurement | 5/5 completed, latency 4.99-12.24 s (mean 8.08 s) |
| Second model | muse-spark-1.3 — proposes SQL from the intent, latency **1.785 s**; executes nothing |
| Technical finding | the model spends its budget on reasoning: **~49% of tokens** (1,270 of 2,585). With a budget of 32 tokens the content is empty |

**Evidence:** docs/MATJE.md (real measurement, not a claim) · scripts/meta_prova.py (reproducible).

### Two models, two roles (27.10.2026)

| Model | Role | Latency |
|---|---|---|
| muse-wonder-1.0 | understanding: request -> intent | 8.08 s mean |
| muse-spark-1.3 | SQL proposal from the intent | **1.785 s** |

The proposal **is not executed**: sql_meta.lejohet() sends it through the same gate
(SELECT 1 / SHOW CATALOGS) and refuses what is not allowed. This is the thesis of the project,
proven with two models: **the model adds capability, not power.**

---

## 3. Demo — 25 %

| Element | Value |
|---|---|
| Video | demo-halimi-178s.mp4 — **178 s** (under the 3-minute limit) |
| Structure | three scenarios: a real question -> action -> refusal |
| Audio | yes, narration |
| Access | open link in the README, readable without an account |

---

## 4. Technical Depth — 20 %

| Mechanism | Evidence |
|---|---|
| Hash chain (prev + hash for every receipt) | server.py |
| Independent verification of the chain (GET /api/verifiko) | recomputes and returns {"ok": false, "prishur": 2} when row 2 is altered |
| Tamper proof | row 2 was edited by hand -> the chain broke exactly there |
| Rule-based refusal, with the reason | tests/test_server.py |
| Test suite | **5/5** across refusal, audit and the chain |

---

## Honest summary

| Criterion | Weight | State |
|---|---|---|
| Impact | 30 % | **strong** — clear evidence, real problem |
| Meta tooling | 25 % | **weak** — one model, one role |
| Demo | 25 % | **done** — 178 s, three scenarios |
| Technical depth | 20 % | **strong** — chain + 5/5 tests + tamper proof |

Priority for the remaining days: **criterion 2**, not more code on criterion 4.
