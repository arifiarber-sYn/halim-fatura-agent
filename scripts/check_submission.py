#!/usr/bin/env python3
"""Submission self-check — the surface the judges actually touch.

Runs the same checks a reviewer would, without needing our machine:

  1. repository page        HTTP 200
  2. raw README.md          HTTP 200 and non-empty
  3. demo video             HTTP 200/206 and duration <= 180 s (ffprobe)
  4. Meta Model API         /v1/models 200 (+ one tiny chat when a key is available)
  5. test suite             pytest -q exits 0

Usage:
    python3 scripts/check_submission.py            # all checks
    python3 scripts/check_submission.py --skip-api # no key needed
    python3 scripts/check_submission.py --json

Exit code 0 only when every check passes.
"""
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request

REPO = "arifiarber-sYn/halim-fatura-agent"
VIDEO = "https://cdn.jsdelivr.net/gh/arifiarber-sYn/halim-fatura-agent@master/demo-halimi-en-v3.mp4"
MAX_SECONDS = 180.0
TIMEOUT = 30


def _get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "halim-submission-check"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return r.status, r.read(4096)
    except urllib.error.HTTPError as e:
        return e.code, b""
    except Exception as e:  # network down, DNS, TLS
        return None, str(e).encode()


def check_repo(results):
    status, body = _get(f"https://github.com/{REPO}")
    results.append(("repository", status == 200, f"HTTP {status}"))
    status, body = _get(f"https://raw.githubusercontent.com/{REPO}/master/README.md")
    ok = status == 200 and len(body) > 200
    results.append(("README (raw)", ok, f"HTTP {status}, {len(body)} bytes"))


def check_video(results):
    status, _ = _get(VIDEO, {"Range": "bytes=0-1023", "User-Agent": "halim-submission-check"})
    ok = status in (200, 206)
    results.append(("demo video", ok, f"HTTP {status}"))
    if ok and shutil.which("ffprobe"):
        try:
            out = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=nw=1:nk=1", VIDEO],
                capture_output=True, text=True, timeout=60)
            duration = float(out.stdout.strip())
            results.append(("video duration", duration <= MAX_SECONDS, f"{duration:.2f} s / {MAX_SECONDS:.0f} s"))
        except Exception as e:
            results.append(("video duration", False, f"ffprobe failed: {e}"))
    else:
        results.append(("video duration", not ok, "skipped (no ffprobe)"))


def check_api(results):
    key = os.environ.get("META_API_KEY", "")
    if not key:
        results.append(("Meta API", False, "META_API_KEY not set — skipped"))
        return
    base = os.environ.get("META_BASE_URL", "https://api.meta.ai/v1").rstrip("/")
    headers = {"Authorization": f"Bearer {key}", "User-Agent": "halim-submission-check"}
    status, body = _get(f"{base}/models", headers)
    models = []
    if status == 200:
        try:
            models = [m["id"] for m in json.loads(body).get("data", [])]
        except Exception:
            pass
    results.append(("Meta /models", status == 200, f"HTTP {status}, {len(models)} models"))

    payload = json.dumps({
        "model": os.environ.get("META_MODEL", "muse-wonder-1.0"),
        "messages": [{"role": "user", "content": "Reply with the single word OK."}],
        "max_tokens": 400,
        "reasoning_effort": "minimal",
    }).encode()
    req = urllib.request.Request(
        f"{base}/chat/completions", data=payload,
        headers={**headers, "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            status = r.status
            data = json.loads(r.read())
        content = (data["choices"][0]["message"].get("content") or "").strip()
        results.append(("Meta chat", status == 200 and bool(content), f"HTTP {status}, reply={content[:40]!r}"))
    except urllib.error.HTTPError as e:
        results.append(("Meta chat", False, f"HTTP {e.code}"))
    except Exception as e:
        results.append(("Meta chat", False, f"error: {e}"))


def check_tests(results):
    try:
        out = subprocess.run([sys.executable, "-m", "pytest", "-q"], capture_output=True, text=True, timeout=180)
        tail = (out.stdout.strip().splitlines() or [""])[-1]
        results.append(("pytest", out.returncode == 0, tail[:80]))
    except Exception as e:
        results.append(("pytest", False, f"error: {e}"))


def main():
    results = []
    check_repo(results)
    check_video(results)
    if "--skip-api" not in sys.argv:
        check_api(results)
    check_tests(results)

    if "--json" in sys.argv:
        print(json.dumps([{"check": c, "pass": ok, "detail": d} for c, ok, d in results], indent=2))
    else:
        for name, ok, detail in results:
            print(f"[{'PASS' if ok else 'FAIL'}] {name:<16} {detail}")
    failed = [c for c, ok, _ in results if not ok]
    if failed:
        print(f"\n{len(failed)} check(s) failed: {', '.join(failed)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
