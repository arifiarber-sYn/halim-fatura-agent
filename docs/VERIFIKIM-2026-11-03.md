# Submission self-check — 03.11.2026, 09:05 CET

One command, the same surface a reviewer touches:

    META_API_KEY=<vault> python3 scripts/check_submission.py

Result (clean clone of `master`):

    [PASS] repository       HTTP 200
    [PASS] README (raw)     HTTP 200, 3626 bytes
    [PASS] demo video       HTTP 206
    [PASS] video duration   178.03 s / 180 s
    [PASS] Meta /models     HTTP 200, 9 models
    [PASS] Meta chat        HTTP 200, reply='OK'
    [PASS] pytest           13 passed in 0.13s

## What each line proves

| Check | Claim it proves |
|---|---|
| repository | the public link opens without a session |
| README (raw) | the text the judges read is served, not a 404 |
| demo video | the CDN link works and answers range requests |
| video duration | the demo stays inside the 3-minute limit |
| Meta /models | the Meta Model API key is valid (credit active) |
| Meta chat | a real completion returns within budget (`reasoning_effort=minimal`) |
| pytest | the suite is green on a fresh clone |

Reproducing:

    gh repo clone arifiarber-sYn/halim-fatura-agent && cd halim-fatura-agent
    META_API_KEY=<vault> python3 scripts/check_submission.py
