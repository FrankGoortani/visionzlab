# VisionzLab Agent Instructions

## Site generator (added 2026-10-06)

The site is now multi-page. **Do not hand-edit generated pages.** All pages (`index.html` and every
`*/index.html`), `sitemap.xml` and `llms.txt` are written by `python3 tools/build.py` (stdlib only) from
the content in that script; shared styles live in `site.css`. Edit content in `tools/build.py`, run it,
and commit the generated output — GitHub Pages serves the files as-is, there is no deploy-time build.
Contact URL and analytics host are constants at the top of `tools/build.py`.

Positioning rule: the site is brand-led. No individual's name, employer or personal contact details
appear on it, except the dedicated business-development team page.


This repository contains the static VisionzLab marketing website. It is primarily HTML and CSS, with reusable snippets in `components/` and assets in `public/`. Use `CLAUDE.md` for background, but follow this file first for Codex workflow.

## Project Map

- `index.html` - main single-page site.
- `site.css` - all styles (generated pages share it).
- `tools/build.py` - generates every page, `sitemap.xml` and `llms.txt`.
- `public/` - icons and static assets.
- `CNAME`, `sitemap.xml`, `robots.txt`, `llms.txt` - deployment and discovery metadata.

## Coding Style

- Indent using **two spaces**; do not use tabs.
- Keep line length under **120 characters** when possible.
- File and directory names should use **kebab-case**.
- Place all images and icons in the `public/` folder.
- Keep the site static unless the user explicitly asks for a build pipeline.
- Preserve relative asset paths for GitHub Pages compatibility.
- Preserve SEO, CNAME, sitemap, robots, and tracking snippets unless the task is about those files.

## Contribution Guidelines

- Avoid committing the `node_modules/` directory or other generated files.
- Keep commits small and descriptive.
- Add or change pages in `tools/build.py`, run it, and commit the generated output.
- Nothing private in this repo: it is public and GitHub Pages serves it.
- Check mobile responsiveness when changing layout or navigation.

## Testing / Build

There are currently no automated tests or build scripts. If you add a build step or other checks in the future, run them locally before committing.

For manual validation:

```bash
python3 -m http.server 8000
```

Then inspect `http://localhost:8000` for desktop/mobile layout, links, console errors, and CTA behavior.
