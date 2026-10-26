# ChimericLabs LLC

Minimal static site for ChimericLabs LLC, published with GitHub Pages.

## Live Site

[GitHub Pages](https://chimera-defi.github.io/chimericlabs-llc/)

## Portfolio References

- https://www.sharedstake.org/
- https://www.sharedtools.org/
- https://github.com/chimera-defi/token-reduce-skill
- https://github.com/chimera-defi/specforge

## Local preview

Open `index.html` directly in a browser, or serve the directory with any static file server.

## Research pages

`research.html` lists our research reports. The DispatchBench page is pulled from the
[bench repo's main branch](https://github.com/chimera-defi/dispatchbench) on every deploy
and daily. To refresh now, run:

```sh
gh workflow run pages.yml -R chimera-defi/chimericlabs-llc
```

Local preview of `/dispatchbench/` needs the report downloaded first:

```sh
mkdir -p dispatchbench
curl -fsSL --retry 3 https://raw.githubusercontent.com/chimera-defi/dispatchbench/main/results/report/page.html -o dispatchbench/index.html
```

Four eth2-quickstart articles are mirrored into `/research/eth2/` on every deploy
and daily, with inlined styles and fonts, links between the articles, and links
back to the originals. Refresh them with
`gh workflow run pages.yml -R chimera-defi/chimericlabs-llc`. For a local preview,
download the articles and serve the site, then open
`http://localhost:8000/research/eth2/ethereum-client-bakeoff/`:

```sh
python3 scripts/mirror_eth2_articles.py --out research/eth2
python3 -m http.server 8000
```

## Deploy

Pushes to `main` deploy through GitHub Actions via `.github/workflows/pages.yml`.
