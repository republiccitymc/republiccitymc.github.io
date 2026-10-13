# Republic City MC Wiki

Live at https://republiccitymc.github.io

Five tabs: Home · How to Play · Quests · Systems · Field Guide (+ Discord button).

- **Server address:** set it once in `assets/site.js` (`RC_SERVER.address`). Every page, the copy button and the online/player-count badge update from there. Leave it `''` to show "Address coming soon".
- One HTML file per page. Shared look: `assets/style.css`. Menu: the `<nav>` block at the top of every page.
- The Field Guide (mobs, bosses, items) shows the snapshot in `assets/wiki-data.js` instantly, then loads live from the Google Sheet **RCMC Wiki Data (public)** via `assets/sheet.js`.
  Edit the sheet, not the HTML, to change mobs, drops, items or prices. The sheet must stay shared as
  "Anyone with the link: Viewer".
- Home page photos: the `PHOTOS` list in the build script (imgur IDs).
- Old page URLs (getting-started, commands, bending, factions, economy, bestiary, items, codex, behind-the-build) redirect to their new homes, so old links in Discord still work.
