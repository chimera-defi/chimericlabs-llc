#!/usr/bin/env python3
"""Build the self-contained miner-site copy of research/sha256/index.html.

  python3 scripts/build_explainer_copy.py OUT.html          write the copy
  python3 scripts/build_explainer_copy.py OUT.html --check   also prove the <article> is identical

The article body is copied as is. Only host chrome changes: the shared stylesheets are inlined,
the web-font links are dropped (so the page makes no requests), site links become absolute, the
breadcrumb points back to the miner docs, and the canonical URL and favicon are the miner site's.
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE = ROOT / "research/sha256/index.html"
MINER = "https://chimera-defi.github.io/simple-sha256-miner/"
FAVICON = ('<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 32 32%27%3E%3Crect width=%2732%27 height=%2732%27 rx=%277%27 fill=%27%23b3263d%27/%3E'
           '%3Cpath d=%27M13 7 11 25M21 7 19 25M7.5 12.5h17M7 19.5h17%27 stroke=%27%23fff%27 stroke-width=%273%27 stroke-linecap=%27round%27 fill=%27none%27/%3E%3C/svg%3E">')
article = lambda html: re.search(r'<article.*?</article>', html, re.S).group(0)


def build(html):
    html = re.sub(r'<link rel="(?:preconnect|stylesheet)"[^>]*fonts\.g[^>]*>\n?', '', html)
    html = re.sub(r'<link href="https://fonts\.googleapis[^>]*>\n?', '', html)
    html = re.sub(r'<link rel="stylesheet" href="\.\./\.\./([^"]+)">',
                  lambda m: "<style>\n" + (ROOT / m.group(1)).read_text().strip() + "\n</style>", html)
    html = re.sub(r'<link rel="icon"[^\n]*>', lambda m: FAVICON, html)
    html = re.sub(r'<link rel="canonical"[^\n]*>', lambda m: f'<link rel="canonical" href="{MINER}how-it-works-v3.html">', html)
    html = html.replace('<meta property="og:url" content="https://chimericlabs.xyz/research/sha256/">\n', '')
    head, rest = html.split('<main', 1)
    crumb = re.search(r'<nav class="art-crumb".*?</nav>', rest, re.S).group(0)
    rest = rest.replace(crumb, '<nav class="art-crumb" aria-label="Breadcrumb"><a href="index.html">← Back to the miner docs</a></nav>')
    html = head + '<main' + rest
    return html.replace('href="../../', 'href="https://chimericlabs.xyz/')


if __name__ == "__main__":
    out = pathlib.Path(sys.argv[1])
    source = PAGE.read_text()
    built = build(source)
    out.write_text(built)
    if "--check" in sys.argv:
        # the copy differs only outside <article> (breadcrumb row, links), so the article must match once links are made relative
        same = article(built).replace("https://chimericlabs.xyz/", "../../") == article(source)
        print("article identical" if same else "ARTICLE DIFFERS")
        sys.exit(0 if same else 1)
