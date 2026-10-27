#!/usr/bin/env python3
"""halim-konzola — agjenti me fatura (prototip per Meta hackathon)."""
import hashlib, json, os, pathlib, re, subprocess, sys, time
from http.server import BaseHTTPRequestHandler, HTTPServer

KORPUS = pathlib.Path(os.environ.get("OA_KORPUS", str(pathlib.Path.home() / "oa-korpus")))
sys.path.insert(0, str(KORPUS))
try:
    from pyet import pergjigju as prokurimi
except Exception:
    prokurimi = None

try:
    from sql_meta import propozo as propozo_sql, lejohet as sql_lejohet
except Exception:
    propozo_sql = None
    sql_lejohet = None

STATE = pathlib.Path.home() / ".openclaw" / "state"
LOG = pathlib.Path(os.environ.get("HALIM_LOG", str(STATE / "halim-konzola.jsonl")))
AUDIT = STATE / "action_audit.jsonl"
PORT = 8092

def _norm(s: str) -> str:
    import unicodedata
    t = unicodedata.normalize("NFD", s or "")
    return "".join(c for c in t if not unicodedata.combining(c)).lower()


def _e_ndaluar(kerkesa: str):
    """Kontroll me bashk-ndodhi, jo me rend fjalesh — gjuha reale eshte e çrregullt."""
    n = _norm(kerkesa)
    ka_skedar = any(w in n for w in ("skedar", "dokument", "file", "te dhena"))
    ka_dergim = any(w in n for w in ("derg", "derp", "posto", "co ", "adres", "email", "upload", "perco"))
    if ka_skedar and ka_dergim:
        return True, "nxjerrje skedaresh jashte makines"
    if any(w in n for w in ("fjalekalim", "password", "token", "celes", "api key", "api_key")):
        return True, "kerkim kredencialesh"
    if any(w in n for w in ("fshi", "delete", "rm -rf")) and any(w in n for w in ("log", "audit", "gjurm")):
        return True, "fshirje gjurmesh"
    return False, ""

FAQJA = """<!doctype html><html lang="sq"><head><meta charset="utf-8">
<title>Halimi — agjenti me fatura</title>
<style>body{font:16px system-ui;max-width:860px;margin:40px auto;padding:0 16px;background:#0f1115;color:#e8e8e8}
input{width:100%;padding:12px;font-size:16px;background:#171a21;color:#fff;border:1px solid #333;border-radius:6px}
button{padding:12px 20px;margin-top:8px;font-size:16px;background:#2d6cdf;color:#fff;border:0;border-radius:6px;cursor:pointer}
.karta{background:#171a21;border:1px solid #2a2f3a;border-radius:8px;padding:16px;margin-top:16px;white-space:pre-wrap}
.fatura{border-left:3px solid #2d6cdf}
.refuzim{border-left:3px solid #d9534f}
code{color:#9fd3ff}</style></head><body>
<h1>Halimi — agjenti me fatura</h1>
<p>Kërko diçka. Agjenti vepron dhe lë provë për çdo hap.</p>
<input id="q" value="Sa kontrata ka prokurimi 2025-2026?">
<button onclick="kerko()">Kërko</button> <button onclick="zet()">Zetaris live</button>
<div id="out"></div>
<script>
const NL=String.fromCharCode(10);
async function kerko(){
  const q=document.getElementById('q').value;
  const r=await fetch('api/kerko',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({pyetja:q})});
  const d=await r.json(); shfaq(d);
}
async function zet(){
  const r=await fetch('api/zet',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sql:'SELECT 1 AS one'})});
  const d=await r.json();
  const out=document.getElementById('out'); out.textContent='';
  const c=document.createElement('div'); c.className='karta';
  c.textContent='ZETARIS LIVE'+NL+'ok: '+d.ok+NL+'rreshta: '+JSON.stringify(d.rreshta)+NL+'ms: '+d.ms+NL+'via: '+d.via;
  out.appendChild(c);
}
function shfaq(d){
  const out=document.getElementById('out'); out.textContent='';
  if(d.pergjigja){const c=document.createElement('div');c.className='karta';c.textContent=d.pergjigja;out.appendChild(c);}
  const f=d.fatura||{};
  const c=document.createElement('div'); c.className='karta '+(f.refuzuar?'refuzim':'fatura');
  let t='FATURA'+NL;
  (f.hapat||[]).forEach(function(x,i){t+=(i+1)+'. '+x+NL;});
  t+='mjete: '+((f.mjete||[]).join(', ')||'-')+NL;
  t+='kohe: '+(f.ms||0)+' ms'+NL;
  t+='refuzuar: '+(f.refuzuar?('PO - '+f.arsyeja):'jo')+NL;
  t+='prove: '+(f.hash||'').slice(0,24)+'...';
  c.textContent=t; out.appendChild(c);
}
</script></body></html>"""


def _hash(d: dict) -> str:
    return hashlib.sha256(json.dumps(d, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def _lexo_audit() -> dict:
    sot = time.strftime("%Y-%m-%d")
    n = sot_n = 0
    if AUDIT.exists():
        for rresht in AUDIT.read_text(encoding="utf-8", errors="replace").splitlines():
            if not rresht.strip():
                continue
            n += 1
            if sot in rresht:
                sot_n += 1
    return {"total": n, "sot": sot_n}




ZET_LEJUAR = ("select 1", "show catalogs")


def zetaris(sql: str) -> dict:
    """Veprim i vetem i lejuar kundrejt Zetaris: prova e lidhjes live."""
    n = " ".join((sql or "").lower().split())
    if not any(n.startswith(x) for x in ZET_LEJUAR):
        return {"ok": False, "gabim": "vetem SELECT 1 dhe SHOW CATALOGS lejohen ne demo", "rreshta": []}
    t0 = time.time()
    try:
        r = subprocess.run(["python3", str(KORPUS / "zet_query.py"), sql],
                           capture_output=True, text=True, timeout=90)
        out = (r.stdout or "") + (r.stderr or "")
    except Exception as e:
        return {"ok": False, "gabim": str(e)[:120], "rreshta": []}
    rreshta = [x.strip() for x in out.splitlines() if x.strip().startswith("(")]
    ok = bool(rreshta)
    return {"ok": ok, "sql": sql, "rreshta": rreshta[:10], "ms": int((time.time() - t0) * 1000),
            "via": "zetaris-thrift", "gabim": "" if ok else out.strip()[-160:]}

def _fundi_i_zinxhirit() -> str:
    """Hash-i i fatures se fundit — lidhja e zinxhirit."""
    try:
        if LOG.exists():
            rreshtat = [r for r in LOG.read_text(encoding="utf-8").splitlines() if r.strip()]
            if rreshtat:
                return str(json.loads(rreshtat[-1]).get("hash") or "")
    except Exception:
        pass
    return "0" * 64


def verifiko_zinxhirin() -> dict:
    """Rillogarit zinxhirin; kthen ku prishet, nese prishet."""
    if not LOG.exists():
        return {"ok": True, "n": 0, "prishur": None}
    para = "0" * 64
    n = 0
    for i, rresht in enumerate(LOG.read_text(encoding="utf-8").splitlines(), 1):
        if not rresht.strip():
            continue
        try:
            d = json.loads(rresht)
        except Exception:
            return {"ok": False, "n": n, "prishur": i, "arsye": "json i pavlefshem"}
        if d.get("prev") != para:
            return {"ok": False, "n": n, "prishur": i, "arsye": "lidhja e zinxhirit nuk perputhet"}
        pa_hash = {k: v for k, v in d.items() if k != "hash"}
        if _hash(pa_hash) != d.get("hash"):
            return {"ok": False, "n": n, "prishur": i, "arsye": "hash i fatures nuk perputhet"}
        para = d["hash"]
        n += 1
    return {"ok": True, "n": n, "prishur": None}

def pergjigju(kerkesa: str) -> dict:
    t0 = time.time()
    n = kerkesa.lower()
    hapat, mjete = [], []
    pergjigja = None
    refuzuar, arsye = False, ""

    i_ndaluar, arsye_p = _e_ndaluar(kerkesa)
    if i_ndaluar:
        refuzuar, arsye = True, arsye_p
        hapat = ["kuptova kerkësen", "kontrollova politikën e sigurisë", "refuzova: " + arsye_p]
        mjete = ["politika"]

    if not refuzuar:
        if re.search(r"kontrat|prokurim|furnizues|award|ocds", n):
            hapat = ["kuptova: pyetje mbi prokurimin", "hapja bazën read-only", "ekzekutova SQL", "citova burimin OCDS"]
            mjete = ["sqlite", "pyet.py"]
            try:
                pergjigja = prokurimi(kerkesa) if prokurimi else "Motorri i prokurimit nuk u ngarkua."
            except Exception as e:
                pergjigja = "Gabim: " + str(e)[:120]
        elif re.search(r"veprim|audit|gjurm|log|sa ke bere", n):
            a = _lexo_audit()
            hapat = ["kuptova: pyetje mbi aktivitetin", "lexova regjistrin e auditimit"]
            mjete = ["action_audit.jsonl"]
            pergjigja = "Regjistri i auditimit: " + str(a["total"]) + " hyrje gjithsej, " + str(a["sot"]) + " sot."
        else:
            hapat = ["kuptova kerkësen", "nuk gjeta mjet të përshtatshëm"]
            mjete = []
            pergjigja = "Nuk e kuptova kërkesën. Provo: prokurim, auditim, ose një kërkesë që duhet refuzuar."

    ms = int((time.time() - t0) * 1000)
    fat = {"kerkesa": kerkesa[:300], "hapat": hapat, "mjete": mjete, "ms": ms,
           "refuzuar": refuzuar, "arsyeja": arsye, "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
    fat["prev"] = _fundi_i_zinxhirit()
    fat["hash"] = _hash(fat)
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(fat, ensure_ascii=False) + chr(10))
    except Exception:
        pass
    return {"pergjigja": pergjigja, "fatura": fat}


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _d(self, b, ct="application/json", k=200):
        self.send_response(k)
        self.send_header("Content-Type", ct)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            return self._d(FAQJA.encode(), "text/html; charset=utf-8")
        if self.path == "/demo.mp4":
            f = pathlib.Path(os.environ.get(
                "HALIM_DEMO",
                str(pathlib.Path(__file__).resolve().parent / "demo-halimi-178s.mp4")))
            if not f.exists():
                return self._d(b"pa video", "text/plain", 404)
            b = f.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "video/mp4")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)
            return
        if self.path == "/health":
            return self._d(json.dumps({"ok": True}).encode())
        if self.path == "/api/verifiko":
            return self._d(json.dumps(verifiko_zinxhirin(), ensure_ascii=False).encode())
        return self._d(json.dumps({"gabim": "not found"}).encode(), k=404)

    def do_POST(self):
        if self.path == "/api/zet":
            n = int(self.headers.get("Content-Length") or 0)
            try:
                d = json.loads(self.rfile.read(n).decode())
            except Exception:
                return self._d(json.dumps({"gabim": "json"}).encode(), k=400)
            return self._d(json.dumps(zetaris(d.get("sql") or ""), ensure_ascii=False).encode())
        if self.path == "/api/propozo":
            n = int(self.headers.get("Content-Length") or 0)
            try:
                d = json.loads(self.rfile.read(n).decode())
            except Exception:
                return self._d(json.dumps({"gabim": "json"}).encode(), k=400)
            kerkesa = (d.get("kerkesa") or "").strip()
            p = propozo_sql(kerkesa) if propozo_sql else None
            if p is None:
                return self._d(json.dumps({"propozoi": None,
                    "arsye": "HALIM_SQL_MODEL nuk eshte 'meta' — sjellja e vjeter"},
                    ensure_ascii=False).encode())
            ok, arsye = sql_lejohet(p.get("sql", "")) if sql_lejohet else (False, "porta mungon")
            p["lejuar"] = ok
            p["porta"] = arsye or "lejohet"
            return self._d(json.dumps(p, ensure_ascii=False).encode())
        if self.path != "/api/kerko":
            return self._d(json.dumps({"gabim": "not found"}).encode(), k=404)
        n = int(self.headers.get("Content-Length") or 0)
        try:
            d = json.loads(self.rfile.read(n).decode())
            q = (d.get("pyetja") or "").strip()
        except Exception:
            return self._d(json.dumps({"gabim": "json"}).encode(), k=400)
        if not q:
            return self._d(json.dumps({"gabim": "pyetja mungon"}).encode(), k=400)
        return self._d(json.dumps(pergjigju(q), ensure_ascii=False).encode())


if __name__ == "__main__":
    print("halim-konzola: http://127.0.0.1:" + str(PORT))
    HTTPServer(("127.0.0.1", PORT), H).serve_forever()
