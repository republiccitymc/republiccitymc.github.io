#!/usr/bin/env python3
"""Builds the Republic City MC wiki.

Each page's content lives in pages/<name>.html. The top of the file holds a few settings:

    <!-- title: Earthbending -->
    <!-- desc: One sentence for search engines and link previews. -->

Then plain HTML. Every <h2 id="..."> becomes an entry in the page's Contents box, which is placed
where the file says <!-- toc --> (left out if there's no marker). This script wraps every page in
the shared layout (top bar, sidebar, breadcrumb, footer) and writes <name>.html at the site root.

Run from anywhere:  python3 tools/build.py
Add a page: create pages/<name>.html and add it to SIDEBAR below.
"""
import html
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
DISCORD = "https://discord.gg/sDV3UeRgCH"
STAFF_FORM = "https://docs.google.com/forms/d/e/1FAIpQLScwG0y4fhHJuOsHGs1cWmVXj707PEQFZhoxQ46axCv9K23ASQ/viewform"

# Sidebar: (group, [(page, label), ...]). The group is also the page's breadcrumb.
SIDEBAR = [
    ("Republic City MC", [("index", "Main Page")]),
    ("New Players", [("how-to-play", "Getting Started"), ("rules", "Rules"), ("commands", "Commands")]),
    ("Bending", [("bending", "Bending & Tiers"), ("earthbending", "Earthbending"), ("waterbending", "Waterbending"),
                 ("firebending", "Firebending"), ("chi-blocking", "Chi Blocking"), ("weapons-master", "Weapons Master")]),
    ("Story", [("quests", "Main Story"), ("side-quests", "Side Quests"), ("dossier", "Dossier & Titles")]),
    ("Society", [("alignment", "Order & Chaos"), ("roleplay-ranks", "Roleplay Ranks")]),
    ("Economy", [("economy", "Money & Shops"), ("crafting", "Crafting"), ("housing", "Housing")]),
    ("Field Guide", [("field-guide", "Mobs, Bosses & Items")]),
]

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
  <a class="btn dc" href="{discord}" target="_blank" rel="noopener">Discord</a>
</div></header>
<input type="checkbox" id="sidetoggle">
<div class="layout">
"""

FOOT = """</div>
<footer class="foot">Republic City MC &middot; 130 AG &middot; Java Edition <span class="js-ver">1.21.11</span> &middot;
<a href="{discord}" target="_blank" rel="noopener">Discord</a> &middot; <a href="{staff}" target="_blank" rel="noopener">Join the team</a></footer>
</div>
<script src="assets/site.js"></script>
</body>
</html>
"""


def sidebar(current):
    out = ['<aside class="side"><input type="search" class="js-find" placeholder="Search the wiki" aria-label="Search the wiki">']
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


def build():
    groups = {page: group for group, pages in SIDEBAR for page, _ in pages}
    for src in sorted((ROOT / "pages").glob("*.html")):
        name = src.stem
        text = src.read_text()
        meta = dict(re.findall(r"<!-- (\w+): (.*?) -->", text))
        body = re.sub(r"<!-- (\w+): .*? -->\n?", "", text)
        body = body.replace("<!-- toc -->", toc(body))
        title = meta.get("title", name)
        crumb = "" if name == "index" else f'<div class="crumb">{html.escape(groups.get(name, ""))}</div>'
        h1 = "" if name == "index" else f"<h1>{html.escape(title)}</h1>"
        page = (HEAD.format(title=html.escape(title), desc=html.escape(meta.get("desc", "")), discord=DISCORD)
                + sidebar(name) + f'\n<main class="article">\n{crumb}{h1}\n{body}</main>\n'
                + FOOT.format(discord=DISCORD, staff=STAFF_FORM))
        (ROOT / f"{name}.html").write_text(page)
        print("built", f"{name}.html")


if __name__ == "__main__":
    build()
