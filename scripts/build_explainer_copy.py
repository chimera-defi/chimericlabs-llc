#!/usr/bin/env python3
"""Build the self-contained miner-site copies of two site articles. The site files are the only sources.

  python3 scripts/build_explainer_copy.py OUT_DIR           write how-it-works-v3.html and search-complexity.html
  python3 scripts/build_explainer_copy.py OUT_DIR --check   also prove each <article> is identical and the shared pictures match

The article body is copied as is. Only host chrome changes: the shared stylesheets are inlined, the web-font links are
dropped (so the page makes no requests), site links become absolute, links between the two articles point at their
miner-site copies, the breadcrumb points back to the miner docs, and the canonical URL and favicon are set.
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://chimericlabs.xyz/"
MINER = "https://chimera-defi.github.io/simple-sha256-miner/"
# source page -> (file name on the miner site, canonical URL or None to keep the source's)
PAGES = {
    "research/sha256/index.html": ("how-it-works-v3.html", MINER + "how-it-works-v3.html"),
    "research/sha256-search-cost/index.html": ("search-complexity.html", None),
}
# a link to one article from the other stays on the miner site in the copy
LOCAL = {"../sha256-search-cost/": "search-complexity.html", "../sha256/": "how-it-works-v3.html"}
FAVICON = ('<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 32 32%27%3E%3Crect width=%2732%27 height=%2732%27 rx=%277%27 fill=%27%23b3263d%27/%3E'
           '%3Cpath d=%27M13 7 11 25M21 7 19 25M7.5 12.5h17M7 19.5h17%27 stroke=%27%23fff%27 stroke-width=%273%27 stroke-linecap=%27round%27 fill=%27none%27/%3E%3C/svg%3E">')
article = lambda html: re.search(r'<article.*?</article>', html, re.S).group(0)
pictures = lambda html: re.findall(r'<figure class="pic">.*?</figure>', html, re.S)


def build(html, canonical):
    html = re.sub(r'<link rel="(?:preconnect|stylesheet)"[^>]*fonts\.g[^>]*>\n?', '', html)
    html = re.sub(r'<link href="https://fonts\.googleapis[^>]*>\n?', '', html)
    html = re.sub(r'<link rel="stylesheet" href="\.\./\.\./([^"]+)">',
                  lambda m: "<style>\n" + (ROOT / m.group(1)).read_text().strip() + "\n</style>", html)
    html = re.sub(r'<link rel="icon"[^\n]*>', lambda m: FAVICON, html)
    if canonical:
        html = re.sub(r'<link rel="canonical"[^\n]*>', lambda m: f'<link rel="canonical" href="{canonical}">', html)
    html = re.sub(r'<meta property="og:url"[^\n]*\n', '', html)
    head, rest = html.split('<main', 1)
    crumb = re.search(r'<nav class="art-crumb".*?</nav>', rest, re.S).group(0)
    rest = rest.replace(crumb, '<nav class="art-crumb" aria-label="Breadcrumb"><a href="index.html">← Back to the miner docs</a></nav>')
    html = head + '<main' + rest
    for rel, local in LOCAL.items():
        html = html.replace(f'href="{rel}', f'href="{local}')
    html = html.replace('href="../../', f'href="{SITE}').replace('href="../', f'href="{SITE}research/')
    return html


def relative(html):
    """Undo the link changes, so a built article can be compared with its source."""
    for rel, local in LOCAL.items():
        html = html.replace(f'href="{local}', f'href="{rel}')
    return html.replace(f'href="{SITE}research/', 'href="../').replace(f'href="{SITE}', 'href="../../')


if __name__ == "__main__":
    out = pathlib.Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    ok = True
    sources = {}
    for page, (name, canonical) in PAGES.items():
        source = sources[page] = (ROOT / page).read_text()
        built = build(source, canonical)
        (out / name).write_text(built)
        if "--check" in sys.argv:
            # the copy differs only outside <article> (breadcrumb row, links), so the article must match once links are made relative
            same = relative(article(built)) == article(source)
            print(f"{name}: article identical" if same else f"{name}: ARTICLE DIFFERS")
            ok &= same
    if "--check" in sys.argv:
        a, b = (pictures(s) for s in sources.values())
        shared = len(a) == 3 and len(b) == 3 and set(a) == set(b)
        print("pictures shared by both articles: identical" if shared else "PICTURES DIFFER between the two articles")
        ok &= shared
        sys.exit(0 if ok else 1)
