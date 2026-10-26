#!/usr/bin/env python3
"""Builds the Republic City MC wiki.

Each page's content lives in pages/<name>.html. The top of the file holds a few settings:

    <!-- title: Earthbending -->
    <!-- desc: One sentence for search engines and link previews. -->

Then plain HTML. Every <h2 id="..."> becomes an entry in the page's Contents box, which is placed
where the file says <!-- toc --> (left out if there's no marker). This script wraps every page in
the shared layout (top bar, sidebar, breadcrumb, footer) and writes <name>.html at the site root.

It also:
  - writes assets/search-index.js for the search box (every <h2> section of every page, plus the
    Field Guide's mobs and items from assets/wiki-data.js; spoiler sections are left out),
  - links the first mention of a term from LINKS on each page (never inside links, headings,
    code, buttons, spoilers or scripts, never to the page itself, never to a page it already links),
  - adds a "See also" row from RELATED at the bottom of each page.

Run from anywhere:  python3 tools/build.py
Add a page: create pages/<name>.html and add it to SIDEBAR below (and RELATED).
"""
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
DISCORD = "https://discord.gg/sDV3UeRgCH"
STAFF_FORM = "https://docs.google.com/forms/d/e/1FAIpQLScwG0y4fhHJuOsHGs1cWmVXj707PEQFZhoxQ46axCv9K23ASQ/viewform"

# Sidebar: (group, [(page, label), ...]). The group is also the page's breadcrumb.
SIDEBAR = [
    ("Republic City MC", [("index", "Home")]),
    ("New Players", [("how-to-play", "Getting Started"), ("rules", "Rules"), ("commands", "Commands")]),
    ("Bending", [("bending", "Bending & Tiers"), ("earthbending", "Earthbending"), ("waterbending", "Waterbending"),
                 ("firebending", "Firebending"), ("chi-blocking", "Chi Blocking"), ("weapons-master", "Weapons Master")]),
    ("Story", [("quests", "Main Story"), ("side-quests", "Side Quests"), ("dossier", "Dossier & Titles")]),
    ("Society", [("alignment", "Order & Chaos"), ("roleplay-ranks", "Roleplay Ranks")]),
    ("Economy", [("economy", "Money & Shops"), ("crafting", "Crafting"), ("housing", "Housing")]),
    ("Field Guide", [("field-guide", "Mobs, Bosses & Items")]),
]

# "See also" at the bottom of each page.
RELATED = {
    "how-to-play": ["quests", "bending", "commands", "side-quests"],
    "rules": ["how-to-play", "commands"],
    "commands": ["how-to-play", "dossier", "housing"],
    "bending": ["earthbending", "waterbending", "firebending", "chi-blocking", "weapons-master"],
    "earthbending": ["bending", "roleplay-ranks", "field-guide"],
    "waterbending": ["bending", "roleplay-ranks", "field-guide"],
    "firebending": ["bending", "roleplay-ranks", "field-guide"],
    "chi-blocking": ["bending", "roleplay-ranks", "weapons-master"],
    "weapons-master": ["bending", "crafting", "economy"],
    "quests": ["side-quests", "alignment", "field-guide", "housing"],
    "side-quests": ["quests", "alignment", "economy"],
    "dossier": ["alignment", "roleplay-ranks", "commands"],
    "alignment": ["roleplay-ranks", "quests", "dossier"],
    "roleplay-ranks": ["alignment", "bending", "dossier"],
    "economy": ["crafting", "housing", "field-guide"],
    "crafting": ["economy", "weapons-master", "field-guide"],
    "housing": ["economy", "quests", "commands"],
    "field-guide": ["quests", "economy", "crafting"],
}

# Cross-links: the first time one of these appears on a page, it links to where it's explained.
# Longest first wins; case-sensitive. Text is matched as it is in the HTML (so "&amp;" for &).
LINKS = [
    ("Order &amp; Chaos", "alignment.html"), ("Order or Chaos", "alignment.html"), ("Order and Chaos", "alignment.html"),
    ("Quest Points", "economy.html#currency"), ("Yuans", "economy.html#currency"),
    ("bending tiers", "bending.html#tiers"), ("Tier II", "bending.html#tiers"), ("Discipline", "bending.html#subelements"),
    ("Technique Scrolls", "bending.html#scrolls"), ("Scroll: Catapult", "bending.html#scrolls"),
    ("Registration Form", "how-to-play.html#first-hour"), ("Registrar Huan", "how-to-play.html#first-hour"),
    ("quest compass", "how-to-play.html#finding-your-way"), ("waypoints", "how-to-play.html#finding-your-way"),
    ("dossier", "dossier.html"), ("Dossier", "dossier.html"),
    ("roleplay ranks", "roleplay-ranks.html"), ("Roleplay Ranks", "roleplay-ranks.html"),
    ("Main Story", "quests.html"), ("main story", "quests.html"), ("Avatar Aang", "quests.html"),
    ("side quests", "side-quests.html"), ("Side Quests", "side-quests.html"), ("Scrap Lessons", "side-quests.html"),
    ("Unity Flats", "housing.html"), ("apartment", "housing.html"), ("Landlady Fe", "housing.html#building"),
    ("hidden caches", "economy.html#caches"), ("hidden cache", "economy.html#caches"),
    ("Jian's Tea House", "economy.html#teas"), ("Shady Zhen", "economy.html#shops"),
    ("Weapons Vendor TenTen", "economy.html#shops"), ("TenTen", "economy.html#shops"),
    ("Noodle Man Raku", "economy.html#shops"), ("Old Man Shen", "crafting.html#basics"),
    ("blueprints", "crafting.html#blueprints"), ("Blueprints", "crafting.html#blueprints"),
    ("Field Guide", "field-guide.html"), ("Spider-Rat Queen", "field-guide.html#bosses"),
    ("Pitmaster Jax", "field-guide.html#bosses"), ("Veterans", "field-guide.html#how-to-fight"),
    ("earthbenders", "earthbending.html"), ("Earthbender", "earthbending.html"),
    ("waterbenders", "waterbending.html"), ("Waterbender", "waterbending.html"),
    ("firebenders", "firebending.html"), ("Firebender", "firebending.html"),
    ("chi blockers", "chi-blocking.html"), ("Chi Blocker", "chi-blocking.html"),
    ("weapons masters", "weapons-master.html"), ("Weapons Masters", "weapons-master.html"),
]
LINKS.sort(key=lambda kv: -len(kv[0]))
# Names that contain a LINKS term but mustn't be linked (quest and book titles).
PROTECT = ["The Gutsy Earthbender"]

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | Republic City MC Wiki</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title} | Republic City MC Wiki">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="https://i.imgur.com/pTQClVA.jpg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/style.css">
<link rel="stylesheet" href="assets/wiki.css">
</head>
<body>
<div class="rc wiki">
<header class="topbar"><div class="in">
  <label for="sidetoggle" class="burger" aria-label="Menu">&#9776;</label>
  <a class="brand" href="index.html">REPUBLIC CITY <span>MC</span> <em>Wiki</em></a>
  <div class="search"><input type="search" class="js-search" placeholder="Search the wiki  ( / )" aria-label="Search the wiki" autocomplete="off"><div class="results" hidden></div></div>
  <a class="btn dc" href="{discord}" target="_blank" rel="noopener">Discord</a>
</div></header>
<input type="checkbox" id="sidetoggle">
<div class="layout">
"""

FOOT = """</div>
<footer class="foot">Republic City MC &middot; 130 AG &middot; Java Edition <span class="js-ver">1.21.11</span> &middot;
<a href="{discord}" target="_blank" rel="noopener">Discord</a> &middot; <a href="{staff}" target="_blank" rel="noopener">Join the team</a></footer>
</div>
<script src="assets/search-index.js"></script>
<script src="assets/site.js"></script>
</body>
</html>
"""


def sidebar(current):
    out = ['<aside class="side"><div class="search side-search"><input type="search" class="js-search" placeholder="Search the wiki" aria-label="Search the wiki" autocomplete="off"><div class="results" hidden></div></div>']
    for group, pages in SIDEBAR:
        out.append(f'<div class="grp"><div class="gh">{html.escape(group)}</div>')
        for page, label in pages:
            on = ' class="on"' if page == current else ""
            out.append(f'<a href="{page}.html"{on}>{html.escape(label)}</a>')
        out.append("</div>")
    out.append(f'<div class="grp"><div class="gh">Community</div><a href="{DISCORD}" target="_blank" rel="noopener">Discord</a>'
               f'<a href="{STAFF_FORM}" target="_blank" rel="noopener">Join the team</a></div></aside>')
    return "\n".join(out)


def toc(body):
    heads = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body)
    if len(heads) < 2:
        return ""
    items = "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in heads)
    return f'<nav class="toc"><div class="th">Contents</div><ol>{items}</ol></nav>'


SKIP_TAGS = {"a", "h1", "h2", "h3", "h4", "code", "button", "summary", "script", "style", "label", "details", "dt"}


def autolink(body, name):
    """Link the first mention of each LINKS term, outside SKIP_TAGS. Returns the new body."""
    linked = {m.split("#")[0] for m in re.findall(r'href="([^"]+)"', body)}
    done = set()
    out, stack = [], []
    for part in re.split(r"(<[^>]+>)", body):
        if part.startswith("<"):
            m = re.match(r"</?\s*([a-zA-Z0-9]+)", part)
            tag = m.group(1).lower() if m else ""
            if part.startswith("</"):
                if tag in stack:
                    while stack and stack.pop() != tag:
                        pass
            elif tag in SKIP_TAGS and not part.endswith("/>"):
                stack.append(tag)
            out.append(part)
            continue
        if stack or not part.strip():
            out.append(part)
            continue
        saved = [p for p in PROTECT if p in part]
        for i, p in enumerate(saved):
            part = part.replace(p, f"\x00{i}\x00")
        for term, url in LINKS:
            page = url.split("#")[0]
            if page == f"{name}.html" or page in linked or page in done:
                continue
            m = re.search(r"(?<![\w-])" + re.escape(term) + r"(?![\w-])", part)
            if not m:
                continue
            part = part[:m.start()] + f'<a href="{url}">{term}</a>' + part[m.end():]
            done.add(page)
            # Only one new link per text run, so links never end up inside each other.
            break
        for i, p in enumerate(saved):
            part = part.replace(f"\x00{i}\x00", p)
        out.append(part)
    return "".join(out)


def text_of(fragment):
    fragment = re.sub(r"<details class=\"spoiler\".*?</details>", " ", fragment, flags=re.S)
    fragment = re.sub(r"<(script|style)\b.*?</\1>", " ", fragment, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def index_page(name, title, body, entries, desc=""):
    parts = re.split(r'<h2 id="([^"]+)">(.*?)</h2>', body)
    intro = (desc + " " + text_of(parts[0])).strip()
    if intro:
        entries.append({"p": title, "h": title, "u": f"{name}.html", "x": intro[:1200]})
    for i in range(1, len(parts), 3):
        hid, head, sect = parts[i], text_of(parts[i + 1]), text_of(parts[i + 2])
        if sect:
            entries.append({"p": title, "h": head, "u": f"{name}.html#{hid}", "x": sect[:1200]})


def index_field_guide(entries):
    js = (ROOT / "assets" / "wiki-data.js").read_text()
    data = json.loads(js[js.index("window.RC_DATA=") + len("window.RC_DATA="):].strip().rstrip(";"))
    for r in data.get("Bestiary", []):
        if not r.get("Name"):
            continue
        boss = (r.get("Rank") or "").lower() == "boss"
        spoiler = (r.get("Spoiler") or "").lower() == "yes"
        x = "Spoiler: open the Field Guide to read it." if spoiler else f'{r.get("Found In", "")}. {r.get("Abilities", "")}'
        entries.append({"p": "Field Guide", "h": r["Name"], "u": "field-guide.html#" + ("bosses" if boss else "mobs"), "x": x})
    for r in data.get("Items", []):
        if not r.get("Item") or not (r.get("Category") or r.get("Price")):
            continue
        spoiler = (r.get("Spoiler") or "").lower() == "yes"
        x = "Spoiler: open the Field Guide to read it." if spoiler else f'{r.get("Price", "")}. {r.get("Where to Get", "")}. {r.get("Effect / Notes", "")}'
        entries.append({"p": "Field Guide", "h": r["Item"], "u": "field-guide.html#items", "x": x})


def see_also(name):
    titles = {page: label for _, pages in SIDEBAR for page, label in pages}
    rel = RELATED.get(name)
    if not rel:
        return ""
    links = " &middot; ".join(f'<a href="{p}.html">{html.escape(titles.get(p, p))}</a>' for p in rel)
    return f'\n<div class="seealso"><span>See also</span> {links}</div>\n'


def build():
    groups = {page: group for group, pages in SIDEBAR for page, _ in pages}
    entries = []
    for src in sorted((ROOT / "pages").glob("*.html")):
        name = src.stem
        text = src.read_text()
        meta = dict(re.findall(r"<!-- (\w+): (.*?) -->", text))
        body = re.sub(r"<!-- (\w+): .*? -->\n?", "", text)
        body = body.replace("<!-- toc -->", toc(body))
        title = meta.get("title", name)
        if name != "index":
            index_page(name, title, body, entries, meta.get("desc", ""))
            body = autolink(body, name) + see_also(name)
        crumb = "" if name == "index" else f'<div class="crumb">{html.escape(groups.get(name, ""))}</div>'
        h1 = "" if name == "index" else f"<h1>{html.escape(title)}</h1>"
        page = (HEAD.format(title=html.escape(title), desc=html.escape(meta.get("desc", "")), discord=DISCORD)
                + sidebar(name) + f'\n<main class="article">\n{crumb}{h1}\n{body}</main>\n'
                + FOOT.format(discord=DISCORD, staff=STAFF_FORM))
        (ROOT / f"{name}.html").write_text(page)
        print("built", f"{name}.html")
    index_field_guide(entries)
    (ROOT / "assets" / "search-index.js").write_text(
        "// Search index for the wiki search box. Generated by tools/build.py; don't edit by hand.\n"
        "window.RC_SEARCH=" + json.dumps(entries, ensure_ascii=False, separators=(",", ":")) + ";\n")
    print("search index:", len(entries), "entries")


if __name__ == "__main__":
    build()
