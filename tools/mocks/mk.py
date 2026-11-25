"""Authoring helpers for use-case mocks. A case is plain data: documents plus an ordered list of stages.

Stage types (rendered by kit/mock.js):
  upload      files arrive (drop zone or connected inbox)          needs docs
  process     pipeline animation, console log, counters            needs docs
  review      queue + source document + extracted fields/checks/flags/draft, approve or send back per item
  exceptions  issues a person resolves by picking an option
  compare     one table with status filters (match, reconcile, rank)
  draft       an editable outbound draft with alternative versions
  approve     the gate: summary, checklist, approve or hold
  write       records appearing in the system of record (test copy)
  report      generated document: KPIs, sections, tables, bar charts, sources; print and download
  ask         questions with cited answers
  feed        monitored changes with sources
  calendar    a schedule of upcoming actions
The runtime appends an "Outcome" stage (decisions, audit trail, what happens in a real setup).

Text fields accept [[highlight]] or [[highlight|Field label]] (links a span in the source to a field row) and **bold**.
Status values: ok, check, bad, info. A field value starting with "?" is uncertain: the person must fill or confirm it.
"""


def D(name, kind, body="", meta="", **kw):
    """A document. kind: pdf, scan, email, sheet, web, call, docx, note.
    Optional: from_, to, subject (email); rows (sheet: first row is the header); label, sub (queue text);
    fields [F...], table Tbl(...), flags [str | (tone, str)], draft Draft(...), notes, yes (approve label), tone."""
    d = dict(name=name, kind=kind, body=body, meta=meta)
    if "from_" in kw:
        kw["from"] = kw.pop("from_")
    d.update(kw)
    return d


def F(label, value, where="", conf=None):
    return [label, value, where] + ([conf] if conf is not None else [])


def Tbl(title, h, *rows):
    """Rows end with a status (ok/check/bad/info) when used in review/compare; plain rows are fine in reports."""
    return dict(title=title, h=list(h), r=[list(r) for r in rows])


def Draft(text, label="Draft", to=None, subject=None, alt=()):
    d = dict(text=text, label=label, alt=list(alt))
    if to:
        d["to"] = to
    if subject:
        d["subject"] = subject
    return d


# ---- stages -------------------------------------------------------------------------------------

def upload(title="Add documents", sub="", **kw):
    return dict(type="upload", title=title, sub=sub, **kw)


def inbox(source, title="Messages arrive", sub="", **kw):
    return dict(type="upload", mode="inbox", source=source, title=title, sub=sub, **kw)


def process(steps=None, log=None, title="Processing", sub="", **kw):
    """steps: [(title, detail)]. log: [(line, tone 'g'|'y'|'', step_index)] extra console lines."""
    s = dict(type="process", title=title, sub=sub, **kw)
    if steps:
        s["steps"] = [list(x) for x in steps]
    if log:
        s["log"] = [list(x) for x in log]
    return s


def review(title="Review", sub="", yes="Approve", **kw):
    return dict(type="review", title=title, sub=sub, yes=yes, **kw)


def X(title, detail, options, rec=None, tone="check", why=""):
    return dict(title=title, detail=detail, options=list(options), rec=rec, tone=tone, why=why)


def exceptions(items, title="Exceptions", sub="", **kw):
    return dict(type="exceptions", items=list(items), title=title, sub=sub, **kw)


def compare(table, title="Compare", sub="", **kw):
    return dict(type="compare", table=table, title=title, sub=sub, **kw)


def draft(text, title="Draft", sub="", **kw):
    return dict(type="draft", text=text, title=title, sub=sub, **kw)


def approve(question, title="Approval", sub="", summary=(), checks=(), **kw):
    return dict(type="approve", question=question, title=title, sub=sub,
                summary=[list(x) for x in summary], checks=list(checks), **kw)


def R(title, kv=(), status="Saved", tone="ok", note=None):
    r = dict(title=title, kv=[list(x) for x in kv], status=status, tone=tone)
    if note:
        r["note"] = note
    return r


def write(system, records, title="Update the system", sub="", **kw):
    return dict(type="write", system=system, records=list(records), title=title, sub=sub, **kw)


def Sec(h, p=None, list=None, table=None, chart=None, kpis=None):  # noqa: A002 - mirrors the JSON key
    s = dict(h=h)
    for k, v in (("p", p), ("list", list), ("table", table), ("chart", chart), ("kpis", kpis)):
        if v is not None:
            s[k] = v
    return s


def Chart(title, labels, values, unit="", prefix="", tones=None):
    c = dict(title=title, labels=list(labels), values=list(values), unit=unit, prefix=prefix)
    if tones:
        c["tones"] = list(tones)
    return c


def report(doc, sections, title="Report", sub="", **kw):
    """kw: subtitle, kpis [(value, label, tone)], sources [str], format, foot, genSteps."""
    if "kpis" in kw:
        kw["kpis"] = [list(k) for k in kw["kpis"]]
    return dict(type="report", doc=doc, sections=list(sections), title=title, sub=sub, **kw)


def QA(q, a, *cites):
    return dict(q=q, a=a, cites=list(cites))


def ask(qa, title="Ask", sub="", **kw):
    return dict(type="ask", qa=list(qa), title=title, sub=sub, **kw)


def Ev(when, title, text, tag=None, src=None):
    e = dict(when=when, title=title, text=text)
    if tag:
        e["tag"] = list(tag)
    if src:
        e["src"] = src
    return e


def feed(items, title="Monitor", sub="", **kw):
    return dict(type="feed", items=list(items), title=title, sub=sub, **kw)


def calendar(days, title="Schedule", sub="", **kw):
    """days: [(label, [(text, tone)])]"""
    return dict(type="calendar", days=[dict(d=d, ev=[list(e) for e in ev]) for d, ev in days], title=title, sub=sub, **kw)


# ---- the case -----------------------------------------------------------------------------------

def case(slug, title, tagline, flow, stages, docs=(), area="", persona=("Sam Rivera", ""), next=None,  # noqa: A002
         outcome=None, unit=None, tags=()):
    """flow: (starts with, the assistant, a person, ends with)."""
    c = dict(slug=slug, title=title, tagline=tagline, area=area,
             flow=dict(zip(("start", "agent", "person", "end"), flow)),
             persona=dict(name=persona[0], role=persona[1]), docs=list(docs), stages=list(stages), tags=list(tags))
    if next:
        c["next"] = list(next)
    if outcome:
        c["outcome"] = outcome
    if unit:
        c["unit"] = unit
    return c


# ---- archetypes: the common shapes, so a new case is mostly data -----------------------------------

def intake(docs_label="Add documents", steps=None, log=None, yes="Approve", review_title="Review", extra=()):
    """Documents in -> processed -> reviewed one by one -> [extra stages: write / report / draft ...]."""
    return [upload(docs_label), process(steps, log), review(review_title, yes=yes)] + list(extra)


def inbox_flow(source, steps=None, log=None, yes="Send reply", extra=()):
    return [inbox(source), process(steps, log, title="Sorting and drafting"), review("Review and reply", yes=yes)] + list(extra)
