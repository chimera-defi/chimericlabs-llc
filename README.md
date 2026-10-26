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

## Deploy

Pushes to `main` deploy through GitHub Actions via `.github/workflows/pages.yml`.
