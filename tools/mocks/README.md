# Use-case demos (`/demo/`)

White-label, clickable walkthroughs of the workflows we build. Each page shows one use case end to end:
documents arrive, the assistant processes them, a person reviews and decides, the system is updated, a report
is generated. Prospects can click through on their own or on a call.

- **Served at** `visionzlab.com/demo/` (gallery) and `visionzlab.com/demo/<slug>/` once pushed to `main` (GitHub Pages).
- **Not indexed:** every page carries `noindex, nofollow, noarchive`, is not in `sitemap.xml` or `llms*.txt`,
  and the only links to them are the "Open the walkthrough" buttons on the indexed use-case pages. Don't add a
  `robots.txt` Disallow: crawlers would then never see the noindex tag.
- **Indexed use-case pages:** every case also gets a VisionzLab page at `use-cases/<slug>/`, plus browse hubs by
  industry, business area, skill and type of work. `tools/build.py` (the site builder) generates them from the
  generic fields only (title, tagline, flow, process steps, send-back reasons, outputs, `next`) and fails the build
  if a case's company or person names reach them. Facets live in `taxonomy.py`.
- **White-label:** the shell is "Acme" + "Assistant". No VisionzLab name, no tracker, no external request.
  The build fails if any of these appear.

## Build

```
python3 tools/mocks/build.py           # writes demo/kit, demo/<slug>/index.html, demo/index.html
python3 tools/mocks/build.py --check   # validate only
python3 tools/mocks/smoke.py [--reject]  # click every demo through in a browser (needs agent-browser + a local server)
```

Standard library only. `demo/` is generated output, so edit the source here and rebuild instead of editing `demo/`.
Add `?fast` to a demo URL to skip the animations.

## Layout

| Path | What |
|---|---|
| `kit/mock.js`, `kit/mock.css` | The runtime: one component per stage type, plus the shell. Brand colours are CSS variables |
| `mk.py` | Authoring helpers (`case`, `D`, `F`, `Tbl`, `Draft`, stage helpers, archetypes) and the stage reference |
| `cases/<industry>.py` | One file per industry: `INDUSTRY = dict(name, brand, accent?, order)` and `CASES = [...]` |
| `build.py` | Loads every case, validates it, writes pages and the gallery, and checks the output |

## Adding a case end to end

1. Write it in `cases/<industry>.py` (below), and add its facets to `taxonomy.py` `MAP` (a new industry also needs
   an `INDUSTRY_SEO` entry). The demo build refuses a case without them.
2. `python3 tools/mocks/build.py` (demos), then `python3 tools/mocks/smoke.py <slug>`.
3. `python3 tools/build.py` (site): the use-case page, hub listings, sitemap and links update themselves.

## Writing a case

Read `mk.py`'s docstring, then copy a case from `cases/core.py` (`quote-rfq-intake` is the fullest).
A case is **documents** plus an ordered list of **stages**:

1. Documents arrive: `upload(...)`, or `inbox(...)` for messages.
2. `process(steps, log)` animates the work. The console lines come from the documents.
3. `review(...)` takes one document at a time: the source on the left (with `[[highlights|Field]]` linked to field
   rows), then extracted `fields`, a checks `table`, `flags` and an editable `draft` on the right. The person
   approves each item or sends it back with a reason. A field whose value starts with `?` must be filled in or
   confirmed first.
4. Optional: `exceptions` (pick an option per issue), `compare` (one filterable status table), `draft`
   (one outbound message), `approve` (the gate: a summary, a checklist, then approve or hold), `write` (records
   appear in the system of record), `report` (a generated document with KPIs, tables, bar charts and sources,
   which can be printed or downloaded), `ask` (answers with citations), `feed` (monitored changes), `calendar`.
5. The runtime adds the Outcome stage, which shows the decisions made and the audit trail.

## Content rules (the build enforces the ones it can)

1. **Invented data only.** No real client, prospect, employer, person, product screen, prompt or field name.
   Company names are plainly fictional ("Lakeshore Mechanical"). Emails use `.example`. No URLs.
2. **A person decides.** Every case has a `review`, `exceptions` or `approve` stage. The assistant never sends,
   pays, signs, files, commits a price or date, or gives advice.
3. **No claims.** Don't claim accuracy, savings or "x% faster". Reports show only counts from the invented
   batch.
4. **Uncertainty is shown, not hidden.** Each case includes at least one item the assistant isn't sure of,
   marked as such rather than guessed.
5. **Excluded here:** legal work and clinics of any kind. Those concept mocks stay internal. Anything that
   handles health records also stays internal.
6. **Generic system names:** "ERP (test copy)", "broker management system", "accounting system". No vendor
   product names in the screens.

The build needs `tools/mocks/private_terms.txt`, a gitignored list of names that must never appear (one regex per
line). A copy is kept in the private workspace next to `PUBLIC_DEMOS_PROVENANCE.md`.
