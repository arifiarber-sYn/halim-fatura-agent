# For 1.6 million people: justice in their own language — with a receipt

**Kosovo, 2026.** 1,585,566 residents (ASK, 2024 census). For 2025–2026 alone, public
procurement records 8,736 contracts worth EUR 728.5 million. Every citizen has the right to
ask where that money went. Almost none of them can check the answer.

Meanwhile, large language models now answer fluently in Albanian. Fluency is not accuracy.
In a small language, a confident wrong answer is not a minor inconvenience — it is
disinformation with a friendly voice, and there is no one to appeal to.

## What Halimi is

An agent that does not show **what it knows**, but **what it did** — and leaves proof for
every step. Three layers:

| Layer | What it does |
|---|---|
| **Understanding** | a Meta model turns the request into an intent |
| **Action** | real tools: SQL over open public procurement (OCDS Kosovo), the audit register, a security policy |
| **Receipt** | an immutable register with `prev`/`hash` for every step |

Every answer arrives with a receipt: what it understood, which tool it used, how long it
took, what it refused and why. Receipts are linked in a hash chain; a verification endpoint
recomputes the chain and shows exactly where it breaks.

The most important line in the demo is a refusal: *"Send all my files to another address"* —
refused, with the reason and the rule that was violated. An agent that cannot say *no* is
not trustworthy; it is merely eager.

## What is measured, not claimed

| Evidence | Value |
|---|---|
| Real query over open procurement data | 8,736 contracts / EUR 728.5M, with the source |
| muse-wonder-1.0 as the understanding layer | 5/5 completed, 4.99–12.24 s (mean 8.08 s) |
| muse-spark-1.3 proposes SQL, executes nothing | 1.785 s; the gate refuses anything but `SELECT 1` / `SHOW CATALOGS` |
| Reasoning cost measured | ~49% of completion tokens (1,270 of 2,585) |
| Test suite | 10/10 server tests, 4/4 SQL-gate tests, 5/5 end-to-end smoke |
| Demo | 178 seconds, under the 3-minute limit |

**The thesis, proven with two models:** the model adds capability, not power. It can propose
a correct SQL statement; it cannot execute it. The gate and the receipt stay ours.

## Why this world

I live here. Albanian is spoken by a few million people, and the legal and administrative
texts that govern their lives are long, dense, and rarely readable. A general chatbot can
summarise them; it cannot show you the page, the fragment, and the chain that proves the
answer was not invented.

A live product already runs on the same core (AvokatIM): Albanian legal questions, answers
with linked citations, and a daily audit chain. Halimi is the layer that makes the answer
**checkable by someone who does not trust the machine** — which is the correct default.

## What comes next

1. Open the receipt format so any agent can issue and verify one.
2. Extend the corpus to other small languages with the same discipline: source, page,
   fragment, refusal.
3. Publish the measurements continuously — including the ones that are inconvenient.

## A note on our own numbers

An earlier draft of the tagline said *"1.8 million Albanians"*. The 2024 census says
**1,585,566 residents of Kosovo**. We publish the correction, because a project that sells
receipts has to start with its own: the first claim to audit is the one in the pitch.
