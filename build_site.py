"""Wrap the two artifact bodies into a standalone 2-page site for GitHub Pages.

The artifact publisher supplies <!doctype>/<head>/<body> at publish time, so the
source files are body content only. GitHub Pages serves them raw, so they need a
real document shell here: charset, viewport, noindex, and the shared nav.

Single source of truth stays in workflow.html / mac-setup.html.

    python build_site.py
"""

import pathlib
import re

ROOT = pathlib.Path(__file__).parent
# GitHub Pages can only serve from the repo root or /docs, not an arbitrary folder
OUT = ROOT / "docs"

PAGES = [
    ("workflow.html", "index.html", "The pipeline"),
    ("mac-setup.html", "mac.html", "Mac setup"),
    ("acestep-applio.html", "apps.html", "Make the song"),
    ("prompts.html", "prompts.html", "Prompts"),
]

NAV_CSS = """
  .sitenav {
    position: sticky; top: 0; z-index: 20;
    background: var(--paper); border-bottom: 1px solid var(--rule);
    margin: 0 -1.5rem 0; padding: 0 1.5rem;
  }
  .sitenav-inner {
    max-width: 62rem; margin: 0 auto; display: flex; align-items: baseline;
    gap: 1.5rem; padding: 0.85rem 0; flex-wrap: wrap;
  }
  .sitenav .brand {
    font-family: var(--serif); font-size: 0.95rem; color: var(--ink);
    margin-right: auto; text-decoration: none;
  }
  .sitenav a.tab {
    font-size: 0.78rem; font-weight: 650; letter-spacing: 0.06em;
    text-transform: uppercase; text-decoration: none; color: var(--ink-faint);
    padding: 0.2rem 0; border-bottom: 2px solid transparent;
  }
  .sitenav a.tab:hover { color: var(--ink); }
  .sitenav a.tab[aria-current="page"] { color: var(--rubric); border-bottom-color: var(--rubric); }
  .masthead { padding-top: 3rem; }
"""


def nav_html(current):
    tabs = "".join(
        '<a class="tab" href="{href}"{cur}>{label}</a>'.format(
            href=href,
            label=label,
            cur=' aria-current="page"' if href == current else "",
        )
        for _, href, label in PAGES
    )
    return (
        '<nav class="sitenav"><div class="sitenav-inner">'
        '<a class="brand" href="index.html">Evangelio del D&iacute;a</a>'
        f"{tabs}</div></nav>"
    )


def build():
    OUT.mkdir(exist_ok=True)
    for src_name, out_name, _ in PAGES:
        raw = (ROOT / src_name).read_text(encoding="utf-8")

        m = re.search(r"<title>(.*?)</title>", raw, re.S)
        title = m.group(1).strip() if m else "Evangelio del Dia"
        body = raw[m.end():] if m else raw

        # inject the nav styles just before the stylesheet closes
        body = body.replace("</style>", NAV_CSS + "</style>", 1)
        # nav goes above the existing .wrap
        body = body.replace('<div class="wrap">', nav_html(out_name) + '\n<div class="wrap">', 1)

        doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<meta name="description" content="Daily Spanish Gospel to song to YouTube pipeline, and the Mac setup walkthrough.">
<title>{title}</title>
</head>
<body>
{body}
</body>
</html>
"""
        (OUT / out_name).write_text(doc, encoding="utf-8")
        print(f"  {src_name:20} -> docs/{out_name:12} {len(doc):>7,} bytes  \"{title}\"")

    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    print("  wrote docs/.nojekyll (stops Pages running Jekyll over it)")


if __name__ == "__main__":
    print("building site/")
    build()
