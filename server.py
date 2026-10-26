#!/usr/bin/env python3
"""halim-konzola — agjenti me fatura (prototip per Meta hackathon)."""
import hashlib, json, os, pathlib, re, sys, time
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.path.insert(0, "/home/kllosha/oa-korpus")
try:
    from pyet import pergjigju as prokurimi
except Exception:
    prokurimi = None

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
<button onclick="kerko()">Kërko</button>
<div id="out"></div>
<script>
async function kerko(){
  const q=document.getElementById("q").value;
  const r=await fetch("/api/kerko",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({pyetja:q})});
  const d=await r.json();
  let h="";
  if(d.pergjigja){h+="<div class=\"karta\">"+d.pergjigja.replace(/</g,"&lt;")+"</div>";}
  const f=d.fatura||{};
  h+="<div class=\"karta "+(f.refuzuar?"refuzim":"fatura")+"\"><b>FATURA</b>";
  h+="\n"+ (f.hapat||[]).map((x,i)=>"  "+(i+1)+". "+x).join("\n");
  h+="\n\nmjete: "+((f.mjete||[]).join(", ")||"-");
  h+="\nkohe: "+(f.ms||0)+" ms";
  h+="\nrefuzuar: "+(f.refuzuar?"PO — "+f.arsyeja:"jo");
  h+="\nprove: "+(f.hash||"").slice(0,24)+"...";
  h+="</div>";
  document.getElementById("out").innerHTML=h;
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
        if self.path == "/health":
            return self._d(json.dumps({"ok": True}).encode())
        if self.path == "/api/verifiko":
            return self._d(json.dumps(verifiko_zinxhirin(), ensure_ascii=False).encode())
        return self._d(json.dumps({"gabim": "not found"}).encode(), k=404)

    def do_POST(self):
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
