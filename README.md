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
- **Bosses:** each Bestiary row with Rank "Boss" gets a page (`boss-<name>.html`) built from the Field Guide data, refreshed live from the sheet in the browser. Story links and fight tips go in `tools/bosses.py`.
- **Hover definitions:** `GLOSSARY` in `tools/build.py`. The first mention of each term on a page gets a dotted underline and a one-line definition.
- **Moves and subelements:** every move and subelement lives in `tools/bending_data.py`. The build makes a page for each (`move-<name>.html`, `sub-<name>.html`), the Moves by Tier table on Bending & Tiers, and each path page's move table. Change a move there, not in the HTML.
- **Search:** `tools/build.py` writes `assets/search-index.js` (every page section plus the Field Guide snapshot; spoiler sections left out). The box is in the top bar, and in the sidebar on phones. `/` focuses it.
- **Cross-links and See also:** the build links the first mention of each term in `LINKS` (in `tools/build.py`) and adds a See also row from `RELATED`. Add a term there, not by hand. Titles that must not be linked go in `PROTECT`.
- **At a glance boxes:** `<dl class="glance">` right after a page's lead paragraph, for the quick answers.
- **Server address:** set once in `assets/site.js` (`RC_SERVER.address`). Every address box and the online badge update. Leave it `''` for "Address coming soon".
- **Look:** colors and shared components in `assets/style.css`; the wiki layout (sidebar, infobox, contents) in `assets/wiki.css`.
- **Field Guide** (mobs, bosses, items) shows the snapshot in `assets/wiki-data.js` instantly, then loads live from the Google Sheet **RCMC Wiki Data (public)** via `assets/sheet.js`. Edit the sheet, not the HTML. Keep it shared as "Anyone with the link: Viewer".
- **Old links** (systems, getting-started, factions, bestiary, items, codex, behind-the-build, rules, crafting) redirect to their new pages, so links in Discord keep working.
