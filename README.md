# Republic City MC Wiki

Live at https://republiccitymc.github.io

Six tabs: Home · How to Play · Quests · Systems · Codex · The Build (+ Discord button).

- **Server address:** set it once in `assets/site.js` (`RC_SERVER.address`). Every page, the copy button and the online/player-count badge update from there. Leave it `''` to show "Address coming soon".
- One HTML file per page. Shared look: `assets/style.css`. Menu: the `<nav>` block at the top of every page.
- The Codex (Bestiary + Items) loads live from the Google Sheet **RCMC Wiki Data (public)** via `assets/sheet.js`.
  Edit the sheet, not the HTML, to change mobs, drops, items or prices. The sheet must stay shared as
  "Anyone with the link: Viewer".
- Old page URLs (getting-started, commands, bending, factions, economy, bestiary, items) redirect to their new homes, so old links in Discord still work.
