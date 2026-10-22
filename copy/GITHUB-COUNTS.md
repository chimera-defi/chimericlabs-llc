# GitHub counts behind the homepage band

As of 2026-10-22, counted with `gh` as `chimera-defi`. Public repos only. `copy/` is excluded from the Pages build.

## 36 · Original public repos on GitHub

```bash
gh api --paginate 'users/chimera-defi/repos?type=owner&per_page=100'
```

- 125 public repos: 87 forks, 38 non-fork, 0 archived.
- 2 of the 38 non-fork repos are empty (`size=0`): `coconuts-airdrop`, `univ3Erc20Mapper-`. That leaves **36**.
- `portfolio.html` uses the same filter (`!repo.fork && repo.size > 0`), so its inventory also shows 36.

Not in the 36: org repos. The account is admin of SharedStake, Coinyieldco, skyfire-dao, Coconuts-finance, Sharedtools, sharedstake-infra and Densofi. Those orgs have 15 public non-fork repos. `repos/{r}/commits?author=chimera-defi` finds commits in 6 of them, all SharedStake: SharedStake-ui, Contracts, infra, project-management, api-amplify, stark-airdrop-calc. Counting org repos too would give 42.

## 9 · Outside repos we contributed to

An outside repo is one not owned by `chimera-defi` or any of its orgs. It counts only if work actually landed there: commits on the default branch, or a merged PR.

```bash
gh api -X GET search/commits --paginate -f q='author:chimera-defi -user:chimera-defi'
gh api -X GET search/issues --paginate -f q='author:chimera-defi is:pr is:merged is:public -user:chimera-defi -org:SharedStake -org:Coinyieldco -org:skyfire-dao -org:Coconuts-finance -org:Sharedtools -org:sharedstake-infra -org:Densofi'
```

| Repo | Evidence |
|---|---|
| apeoverflow/densofi | 35 commits, 10 merged PRs (ETHGlobal Taipei build; the repo is under a teammate's account) |
| vfat-io/vfat-tools | 8 commits, 3 merged PRs |
| hundred-finance/hundred-dao-ui | 13 commits (2021) |
| Laser420/DAO_Managed_Vault | 27 commits (hackathon, 2023) |
| Maralena86/sybil-resistant-DAO | 21 commits (hackathon, 2023) |
| desterds/cnc-index | 21 commits (2021) |
| cheerbotme/ethglobalnyc2025 | 18 commits (ETHGlobal NYC 2025) |
| HKUDS/CLI-Anything | 1 merged PR |
| jiayaoqijia/cryptoskill | 1 merged PR |

Excluded from the 9:

- `Degen-Haus/-vfat-tools` and `Alba3k/vfat-tools` are non-fork copies of vfat-tools. They contain the same commit SHAs, so they are not separate contributions.
- PRs that were opened but never merged: banteg/takopi, bekatom/awesome-ethereum, ethereum/clear-signing-erc7730-registry, paradigmxyz/reth, Railway-Wallet/Railway-Wallet, RoboVault/WAGMI_Yield, yearn/ape-tax. That is 12 outside repos with any PR at all.
- GraphQL `repositoriesContributedTo` gives 11 (or 8 when limited to COMMIT and PULL_REQUEST). Don't use it. It only covers recent activity, so it misses vfat-tools, densofi and hundred-finance. It also includes our own SharedStake org repos and counts unmerged PRs.

## Other band numbers

- **4 hackathon wins and finalist places**: these are the 4 cards in `portfolio.html`. GitHub can't verify prizes.
- **4+ production systems shipped**: GitHub can't verify this, so it was left as is.
