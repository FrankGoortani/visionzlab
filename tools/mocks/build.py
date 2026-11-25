#!/usr/bin/env python3
"""Build the white-label use-case demos into /demo/ (noindex, not in the sitemap, not linked from the site).

    python3 tools/mocks/build.py            # writes demo/kit/, demo/<slug>/index.html, demo/index.html
    python3 tools/mocks/build.py --check    # validate only
    python3 tools/mocks/build.py --check --only insurance,food   # validate some industry files

Cases live in tools/mocks/cases/<industry>.py (INDUSTRY dict + CASES list), written with tools/mocks/mk.py.
Standard library only. The build fails on a schema error or on anything that would break the demo rules
(see tools/mocks/README.md).
"""
import hashlib
import html
import importlib
import json
import pathlib
import pkgutil
import re
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OUT = ROOT / "demo"
sys.path.insert(0, str(HERE))

sys.dont_write_bytecode = True
import cases  # noqa: E402

PRODUCT = "Assistant"
ROBOTS = '<meta name="robots" content="noindex, nofollow, noarchive">'
HEAD = f"""<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
{ROBOTS}<meta name="referrer" content="no-referrer">"""
STAGE_NEEDS = {
    "upload": [], "process": [], "review": [], "exceptions": ["items"], "compare": ["table"], "draft": ["text"],
    "approve": ["question"], "write": ["system", "records"], "report": ["doc", "sections"], "ask": ["qa"],
    "feed": ["items"], "calendar": ["days"],
}
HUMAN_STAGES = {"review", "exceptions", "approve"}
DOC_KINDS = {"pdf", "scan", "email", "sheet", "web", "call", "docx", "note"}
TONES = {"ok", "check", "bad", "info"}
# Words that must never reach a public demo: our own name and claims we may not make. Names of people and
# companies we must never mention live in private_terms.txt (gitignored, one regex per line), because this repo
# is public; the build refuses to run without it.
PRIVATE = HERE / "private_terms.txt"
if not PRIVATE.exists():
    raise SystemExit(f"missing {PRIVATE.name}: copy it from the private workspace before building")
PRIVATE_TERMS = [ln.strip() for ln in PRIVATE.read_text().splitlines() if ln.strip() and not ln.startswith("#")]
BANNED = [r"visionz", *PRIVATE_TERMS,
          r"\b\d+\s*%\s*(faster|less|fewer|cheaper|saving|savings|reduction)\b", r"\bguarantee", r"\baccuracy of \d"]
BANNED_RE = re.compile("|".join(BANNED), re.I)
EXTERNAL_RE = re.compile(r"""(?:src|href)\s*=\s*["']?(?:https?:)?//""", re.I)
# Final guard over the written files: our name or a tracker.
LEAK_RE = re.compile("|".join([r"visionz", r"umami", r"googletagmanager", r"gtag\(", *PRIVATE_TERMS]), re.I)


def load(only=None):
    inds, all_cases = [], []
    for m in sorted(pkgutil.iter_modules(cases.__path__), key=lambda m: m.name):
        if only and m.name not in only:
            continue
        mod = importlib.import_module(f"cases.{m.name}")
        ind = dict(mod.INDUSTRY, id=m.name)
        inds.append(ind)
        for c in mod.CASES:
            all_cases.append(dict(c, industry=ind["name"], ind=ind["id"]))
    inds.sort(key=lambda i: (i.get("order", 50), i["name"]))
    return inds, all_cases


def validate(c, ind):
    where = c.get("slug", "?")
    err = []
    e = err.append
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", c.get("slug", "")):
        e("slug must be kebab-case")
    for k in ("title", "tagline"):
        if not c.get(k):
            e(f"missing {k}")
    if set(c["flow"]) != {"start", "agent", "person", "end"} or not all(c["flow"].values()):
        e("flow needs four non-empty parts")
    types = [s.get("type") for s in c["stages"]]
    for s in c["stages"]:
        t = s.get("type")
        if t not in STAGE_NEEDS:
            e(f"unknown stage type {t!r}")
            continue
        for k in STAGE_NEEDS[t]:
            if not s.get(k):
                e(f"{t} stage missing {k}")
        if t == "exceptions":
            for x in s["items"]:
                if len(x["options"]) < 2:
                    e(f"exception {x['title']!r} needs at least two options")
                if x.get("rec") is not None and not 0 <= x["rec"] < len(x["options"]):
                    e(f"exception {x['title']!r} rec out of range")
        if t == "compare":
            for r in s["table"]["r"]:
                if r[-1] not in TONES:
                    e(f"compare row must end with a status: {r}")
        if t == "ask":
            for q in s["qa"]:
                if not q.get("cites"):
                    e(f"ask answer without a source: {q['q']!r}")
    if not HUMAN_STAGES & set(types):
        e("every case needs a person to decide: add a review, exceptions or approve stage")
    if {"upload", "process", "review"} & set(types) and not c["docs"]:
        e("upload/process/review stages need docs")
    if "review" in types and "process" not in types:
        e("review without a process stage")
    for d in c["docs"]:
        if d.get("kind") not in DOC_KINDS:
            e(f"doc {d.get('name')!r}: kind must be one of {sorted(DOC_KINDS)}")
        if d.get("kind") == "sheet" and not d.get("rows") and not d.get("body"):
            e(f"sheet {d['name']!r} needs rows")
        for f in d.get("fields", []):
            if len(f) not in (3, 4):
                e(f"field {f} must be F(label, value, where[, conf])")
        for r in (d.get("table") or {}).get("r", []):
            if r[-1] not in TONES:
                e(f"doc {d['name']!r} table row must end with a status: {r}")
        for fl in d.get("flags", []):
            if isinstance(fl, list) and fl[0] not in TONES:
                e(f"flag tone {fl[0]!r} in {d['name']!r}")
    blob = json.dumps(c, ensure_ascii=False)
    m = BANNED_RE.search(blob)
    if m:
        e(f"banned text {m.group(0)!r} (brand, people or an unsupported claim)")
    if re.search(r"https?://", blob):
        e("no URLs in demo data (use 'example' text instead)")
    if err:
        raise SystemExit(f"[{ind['id']}/{where}] " + "; ".join(err))


def page(c, ind, kit_v):
    e = html.escape
    data = dict(c, brand=dict(name=ind["brand"], product=PRODUCT, mark=ind["brand"][:1].upper()))
    data.pop("tags", None)
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    accent = ind.get("accent")
    style = f"<style>:root{{--accent:{accent};--accent-soft:{ind.get('accent_soft', '#eef0f6')}}}</style>" if accent else ""
    return f"""<!doctype html>
<html lang="en"><head>{HEAD}
<title>{e(c['title'])} · demo</title><meta name="description" content="{e(c['tagline'])}">
<link rel="stylesheet" href="../kit/mock.css?v={kit_v}">{style}</head>
<body><noscript>This demo needs JavaScript.</noscript>
<script type="application/json" id="case">{blob}</script>
<script src="../kit/mock.js?v={kit_v}" defer></script></body></html>
"""


def gallery(inds, all_cases, kit_v):
    e = html.escape
    secs, nav = [], []
    for ind in inds:
        cs = [c for c in all_cases if c["ind"] == ind["id"]]
        if not cs:
            continue
        tiles = "".join(f'<a class="tile" href="{c["slug"]}/" data-q="{e((c["title"] + " " + c["tagline"] + " " + " ".join(c["tags"])).lower())}">'
                        f'<b>{e(c["title"])}</b><small>{e(c["tagline"])}</small></a>' for c in cs)
        secs.append(f'<section class="ind" id="{ind["id"]}"><h2>{e(ind["name"])} <small>{len(cs)}</small></h2><div class="grid">{tiles}</div></section>')
        nav.append(f'<a href="#{ind["id"]}">{e(ind["name"])}</a>')
    return f"""<!doctype html>
<html lang="en"><head>{HEAD}<title>Use-case demos</title>
<link rel="stylesheet" href="kit/mock.css?v={kit_v}"></head><body>
<div class="demo-note"><b>Demos</b> · invented data, pre-written results, nothing connected to a real system.</div>
<main class="gal"><h1>See how it works, end to end</h1>
<p class="tagline">{len(all_cases)} walkthroughs across {len(nav)} industries. Each one shows documents arriving, the assistant preparing the work, and a person deciding. Pick one that looks like your week.</p>
<input class="search" id="q" placeholder="Search: invoices, quotes, renewals, claims…" aria-label="Search demos">
<nav class="jump">{''.join(nav)}</nav>
{''.join(secs)}</main>
<script>document.getElementById('q').oninput=e=>{{const v=e.target.value.toLowerCase().trim();document.querySelectorAll('.tile').forEach(t=>t.style.display=!v||t.dataset.q.includes(v)?'':'none');document.querySelectorAll('.ind').forEach(s=>s.style.display=[...s.querySelectorAll('.tile')].some(t=>t.style.display!=='none')?'':'none')}}</script>
</body></html>
"""


def main():
    only = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None
    inds, all_cases = load(only)
    by_id = {i["id"]: i for i in inds}
    seen = set()
    for i in inds:
        for k in ("name", "brand"):
            if not (i.get(k)):
                raise SystemExit(f"industry {i['id']} needs {k}")
    for c in all_cases:
        if not (c["slug"] not in seen and c["slug"] != "kit"):
            raise SystemExit(f"duplicate slug {c['slug']}")
        seen.add(c["slug"])
        validate(c, by_id[c["ind"]])
    import taxonomy  # every case needs browse facets: they drive its indexed page and hubs under /use-cases/
    vocab = {"fn": taxonomy.FUNCTIONS, "skills": taxonomy.SKILLS, "tasks": taxonomy.TASKS}
    for c in all_cases:
        f = taxonomy.MAP.get(c["slug"])
        if f is None:
            raise SystemExit(f"{c['slug']}: add it to tools/mocks/taxonomy.py MAP (fn, skills, tasks)")
        for k, ids in f.items():
            bad = [i for i in ids if i not in vocab[k]]
            if bad or not ids:
                raise SystemExit(f"{c['slug']}: taxonomy {k} {ids} has unknown or no ids {bad}")
    for i in inds:
        if i["id"] not in taxonomy.INDUSTRY_SEO:
            raise SystemExit(f"industry {i['id']}: add audience and intro to taxonomy.INDUSTRY_SEO")
    print(f"ok: {len(all_cases)} cases in {len(inds)} industries")
    if "--check" in sys.argv or only:
        return
    kit = OUT / "kit"
    kit.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha1()
    for f in ("mock.css", "mock.js"):
        src = (HERE / "kit" / f).read_bytes()
        h.update(src)
        (kit / f).write_bytes(src)
    kit_v = h.hexdigest()[:8]
    for d in OUT.iterdir():  # remove pages for cases that no longer exist
        if d.is_dir() and d.name != "kit" and d.name not in seen:
            shutil.rmtree(d)
    for c in all_cases:
        p = OUT / c["slug"] / "index.html"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(page(c, by_id[c["ind"]], kit_v), encoding="utf-8")
    (OUT / "index.html").write_text(gallery(inds, all_cases, kit_v), encoding="utf-8")
    # Final guard over everything written.
    for f in OUT.rglob("*"):
        if f.suffix in (".html", ".js", ".css"):
            t = f.read_text(encoding="utf-8")
            if not (not LEAK_RE.search(t)):
                raise SystemExit(f"brand/tracker leak in {f}")
            if not (not EXTERNAL_RE.search(t)):
                raise SystemExit(f"external request in {f}")
            if f.suffix == ".html":
                if not (ROBOTS in t):
                    raise SystemExit(f"noindex missing in {f}")
    print(f"wrote {len(all_cases)} demos + gallery to {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
