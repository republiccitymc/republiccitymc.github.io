# Republic City MC Wiki

Live at https://republiccitymc.github.io

A wiki-style site: sidebar on the left, one article per topic, a facts box and a Contents list on longer pages.

## Editing a page
1. Edit `pages/<name>.html`. The two comment lines at the top are the page title and its one-line description; the rest is plain HTML.
2. Run `python3 tools/build.py`. It wraps every page in the shared layout (top bar, sidebar, breadcrumb, footer) and writes `<name>.html` at the root.
3. Commit both the `pages/` file and the built page.

Every `<h2 id="...">` becomes a Contents entry where the page has `<!-- toc -->`.
To add a page: create `pages/<name>.html` and add it to `SIDEBAR` in `tools/build.py`.

## Other bits
- **Server address:** set once in `assets/site.js` (`RC_SERVER.address`). Every address box and the online badge update. Leave it `''` for "Address coming soon".
- **Look:** colors and shared components in `assets/style.css`; the wiki layout (sidebar, infobox, contents) in `assets/wiki.css`.
- **Field Guide** (mobs, bosses, items) shows the snapshot in `assets/wiki-data.js` instantly, then loads live from the Google Sheet **RCMC Wiki Data (public)** via `assets/sheet.js`. Edit the sheet, not the HTML. Keep it shared as "Anyone with the link: Viewer".
- **Old links** (systems, getting-started, factions, bestiary, items, codex, behind-the-build) redirect to their new pages, so links in Discord keep working.
