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
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import bending_data as BD  # noqa: E402  (moves and subelements; see tools/bending_data.py)
import bosses as BOSS  # noqa: E402  (boss page extras; see tools/bosses.py)
DISCORD = "https://discord.gg/sDV3UeRgCH"
STAFF_FORM = "https://docs.google.com/forms/d/e/1FAIpQLScwG0y4fhHJuOsHGs1cWmVXj707PEQFZhoxQ46axCv9K23ASQ/viewform"

# Sidebar: (group, [(page, label), ...]). The group is also the page's breadcrumb.
SIDEBAR = [
    ("", [("index", "Home")]),
    ("New Players", [("how-to-play", "Getting Started"), ("commands", "Commands")]),
    ("Bending", [("bending", "Bending & Tiers"), ("earthbending", "Earthbending"), ("waterbending", "Waterbending"),
                 ("firebending", "Firebending"), ("chi-blocking", "Chi Blocking"), ("weapons-master", "Weapons Master")]),
    ("Story", [("quests", "Arc 1"), ("side-quests", "Side Quests")]),
    ("City Life", [("dossier", "Dossier & Titles"), ("alignment", "Order & Chaos"), ("roleplay-ranks", "Roleplay Ranks"),
                   ("economy", "Money & Crafting"), ("housing", "Housing")]),
    ("Field Guide", [("field-guide", "Mobs, Bosses & Items")]),
]

# "See also" at the bottom of each page.
RELATED = {
    "how-to-play": ["quests", "bending", "commands", "side-quests"],
    "commands": ["how-to-play", "dossier", "housing"],
    "bending": ["earthbending", "waterbending", "firebending", "chi-blocking", "weapons-master"],
    "earthbending": ["bending", "roleplay-ranks", "field-guide"],
    "waterbending": ["bending", "roleplay-ranks", "field-guide"],
    "firebending": ["bending", "roleplay-ranks", "field-guide"],
    "chi-blocking": ["bending", "roleplay-ranks", "weapons-master"],
    "weapons-master": ["bending", "economy", "field-guide"],
    "quests": ["side-quests", "alignment", "field-guide", "housing"],
    "side-quests": ["quests", "alignment", "economy"],
    "dossier": ["alignment", "roleplay-ranks", "commands"],
    "alignment": ["roleplay-ranks", "quests", "dossier"],
    "roleplay-ranks": ["alignment", "bending", "dossier"],
    "economy": ["housing", "field-guide", "weapons-master"],
    "housing": ["economy", "quests", "commands"],
    "field-guide": ["quests", "economy", "bending"],
}

# Cross-links: the first time one of these appears on a page, it links to where it's explained.
# Longest first wins; case-sensitive. Text is matched as it is in the HTML (so "&amp;" for &).
LINKS = [
    ("Order &amp; Chaos", "alignment.html"), ("Order or Chaos", "alignment.html"), ("Order and Chaos", "alignment.html"),
    ("Quest Points", "economy.html#currency"), ("Yuans", "economy.html#currency"),
    ("bending tiers", "bending.html#tiers"), ("Tier II", "bending.html#tiers"), ("Discipline", "bending.html#subelements"),
    ("Technique Scrolls", "bending.html#scrolls"), ("Scroll: Catapult", "bending.html#scrolls"), ("technique scrolls", "bending.html#scrolls"),
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
    ("Noodle Man Raku", "economy.html#shops"), ("Old Man Shen", "economy.html#basics"),
    ("blueprints", "economy.html#blueprints"), ("Blueprints", "economy.html#blueprints"),
    ("Field Guide", "field-guide.html"), ("Spider-Rat Queen", "boss-spider-rat-queen.html"),
    ("Pitmaster Jax", "boss-pitmaster-jax.html"), ("Veterans", "field-guide.html#how-to-fight"),
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
        head = f'<div class="gh">{html.escape(group)}</div>' if group else ""
        out.append(f'<div class="grp">{head}')
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

# Hover definitions: the first mention of a term on a page gets a dotted underline and a one-line
# definition on hover (or tap on phones). (pattern, definition); patterns are regexes, case-sensitive.
GLOSSARY = [
    (r"Quest Points|QP", "Earned from quests. They raise your bending tier and are never spent."),
    (r"Yuans", "The city's money. Earned from quests and mobs, spent in shops."),
    (r"Order (?:and|or|&amp;) Chaos", "Two separate scores your quest choices raise. They open different Roleplay Ranks."),
    (r"Tier (?:I|II|III)\b|Tier &#9733;", "Your bending rank: I to start, II at 50 QP, III at 250, star at 500. It goes up by itself."),
    (r"[Ss]ubelements?", "A specialty inside an element, like Metal or Ice. Benders get one at Tier II, two at III, three at star."),
    (r"Discipline", "The line on your dossier that lists your subelements."),
    (r"[Rr]oleplay [Rr]anks?", "Groups you can join, like the police or the White Lotus. Your rank shows on your nametag."),
    (r"Technique Scrolls?", "Read one to learn a move for good, at any tier. Bosses drop some; TenTen sells others."),
    (r"[Ww]aypoints?", "Landmarks you've walked past. /wp takes you back to any of them."),
    (r"[Cc]ombos?\b", "A move you perform by chaining other moves in order."),
]
GLOSSARY_SKIP = SKIP_TAGS | {"th", "summary", "small"}


def glossary(body):
    """Wrap the first mention of each GLOSSARY term in a hover definition (outside headings, links, code)."""
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
            elif (tag in GLOSSARY_SKIP or 'class="gl"' in part or 'class="cb"' in part) and not part.endswith("/>"):
                stack.append(tag)
            out.append(part)
            continue
        if stack or not part.strip():
            out.append(part)
            continue
        for i, (pat, tip) in enumerate(GLOSSARY):
            if i in done:
                continue
            m = re.search(r"(?<![\w-])(?:" + pat + r")(?![\w-])", part)
            if not m:
                continue
            part = (part[:m.start()] + f'<span class="gl" tabindex="0" data-tip="{html.escape(tip)}">{m.group(0)}</span>'
                    + part[m.end():])
            done.add(i)
            break
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


# ---------------- Bending: move and subelement pages, move tables (data in tools/bending_data.py) ----------------
def move_url(m):
    return f"move-{BD.slug(m['name'])}.html"


def sub_url(key):
    return f"sub-{key}.html"


def move_li(m, show_sub=True):
    cls = []
    if m["sub"]:
        cls += ["sm", f"s-{m['sub']}"]
    if m["later"]:
        cls.append("later")
    c = f' class="{" ".join(cls)}"' if cls else ""
    name = html.escape(m["name"])
    inner = name if m["later"] else f'<a href="{move_url(m)}">{name}</a>'
    if m["combo"]:
        inner += '<span class="cb">combo</span>'
    if m["later"]:
        inner += '<span class="cb">coming later</span>'
    title = f' title="{BD.SUBS[m["sub"]]["name"]}"' if m["sub"] and show_sub else ""
    return f"<li{c}{title}>{inner}</li>"


def tier_groups():
    """The tiers plus the Scrolls group (scroll-only moves), as (key, name, sub-label)."""
    return [(t, n, q) for t, (n, q) in BD.TIERS.items()] + [("SC", BD.SCROLL_TIER[0], BD.SCROLL_TIER[1])]


def tier_label(t):
    return BD.SCROLL_TIER if t == "SC" else BD.TIERS[t]


def moves_of(path, tier):
    return [m for m in BD.MOVES if m["path"] == path and m["tier"] == tier and not m["later"]]


def coming_later(paths=None):
    """One line naming the moves that aren't on the server yet (they're left out of the tables)."""
    later = [m["name"] for m in BD.MOVES if m["later"] and (paths is None or m["path"] in paths)]
    blank = [BD.PATHS[k]["name"] for k in (paths or BD.PATHS)
             if any(not moves_of(k, t) for t in BD.TIERS)]
    bits = []
    if later:
        bits.append(", ".join(later))
    if blank:
        bits.append("more " + " and ".join(blank) + " moves" if len(blank) < 3 else "more moves for " + ", ".join(blank))
    return f'<p class="hint">Coming later: {"; ".join(bits)}.</p>' if bits else ""


def sub_legend(paths=None):
    chips = "".join(f'<a class="schip s-{k}" href="{sub_url(k)}">{v["name"]}</a>'
                    for k, v in BD.SUBS.items() if paths is None or v["path"] in paths)
    return f'<p class="sublegend"><span>Subelement moves</span>{chips}</p>' if chips else ""


def moves_table():
    head = "".join(f'<th>{n}<small>{q}</small></th>' for _, n, q in tier_groups())
    rows = []
    for key, p in BD.PATHS.items():
        cells = []
        for t, n, q in tier_groups():
            ms = moves_of(key, t)
            inner = f'<ul class="mv">{"".join(move_li(m) for m in ms)}</ul>' if ms else '&mdash;'
            cells.append(f'<td data-l="{n} &middot; {q}">{inner}</td>')
        rows.append(f'<tr><td data-l="Path"><a href="{p["page"]}.html">{p["name"]}</a></td>{"".join(cells)}</tr>')
    return (sub_legend() + f'<div class="tbl-wrap"><table class="moves"><thead><tr><th>Path</th>{head}</tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>' + coming_later())


def path_moves_table(path):
    rows = []
    for t, n, q in tier_groups():
        ms = moves_of(path, t)
        if not ms:
            continue
        inner = f'<ul class="mv">{"".join(move_li(m) for m in ms)}</ul>'
        rows.append(f'<tr><td data-l="Tier">{n}<small>{q}</small></td><td data-l="Moves">{inner}</td></tr>')
    paths = [path]
    return (sub_legend(paths) + '<div class="tbl-wrap"><table class="moves path"><thead><tr><th>Tier</th><th>Moves</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>' + coming_later([path]))


def fill_markers(body):
    body = body.replace("<!-- moves-table -->", moves_table())
    return re.sub(r"<!-- moves:(\w+) -->", lambda mm: path_moves_table(mm.group(1)), body)


def move_page(m):
    p = BD.PATHS[m["path"]]
    n, q = tier_label(m["tier"])
    rows = [f'<dt>Path</dt><dd><a href="{p["page"]}.html">{p["name"]}</a></dd>']
    if m["sub"]:
        rows.append(f'<dt>Subelement</dt><dd><a class="schip s-{m["sub"]}" href="{sub_url(m["sub"])}">{BD.SUBS[m["sub"]]["name"]}</a></dd>')
    if m.get("scroll"):
        rows.append(f'<dt>Learned from</dt><dd><a href="bending.html#scrolls">Scroll: {html.escape(m["name"])}</a></dd>')
        rows.append(f'<dt>Price</dt><dd>{m["scroll"]["price"]} Yuans, {m["scroll"].get("seller", BD.SCROLL_SELLER)}</dd>')
        rows.append('<dt>Tier</dt><dd>Any</dd>')
    else:
        rows.append(f'<dt>Tier</dt><dd><a href="bending.html#tiers">{n}</a> ({q})</dd>')
    rows.append(f'<dt>Type</dt><dd>{"Combo" if m["combo"] else "Move"}</dd>')
    tcls = f's-{m["sub"]}' if m["sub"] else f'bg-{m["path"]}'
    box = f'<aside class="infobox"><div class="ib-title {tcls}">{html.escape(m["name"])}</div><dl>{"".join(rows)}</dl></aside>'
    steps = "".join(f'<li>{"<b>" + lab + ".</b> " if lab else ""}{how}</li>' for lab, how in m["use"])
    if not m["combo"]:
        steps += f'<li><b>Bind it.</b> <code>/b bind {m["name"].replace(" ", "")} &lt;slot&gt;</code> puts it on a hotbar slot (1&ndash;9).</li>'
    hint = ('<p class="hint">A combo: you perform it by chaining the moves above. <code>/b help '
            f'{m["name"].replace(" ", "")}</code> shows the sequence in game.</p>') if m["combo"] else ""
    others = [o for o in BD.MOVES if o is not m and not o["later"] and o["path"] == m["path"] and o["sub"] == m["sub"]]
    label = BD.SUBS[m["sub"]]["name"] if m["sub"] else p["name"]
    more = ""
    if others:
        more = (f'<h2 id="more">More {label} Moves</h2><ul class="mv inline">'
                + "".join(move_li(o, False) for o in others) + "</ul>")
    body = (f'{box}<p class="lead">{m["what"]}</p>\n<h2 id="use">How to Use</h2><ul>{steps}</ul>{hint}\n'
            f'<h2 id="get">How to Get It</h2><p>{m["get"] or BD.default_get(m)}</p>\n{more}\n')
    crumb = f'Bending &middot; {p["name"]}'
    desc = f'{m["name"]}: a {label} move on Republic City MC. How to use it and how to get it.'
    return f"move-{BD.slug(m['name'])}", m["name"], desc, body, crumb, p["page"]


def sub_page(key):
    s = BD.SUBS[key]
    p = BD.PATHS[s["path"]]
    sibs = " &middot; ".join(f'<a href="{sub_url(k)}">{v["name"]}</a>' if k != key else f"<b>{v['name']}</b>"
                             for k, v in BD.SUBS.items() if v["path"] == s["path"])
    first = BD.TIERS[s.get("first", BD.SUB_FIRST_TIER[s["path"]])]
    ms = [m for m in BD.MOVES if m["sub"] == key and not m["later"]]
    later = [m["name"] for m in BD.MOVES if m["sub"] == key and m["later"]]
    rows = [f'<dt>Element</dt><dd><a href="{p["page"]}.html">{p["name"]}</a></dd>',
            f'<dt>Subelements</dt><dd>{sibs}</dd>',
            f'<dt>From</dt><dd>{first[0]} ({first[1]})</dd>']
    box = f'<aside class="infobox"><div class="ib-title s-{key}">{s["name"]}</div><dl>{"".join(rows)}</dl></aside>'
    if ms:
        mt = "".join(f'<tr><td data-l="Move"><ul class="mv">{move_li(m, False)}</ul></td><td data-l="Tier">{tier_label(m["tier"])[0]}</td>'
                     f'<td data-l="What it does">{m["what"]}</td></tr>' for m in ms)
        moves = f'<div class="tbl-wrap"><table><thead><tr><th>Move</th><th>Tier</th><th>What it does</th></tr></thead><tbody>{mt}</tbody></table></div>'
    else:
        moves = "<p>No moves of its own yet: it opens up new things to bend with the moves you already know.</p>"
    if later:
        moves += f'<p class="hint">Coming later: {", ".join(later)}.</p>'
    body = (f'{box}<p class="lead">{s["lead"]}</p>\n<!-- toc -->\n'
            f'<h2 id="bends">What You Can Bend</h2><p>{s["bends"]}</p>\n'
            f'<h2 id="moves">Moves</h2>{moves}\n'
            f'<h2 id="get">How to Get It</h2><p>{BD.SUB_RULES[s["path"]]} You choose the order. {s["teacher"]}</p>\n')
    body = body.replace("<!-- toc -->", toc(body))
    desc = f'{s["name"]}, a {p["name"].lower()} subelement on Republic City MC: what it bends, its moves and how to get it.'
    return f"sub-{key}", f'{s["name"]} ({p["name"]})', desc, body, f'Bending &middot; Subelements', p["page"]


# ---------------- Field Guide: boss pages (stats from assets/wiki-data.js, live from the sheet in the browser) ----------------
def wiki_data():
    js = (ROOT / "assets" / "wiki-data.js").read_text()
    return json.loads(js[js.index("window.RC_DATA=") + len("window.RC_DATA="):].strip().rstrip(";"))


def boss_slug(name):
    return "boss-" + re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


BOSS_JS = """<script src="assets/wiki-data.js"></script>
<script src="assets/sheet.js"></script>
<script>
(function(){
  var NAME=%s;
  function sentences(t){return String(t||'').split(/(?<=[.!?])\\s+(?=[A-Z])/).filter(Boolean);}
  function drops(t){return String(t||'').split(/(?<=\\))[,.]\\s+|\\.\\s+(?=[A-Z])/).filter(function(x){return x&&x.indexOf('Everyone')!==0;});}
  function li(a){return a.map(function(x){return '<li>'+rcEsc(x)+'</li>';}).join('');}
  function draw(rows){
    var r=rows.filter(function(x){return x['Name']===NAME;})[0]; if(!r) return;
    var set=function(id,v){var e=document.getElementById(id); if(e) e.innerHTML=v;};
    set('bs-found',rcEsc(r['Found In'])); set('bs-health',rcEsc(r['Health'])); set('bs-melee',rcEsc(r['Melee Damage']));
    set('bs-abilities',li(sentences(r['Abilities']))); set('bs-drops',li(drops(r['Drops'])));
  }
  if(window.RC_DATA) draw(RC_DATA.Bestiary);
  rcLoadSheet('Bestiary').then(draw).catch(function(){});
})();
</script>
"""


def sentences(t):
    return [x for x in re.split(r"(?<=[.!?])\s+(?=[A-Z])", t or "") if x]


def drop_list(t):
    """Drops as a list; the shared-loot sentence is shown once on its own, not as a drop."""
    return [x for x in re.split(r"(?<=\))[,.]\s+|\.\s+(?=[A-Z])", t or "") if x and not x.startswith("Everyone")]


def boss_page(r):
    name = r["Name"]
    extra = BOSS.BOSSES.get(name, {})
    esc = html.escape
    rows = [f'<dt>Found in</dt><dd id="bs-found">{esc(r.get("Found In", ""))}</dd>',
            f'<dt>Health</dt><dd id="bs-health">{esc(r.get("Health", ""))}</dd>',
            f'<dt>Melee</dt><dd id="bs-melee">{esc(r.get("Melee Damage", ""))}</dd>']
    if extra.get("story"):
        rows.append(f'<dt>Story</dt><dd><a href="{extra["story"][1]}">{esc(extra["story"][0])}</a></dd>')
    box = f'<aside class="infobox"><div class="ib-title plain">{esc(name)}</div><dl>{"".join(rows)}</dl></aside>'
    abil = "".join(f"<li>{esc(x)}</li>" for x in sentences(r.get("Abilities", "")))
    drops = "".join(f"<li>{esc(x)}</li>" for x in drop_list(r.get("Drops", "")))
    tips = "".join(f"<li>{t}</li>" for t in extra.get("tips", []))
    inner = (f'<h2 id="fight">The Fight</h2><ul id="bs-abilities">{abil}</ul>\n'
             + (f'<h2 id="tips">Tips</h2><ul>{tips}</ul>\n' if tips else "")
             + f'<h2 id="drops">Drops</h2><p>Everyone who does at least 10% of the damage gets their own roll.</p><ul id="bs-drops">{drops}</ul>\n'
             + '<p class="hint">Numbers update from the live Field Guide sheet. Every mob and boss: <a href="field-guide.html">Mobs, Bosses &amp; Items</a>.</p>\n')
    spoiler = (r.get("Spoiler") or "").lower() == "yes"
    if spoiler:
        body = (f'{box}<p class="lead">A boss from late in the story. Everything below is a spoiler.</p>\n'
                f'<details class="spoiler"><summary>Show the fight (spoilers)</summary><div class="inner">\n{inner}</div></details>\n')
    else:
        body = f'{box}<p class="lead">How the fight works, how to win it, and what drops.</p>\n<!-- toc -->\n{inner}'
        body = body.replace("<!-- toc -->", toc(body))
    body += BOSS_JS % json.dumps(name)
    desc = f"{name}, a boss on Republic City MC: how the fight works, tips and drops."
    return boss_slug(name), name, desc, body, "Field Guide &middot; Bosses", "field-guide"


def boss_pages():
    return [boss_page(r) for r in wiki_data().get("Bestiary", []) if r.get("Name") and (r.get("Rank") or "").lower() == "boss"]


def generated_pages():
    return [move_page(m) for m in BD.MOVES if not m["later"]] + [sub_page(k) for k in BD.SUBS] + boss_pages()


def write_page(name, title, desc, body, crumb, side):
    h1 = "" if name == "index" else f"<h1>{html.escape(title)}</h1>"
    page = (HEAD.format(title=html.escape(title), desc=html.escape(desc), discord=DISCORD)
            + sidebar(side) + f'\n<main class="article">\n{crumb}{h1}\n{body}</main>\n'
            + FOOT.format(discord=DISCORD, staff=STAFF_FORM))
    (ROOT / f"{name}.html").write_text(page)
    print("built", f"{name}.html")


def build():
    groups = {page: group for group, pages in SIDEBAR for page, _ in pages}
    entries = []
    for src in sorted((ROOT / "pages").glob("*.html")):
        name = src.stem
        text = src.read_text()
        meta = dict(re.findall(r"<!-- (\w+): (.*?) -->", text))
        body = re.sub(r"<!-- (\w+): .*? -->\n?", "", text)
        body = fill_markers(body)
        body = body.replace("<!-- toc -->", toc(body))
        title = meta.get("title", name)
        if name != "index":
            index_page(name, title, body, entries, meta.get("desc", ""))
            body = autolink(glossary(body), name) + see_also(name)
        crumb = "" if name == "index" else f'<div class="crumb">{html.escape(groups.get(name, ""))}</div>'
        write_page(name, title, meta.get("desc", ""), body, crumb, name)
    for name, title, desc, body, crumb, side in generated_pages():
        index_page(name, title, body, entries, desc)
        titles = {page: label for _, pages in SIDEBAR for page, label in pages}
        first = ('<a href="bending.html">Bending &amp; Tiers</a> &middot; ' if side != "field-guide" else "")
        body = autolink(glossary(body), name) + f'\n<div class="seealso"><span>See also</span> {first}<a href="{side}.html">{html.escape(titles.get(side, side))}</a></div>\n'
        write_page(name, title, desc, body, f'<div class="crumb">{crumb}</div>', side)
    index_field_guide(entries)
    (ROOT / "assets" / "search-index.js").write_text(
        "// Search index for the wiki search box. Generated by tools/build.py; don't edit by hand.\n"
        "window.RC_SEARCH=" + json.dumps(entries, ensure_ascii=False, separators=(",", ":")) + ";\n")
    print("search index:", len(entries), "entries")


if __name__ == "__main__":
    build()
