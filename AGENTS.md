# VisionzLab Agent Instructions

This repository contains the static VisionzLab marketing website. It is primarily HTML and CSS, with reusable snippets in `components/` and assets in `public/`. Use `CLAUDE.md` for background, but follow this file first for Codex workflow.

## Project Map

- `index.html` - main single-page site.
- `style.css` - global design tokens and base styles.
- `index.css` - page and section styles.
- `components/` - reusable HTML/CSS snippets.
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
- When adding components or pages, update the main HTML and accompanying CSS.
- Maintain the existing TeleportHQ/accordion behavior unless replacing it is part of the request.
- Check mobile responsiveness when changing layout or navigation.

## Testing / Build

There are currently no automated tests or build scripts. If you add a build step or other checks in the future, run them locally before committing.

For manual validation:

```bash
python3 -m http.server 8000
```

Then inspect `http://localhost:8000` for desktop/mobile layout, links, console errors, and CTA behavior.
