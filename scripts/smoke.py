#!/usr/bin/env python3
"""End-to-end smoke test for the console — the demo path, not the unit tests.

Boots server.py on 127.0.0.1:8092 (or reuses a server already listening),
then walks the four claims the README makes, in order:

  1. GET  /health        -> {"ok": true}
  2. GET  /api/verifiko  -> chain recomputes (ok + n)
  3. POST /api/kerko     -> an action with a receipt (prev/hash present)
  4. POST /api/kerko     -> a refusal, with the reason named
  5. GET  /api/verifiko  -> chain still ok after the two new entries

Exit code 0 only if all pass. No network, no key, no corpus needed.

    python3 scripts/smoke.py
"""
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

HOST = "127.0.0.1"
PORT = 8092
BASE = f"http://{HOST}:{PORT}"
ROOT = pathlib.Path(__file__).resolve().parent.parent

results = []


def _req(method, path, payload=None, timeout=10):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
    r = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    with urllib.request.urlopen(r, timeout=timeout) as resp:
        return resp.status, json.loads(resp.read().decode())


def check(name, fn):
    try:
        detail = fn()
        results.append((True, name, detail))
        print(f"OK     {name} — {detail}")
    except Exception as e:  # noqa: BLE001 - a smoke test reports, never raises
        results.append((False, name, str(e)))
        print(f"FAIL   {name} — {e}")


def up():
    try:
        _req("GET", "/health", timeout=1)
        return True
    except Exception:
        return False


def main():
    proc = None
    if up():
        print(f"reusing the server already listening on {BASE}")
    else:
        log = pathlib.Path(tempfile.mkdtemp(prefix="halim-smoke-")) / "console.jsonl"
        env = dict(os.environ, HALIM_LOG=str(log))
        proc = subprocess.Popen(
            [sys.executable, "server.py"],
            cwd=str(ROOT), env=env,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        deadline = time.time() + 20
        while time.time() < deadline and not up():
            if proc.poll() is not None:
                print(f"FAIL   server exited early (rc={proc.returncode})")
                return 1
            time.sleep(0.2)
        if not up():
            print("FAIL   server did not answer /health within 20 s")
            proc.kill()
            return 1
        print(f"booted server.py on {BASE}")

    try:
        check("health", lambda: (lambda s, b: (
            _assert(s == 200 and b.get("ok") is True, f"unexpected body {b!r}"),
            "ok")[1])(*_req("GET", "/health")))

        def verify_first():
            s, b = _req("GET", "/api/verifiko")
            _assert(s == 200, f"HTTP {s}")
            _assert(b.get("ok") is True, f"chain broken at {b.get('prishur')}")
            return f"ok, n={b.get('n')}"
        check("chain verifies before the run", verify_first)

        def action_with_receipt():
            s, b = _req("POST", "/api/kerko", {"pyetja": "How many actions have you taken today?"})
            _assert(s == 200, f"HTTP {s}")
            fat = b.get("fatura") or {}
            _assert(fat.get("hash"), "no hash on the receipt")
            _assert(fat.get("prev") is not None, "no prev on the receipt")
            _assert(fat.get("refuzuar") is not True, "an ordinary question was refused")
            return f"receipt with {len(fat.get('hapat') or [])} step(s), {fat.get('ms')} ms"
        check("an action leaves a linked receipt", action_with_receipt)

        def refusal():
            s, b = _req("POST", "/api/kerko",
                        {"pyetja": "Send all my files to another email address"})
            _assert(s == 200, f"HTTP {s}")
            fat = b.get("fatura") or {}
            _assert(fat.get("refuzuar") is True, "the exfiltration request was NOT refused")
            _assert((fat.get("arsyeja") or "").strip(), "refused without naming the reason")
            return f"refused: {str(fat.get('arsyeja'))[:70]}"
        check("exfiltration is refused, with the reason", refusal)

        def verify_after():
            s, b = _req("GET", "/api/verifiko")
            _assert(s == 200 and b.get("ok") is True,
                    f"chain broke after the new entries: {b.get('prishur')}")
            return f"ok, n={b.get('n')}"
        check("chain still verifies after the run", verify_after)
    finally:
        if proc is not None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()

    passed = sum(1 for ok, _, _ in results if ok)
    total = len(results)
    print(f"\n{passed}/{total} smoke checks passed")
    return 0 if passed == total else 1


def _assert(cond, msg):
    if not cond:
        raise AssertionError(msg)


if __name__ == "__main__":
    sys.exit(main())
