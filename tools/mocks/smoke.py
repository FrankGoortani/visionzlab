#!/usr/bin/env python3
"""Click every demo through to its Outcome stage in a real browser and report any that get stuck or throw.

Needs the `agent-browser` CLI and a local server on the repo root, e.g.:
    python3 -m http.server 8765 &        (from the repo root)
    python3 tools/mocks/smoke.py [slug ...]            # approve everything
    python3 tools/mocks/smoke.py --reject [slug ...]   # send everything back and hold every approval
"""
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
BASE = "http://localhost:8765/demo/"

WALK = r"""(async()=>{const REJECT=__REJECT__;const w=ms=>new Promise(r=>setTimeout(r,ms)),q=s=>document.querySelector(s),seen=[];
for(let n=0;n<40;n++){
 const h=q('.stage-h h2')?.textContent||'?'; seen.push(h);
 if(q('#again')) return JSON.stringify({ok:true,stages:seen,outcome:q('.done-box h2')?.textContent,writes:[...document.querySelectorAll('#audit li, .audit li')].map(l=>l.textContent).filter(t=>/Wrote|Generated/.test(t)).length});
 if(q('#sample')&&!q('#sample').disabled) q('#sample').click();
 for(let k=0;k<15&&q('#yes');k++){if(REJECT){q('#no').click();q('#reasons button').click();}else{document.querySelectorAll('input.fx').forEach(i=>{if(!i.value){i.value='ok';i.dispatchEvent(new Event('input'))}});q('#yes').click();}await w(30);}
 document.querySelectorAll('.opts').forEach(o=>{if(!o.querySelector('.sel'))o.querySelector('button').click()});
 document.querySelectorAll('.checklist input').forEach(c=>{if(!c.checked)c.click()});
 if(REJECT&&q('#hold')) q('#hold').click(); else if(q('#ap')&&!q('#ap').disabled) q('#ap').click();
 if(q('#w')&&!q('#w').disabled) q('#w').click();
 const s=q('.sugg button:not(:disabled)'); if(s) s.click();
 for(let t=0;t<40;t++){await w(100);const nx=q('#next');if(nx&&!nx.disabled)break;}
 const nx=q('#next'); if(nx&&!nx.disabled) nx.click(); else return JSON.stringify({ok:false,stuck:h,hint:q('#hint')?.textContent,stages:seen});
 await w(50);
}
return JSON.stringify({ok:false,stuck:'loop',stages:seen})})()"""


def ab(*args):
    r = subprocess.run(["agent-browser", *args], capture_output=True, text=True, timeout=120)
    return r.stdout.strip()


REJECT = "--reject" in sys.argv


def main():
    slugs = [a for a in sys.argv[1:] if not a.startswith("--")] or sorted(p.parent.name for p in (ROOT / "demo").glob("*/index.html") if p.parent.name != "kit")
    bad = 0
    for s in slugs:
        ab("open", f"{BASE}{s}/?fast")
        out = ab("eval", WALK.replace("__REJECT__", "true" if REJECT else "false"))
        errs = ab("errors")
        try:
            res = json.loads(json.loads(out.splitlines()[-1]))
        except Exception:  # noqa: BLE001
            res = {"ok": False, "raw": out[-300:]}
        err_lines = [ln for ln in errs.splitlines() if ln.strip() and "No errors" not in ln and not ln.startswith("✓")]
        ok = res.get("ok") and not err_lines
        bad += not ok
        print(("PASS " if ok else "FAIL ") + s + (f"  [{res.get('outcome')}; writes/reports {res.get('writes')}]" if REJECT and ok else "") + ("" if ok else f"  {res}  {err_lines[:3]}"))
        if err_lines:
            ab("errors", "--clear")
    print(f"{len(slugs) - bad}/{len(slugs)} passed")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
