#!/usr/bin/env python3
"""Mirror the four server-rendered eth2-quickstart articles for GitHub Pages."""

import argparse
from functools import lru_cache
from html import escape, unescape
from html.parser import HTMLParser
from pathlib import Path
import re
import time
from urllib.error import URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import urlopen


ARTICLES = {
    "ethereum-client-bakeoff": ("Ethereum client bake-off",),
    "bakeoff-results": ("Bake-off results",),
    # The methodology's published title differs from its short card title.
    "how-we-tested-with-claude": ("How", "Bake-off With Claude"),
    "bakeoff-harness": ("The bake-off harness",),
}
URL_ATTRIBUTE = re.compile(r'''(\b(?:href|src)\s*=\s*)(["'])(.*?)\2''', re.I)
CSS_URL = re.compile(r'''url\(\s*(["']?)(/[^\s)"']+)\1\s*\)''', re.I)


@lru_cache(maxsize=None)
def fetch(url, attempts=3):
    # Retry like the DispatchBench step's curl --retry 3, so a CDN blip
    # doesn't fail the whole Pages deploy.
    for attempt in range(1, attempts + 1):
        try:
            with urlopen(url, timeout=60) as response:
                return response.read()
        except (OSError, URLError, ValueError) as error:
            if attempt == attempts:
                raise ValueError(f"Could not fetch {url}: {error}") from error
            time.sleep(2 * attempt)


def source_url(source, path):
    parts = urlsplit(path)
    return urljoin(source.rstrip("/") + "/", parts.path.lstrip("/")) + (
        "?" + parts.query if parts.query else ""
    )


def shared_css(href, source, origin, assets):
    """Write the stylesheet and its fonts once under assets/ and return its link tag.

    Fonts are copied to our own origin (the upstream server's cross-origin policy
    blocks hotlinking them) instead of being embedded, so the four pages share
    one cached copy rather than each carrying ~1.2 MB of base64.
    """
    name = Path(urlsplit(href).path).name
    css = fetch(source_url(source, href)).decode("utf-8")

    def replace_url(match):
        path = match[2]
        if path.startswith("//"):
            return match[0]
        filename = Path(urlsplit(path).path).name
        if filename.lower().endswith(".woff2"):
            font = assets / "fonts" / filename
            font.parent.mkdir(parents=True, exist_ok=True)
            font.write_bytes(fetch(source_url(source, path)))
            return f"url(fonts/{filename})"
        return f"url({match[1]}{origin}{path}{match[1]})"

    assets.mkdir(parents=True, exist_ok=True)
    (assets / name).write_text(CSS_URL.sub(replace_url, css), encoding="utf-8")
    return f'<link rel="stylesheet" href="../assets/{escape(name, quote=True)}">'


class ArticleMirror(HTMLParser):
    def __init__(self, source, origin, slug, assets):
        super().__init__(convert_charrefs=False)
        self.source = source
        self.assets = assets
        self.origin = origin
        self.slug = slug
        self.output = []
        self.in_main = False
        self.has_main = False
        self.skipping = None
        self.skip_depth = 0

    def rewrite_url(self, match):
        value = unescape(match[3])
        if not value.startswith("/") or value.startswith("//"):
            return match[0]
        parts = urlsplit(value)
        slug = parts.path.removeprefix("/blog/").rstrip("/")
        if parts.path.startswith("/blog/") and slug in ARTICLES:
            value = f"../{slug}/"
            value += "?" + parts.query if parts.query else ""
            value += "#" + parts.fragment if parts.fragment else ""
        else:
            value = self.origin + value
        return match[1] + match[2] + escape(value, quote=True) + match[2]

    def handle_starttag(self, tag, attrs):
        if self.skipping:
            if tag == self.skipping:
                self.skip_depth += 1
            return
        attributes = dict(attrs)
        if (tag == "footer" and not self.in_main) or (
            tag == "button" and "Copy link to this section" in (
                attributes.get("aria-label"), attributes.get("title")
            )
        ):
            self.skipping = tag
            self.skip_depth = 1
            return
        if tag == "main":
            self.in_main = self.has_main = True
        if tag == "link":
            relations = (attributes.get("rel") or "").lower().split()
            if "preload" in relations or "modulepreload" in relations:
                return
            if "stylesheet" in relations:
                self.output.append(shared_css(attributes["href"], self.source, self.origin, self.assets))
                return
        # Preserve raw SVG attribute casing and all article markup.
        self.output.append(URL_ATTRIBUTE.sub(self.rewrite_url, self.get_starttag_text()))
        if tag == "body":
            original = escape(f"{self.origin}/blog/{self.slug}", quote=True)
            self.output.append(
                '<div style="display:flex;flex-wrap:wrap;justify-content:space-between;'
                'gap:8px 24px;padding:12px 20px;background:#111827;color:#e5e7eb;'
                'border-bottom:1px solid #374151;font:14px/1.5 system-ui,sans-serif">'
                '<a href="https://chimericlabs.xyz/research.html" '
                'style="color:#93c5fd;text-decoration:underline">← Chimeric Labs Research</a>'
                f'<a href="{original}" style="color:#d1d5db;text-decoration:underline">'
                'First published on eth2quickstart.com</a></div>'
            )

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if self.skipping:
            if tag == self.skipping:
                self.skip_depth -= 1
                if not self.skip_depth:
                    self.skipping = None
            return
        if tag == "main":
            self.in_main = False
        self.output.append(f"</{tag}>")

    def handle_data(self, data):
        if not self.skipping:
            self.output.append(data)

    def handle_entityref(self, name):
        self.handle_data(f"&{name};")

    def handle_charref(self, name):
        self.handle_data(f"&#{name};")

    def handle_comment(self, data):
        self.handle_data(f"<!--{data}-->")

    def handle_decl(self, decl):
        self.handle_data(f"<!{decl}>")


def mirror(source, origin, out):
    for slug, expected in ARTICLES.items():
        page = fetch(source_url(source, f"/blog/{slug}")).decode("utf-8")
        # Next.js hydration is unnecessary because the article is server-rendered.
        page = re.sub(r"<script\b[^>]*>.*?</script\s*>", "", page, flags=re.I | re.S)
        title = re.search(r"<title\b[^>]*>(.*?)</title\s*>", page, re.I | re.S)
        if not title or not all(text.casefold() in unescape(title[1]).casefold() for text in expected):
            raise ValueError(f"{slug}: <title> must contain {expected!r}")
        # Upstream uses both header and nav wrappers for its site menu.
        page = re.sub(
            r"<(header|nav)\b[^>]*>.*?</\1\s*>",
            lambda match: "" if "Open menu" in match[0] and not re.search(
                r'''\bid\s*=\s*["']article-top["']''', match[0], re.I
            ) else match[0],
            page, flags=re.I | re.S,
        )
        parser = ArticleMirror(source, origin, slug, out / "assets")
        parser.feed(page)
        parser.close()
        if not parser.has_main:
            raise ValueError(f"{slug}: page has no <main>")
        destination = out / slug / "index.html"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text("".join(parser.output), encoding="utf-8")
        print(f"Mirrored {slug} -> {destination}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="https://eth2quickstart.com")
    parser.add_argument("--origin", default="https://eth2quickstart.com")
    parser.add_argument("--out", type=Path, default=Path("_site/research/eth2"))
    args = parser.parse_args()
    try:
        mirror(args.source, args.origin.rstrip("/"), args.out)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Mirror failed: {error}\n")


if __name__ == "__main__":
    main()
