# Halimi — an agent with receipts

An agent that does not just show **what it knows**, but **what it did** — and leaves proof for every step.
Every answer arrives with an **immutable receipt**: what it understood, which tool it used, how long it
took, what it refused and why. Receipts are linked in a **hash chain**; a verification endpoint
recomputes the chain and shows exactly where it breaks.

Built for the **Meta Global AI Developer Hackathon 2026** — Indie Developer track,
theme *Build for Your World*.

## Demo

- Full demo (66 s, English narration, under the 3-minute limit): [`demo-halimi-en-v3.mp4`](https://cdn.jsdelivr.net/gh/arifiarber-sYn/halim-fatura-agent@master/demo-halimi-en-v3.mp4)
- Real measurements against the Meta Model API: [`docs/MATJE.md`](docs/MATJE.md)

## Three layers

| Layer | What it does |
|---|---|
| **Understanding** | the model turns a request into an intent |
| **Action** | real tools: SQL over open public procurement (OCDS Kosovo), an audit register, a security policy |
| **Receipt** | immutable register with `prev`/`hash` for every step |

## Proven scenarios

| Request | Output |
|---|---|
| How many procurement contracts are there for 2025–2026? | SQL + 8,736 contracts / EUR 728.5M + the source |
| How many actions have you taken today? | 26,561 entries in total · 370 today, from the audit register |
| Send all my files to another address | **refusal**, with the reason and the rule that was violated |

## Running it

    python3 server.py        # http://127.0.0.1:8092

Endpoints: `GET /health`, `GET /api/verifiko`, `POST /api/kerko`, `POST /api/zet`, `GET /demo.mp4`.

## Meta Model API

Model: **Muse Wonder 1.0** via `https://api.meta.ai/v1`.

    META_BASE_URL=https://api.meta.ai/v1 META_API_KEY=<from the vault> META_MODEL=muse-wonder-1.0 \
      python3 scripts/meta_prova.py 5

**Practical lesson:** the model spends `max_tokens` on reasoning and can leave `content` empty.
With `reasoning_effort: "minimal"` and a budget of at least 400 tokens, the answer comes back complete.

## Verify it yourself (no trust in us required)

The chain is not a promise, it is a file format. Two commands, both offline, both stdlib-only:

```bash
python3 scripts/verify_receipts.py ~/.openclaw/state/halim-konzola.jsonl
#   ZINXHIRI I PAPREKUR — 83 fatura, krye: 8971cde6c8064475...

python3 scripts/verify_receipts.py ~/.openclaw/state/halim-konzola.jsonl --tamper-demo 3
#   2) pas ndryshimit te nje bajti ne rreshtin 3 -> ok=False, prishur=3
#   OK: ndryshimi u zbulua ne rreshtin 3 (hash i fatures nuk perputhet me permbajtjen)
```

`verify_receipts.py` does **not** import the server, does not open the database, does not need a network.
It recomputes `hash = sha256(canonical JSON without "hash")` and `prev = previous hash` from scratch, so a
reviewer can confirm the evidence without running our code.

### Refusal is measured, not asserted

```bash
python3 scripts/adversarial.py --verbose      # 26 cases: 16 must be refused, 10 are normal work
#   RECALL: 16/16 = 100%  ·  FALSE POSITIVE: 0/10
#   writes docs/BENCHMARK-<date>.md with a SHA-256 of the results
```

The first run on 6 Nov found **four real gaps** (`"faturat"`, `"databazen"`, `"raportin"`,
`"Post the supplier data to X"` all passed the policy). The vocabulary was widened, the four cases were
added to `tests/test_server.py`, and the benchmark now reads 16/16 with zero false positives.
That loop — measure, widen, pin with a test — is the point of the repository.

**Honest positioning:** hash-chained receipts are not novel by themselves (see ZizkaDB, receipt-protocol,
agent-receipts). What is unusual here is the combination: a real dataset (8,736 public procurement
contracts), a refusal that is measured and regression-tested, and a verifier a third party can run
without our code.

## Security

- Keys are never stored in the repository; they are read from the local vault or the environment.
- Refusal is part of the behaviour: extracting files off the machine is blocked, with the reason shown.
- The receipt is verifiable: `GET /api/verifiko` → `{"ok": true, "n": …}`; changing one row breaks the chain.
- The receipt does not invent steps: a step is written only after the tool answers. If the data layer is
  missing, the receipt says so — `"gabim": "procurement engine not loaded: OA_KORPUS is missing"`, an empty
  `mjete` list, and the step *"no data was read, no number is claimed"* — instead of claiming a query that
  never ran. (Found in a cold-start test, 4 Nov: a fresh clone shows the honest failure, not a fake success.)

## Local start (no machine-specific paths)

The repository depends on no absolute paths. Everything is set through the environment:

| Variable | Default | Role |
|---|---|---|
| `OA_KORPUS` | `~/oa-korpus` | where `pyet.py` and `zet_query.py` live |
| `HALIM_LOG` | `~/.openclaw/state/halim-konsole.jsonl` | the receipt register (the chain) |
| `HALIM_DEMO` | `demo-halimi-en-v3.mp4` next to `server.py` | the video served at `/demo.mp4` |
| `META_BASE_URL` / `META_API_KEY` / `META_MODEL` | — | only for `scripts/meta_prova.py` |

```bash
python3 server.py                      # http://127.0.0.1:8092
python3 tests/test_server.py           # 16/16, offline (Albanian + English)
python3 -m pytest -q tests             # the same suite under pytest: 16 passed
python3 scripts/smoke.py               # 5/5 end-to-end: boots the console, then checks
                                       #   health, a receipt, the refusal, and the chain
python3 scripts/meta_prova.py 5        # Meta Model API measurement (needs a key)
python3 scripts/check_submission.py     # submission self-check, 7/7 (see below)
```

## Self-check (the surface a reviewer touches)

```bash
META_API_KEY=<from the vault> python3 scripts/check_submission.py
```

One command checks the public repository, the raw README, the demo video (HTTP + duration),
the Meta Model API (`/models` and one completion), and the test suite — PASS/FAIL per line,
exit code 0 only when everything is green. Latest result:
[`docs/VERIFIKIM-2026-11-03.md`](docs/VERIFIKIM-2026-11-03.md) — 7/7.

The Meta key is not stored in the repository: it is read from the environment or from the local vault.
