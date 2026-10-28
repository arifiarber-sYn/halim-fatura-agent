# Halimi — an agent with receipts

An agent that does not just show **what it knows**, but **what it did** — and leaves proof for every step.
Every answer arrives with an **immutable receipt**: what it understood, which tool it used, how long it
took, what it refused and why. Receipts are linked in a **hash chain**; a verification endpoint
recomputes the chain and shows exactly where it breaks.

Built for the **Meta Global AI Developer Hackathon 2026** — Indie Developer track,
theme *Build for Your World*.

## Demo

- 3-minute video: [`demo-halimi-178s.mp4`](https://cdn.jsdelivr.net/gh/arifiarber-sYn/halim-fatura-agent@master/demo-halimi-178s.mp4)
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

## Security

- Keys are never stored in the repository; they are read from the local vault or the environment.
- Refusal is part of the behaviour: extracting files off the machine is blocked, with the reason shown.
- The receipt is verifiable: `GET /api/verifiko` → `{"ok": true, "n": …}`; changing one row breaks the chain.

## Local start (no machine-specific paths)

The repository depends on no absolute paths. Everything is set through the environment:

| Variable | Default | Role |
|---|---|---|
| `OA_KORPUS` | `~/oa-korpus` | where `pyet.py` and `zet_query.py` live |
| `HALIM_LOG` | `~/.openclaw/state/halim-konsole.jsonl` | the receipt register (the chain) |
| `HALIM_DEMO` | `demo-halimi-178s.mp4` next to `server.py` | the video served at `/demo.mp4` |
| `META_BASE_URL` / `META_API_KEY` / `META_MODEL` | — | only for `scripts/meta_prova.py` |

```bash
python3 server.py                      # http://127.0.0.1:8092
python3 tests/test_server.py           # 5/5, offline
python3 scripts/meta_prova.py 5        # Meta Model API measurement (needs a key)
```

The Meta key is not stored in the repository: it is read from the environment or from the local vault.
