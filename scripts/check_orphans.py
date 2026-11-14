#!/usr/bin/env python3
"""Fail when a published page cannot be reached by following links from the home page.

Usage: python3 scripts/check_orphans.py SITE_DIR [--report]
SITE_DIR is the built site (CI's _site). A page is any .html file that is a full document (has <html or
<title); fragments that other pages paste in at build time are not pages. --report prints every page with
the pages that link to it.
"""
import argparse
import pathlib
import sys
from html.parser import HTMLParser
from urllib.parse import unquote, urljoin, urlsplit

SITE_HOSTS = {"chimericlabs.xyz", "www.chimericlabs.xyz"}
GH_PAGES_PREFIX = "chimera-defi.github.io/chimericlabs-llc"


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.found = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("a", "area", "link") and a.get("href"):
            if tag != "link" or a.get("rel") in ("alternate", "next", "prev"):
                self.found.append(a["href"])
        if tag in ("iframe", "frame") and a.get("src"):
            self.found.append(a["src"])


def is_page(path):
    head = path.read_text(errors="ignore")[:4000].lower()
    return "<html" in head or "<title" in head


def resolve(root, page, href):
    """Map an href on `page` to a site path like 'research/sha256/index.html', or None if off-site."""
    base = "https://chimericlabs.xyz/" + page.relative_to(root).as_posix()
    url = urlsplit(urljoin(base, href.strip()))
    host_path = url.netloc + url.path
    if url.netloc in SITE_HOSTS:
        path = url.path
    elif host_path.startswith(GH_PAGES_PREFIX):
        path = host_path[len(GH_PAGES_PREFIX):]
    else:
        return None
    path = unquote(path).lstrip("/")
    if path == "" or path.endswith("/"):
        path += "index.html"
    target = root / path
    if not target.exists() and (root / path / "index.html").exists():
        target = root / path / "index.html"
    return target.relative_to(root).as_posix() if target.exists() else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("site")
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()
    root = pathlib.Path(args.site).resolve()
    pages = {p.relative_to(root).as_posix() for p in root.rglob("*.html") if is_page(p)}
    linked_from = {p: set() for p in pages}
    seen, queue = {"index.html"}, ["index.html"]
    while queue:
        page = queue.pop()
        parser = Links()
        parser.feed((root / page).read_text(errors="ignore"))
        for href in parser.found:
            target = resolve(root, root / page, href)
            if target in pages:
                linked_from[target].add(page)
                if target not in seen:
                    seen.add(target)
                    queue.append(target)
    if args.report:
        for p in sorted(pages):
            print(f"{p}  <-  {', '.join(sorted(linked_from[p])) or '(nothing)'}")
    orphans = sorted(pages - seen)
    for p in orphans:
        print(f"ORPHAN: /{p} is not reachable from the home page; link it from research.html")
    print(f"{len(seen)} of {len(pages)} pages reachable from the home page")
    sys.exit(1 if orphans else 0)


if __name__ == "__main__":
    main()
