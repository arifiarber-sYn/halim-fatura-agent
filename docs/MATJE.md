# Real measurements — Meta Model API

**Date:** 26 October 2026 · **Model:** muse-wonder-1.0 · **Base:** https://api.meta.ai/v1
**Parameters:** temperature 0, max_tokens 900, reasoning_effort "minimal"
**Question source:** the test bank (META-BANKA-50), first 5 questions.

| ID | Latency | Prompt tok | Completion tok | Of which reasoning | Answer length |
|---|---|---|---|---|---|
| Q-01 | 9.88 s | 24 | 506 | 214 | 892 |
| Q-02 | 7.76 s | 26 | 491 | 242 | 760 |
| Q-03 | 4.99 s | 35 | 440 | 352 | 219 |
| Q-04 | 5.52 s | 21 | 380 | 246 | 386 |
| Q-05 | 12.24 s | 16 | 768 | 216 | 1584 |

## Summary

- **Latency:** min 4.99 s · mean 8.08 s · max 12.24 s (5/5 finished with finish_reason=stop).
- **Tokens:** 122 prompt · 2,585 completion · 1,270 of them reasoning (~49%).
- **Practical conclusion:** with reasoning_effort=minimal and a budget of at least 400 tokens the answer
  comes back complete; with a budget of 32 tokens the content stays empty.

## Reproducing

    META_BASE_URL=https://api.meta.ai/v1 META_API_KEY=*** the vault> META_MODEL=muse-wonder-1.0 \
      python3 scripts/meta_prova.py 5

The key is not stored in the repository: it is read from the local vault or the environment.

---

## Second model — muse-spark-1.3 (27.10.2026)

**Role:** proposes an SQL statement from the intent. **It executes nothing.**
**Flag:** HALIM_SQL_MODEL=meta. Without the flag, sql_meta.propozo() returns None
and the behaviour stays exactly as before — no network, no cost.

| Evidence | Result |
|---|---|
| Question | "How many procurement contracts are there for 2025-2026?" |
| Proposed SQL | SELECT COUNT(*) FROM AVOKATIM.ocds_awards WHERE date BETWEEN DATE '2025-01-01' AND ... |
| Latency | **1.785 s** |
| Model | muse-spark-1.3 |
| **The gate** | **refuses** — only SELECT 1 and SHOW CATALOGS are allowed in the demo |

This is the central proof of the thesis: the model produces a correct and useful statement,
but **it has no power to execute it**. sql_meta.lejohet() returns (False, ...) and the
receipt records the refusal with the reason.

**Measured difference between models:** muse-wonder-1.0 (understanding, free text) averages
8.08 s; muse-spark-1.3 (structured output) **1.79 s**. A narrower role, and faster.

Evidence: tests/test_sql_meta.py — 4/4 (flag off makes no network call; DROP is refused;
SELECT 1 is allowed; markdown stripping extracts the SQL).
