// Breakout concept mock: all figures, names and terms below are invented placeholders.
// Nothing here talks to a network, a wallet or a market.
const TOKENS = [
  { id: "lv", artist: "Lune Vega", initials: "LV", ticker: "LUNE", album: "Saltwater Hymns", release: "Mar 2027", share: 15, price: 2, raised: 84000, goal: 120000 },
  { id: "ns", artist: "Nia Sol", initials: "NS", ticker: "NIA", album: "Velvet Hours", release: "May 2027", share: 20, price: 5, raised: 212000, goal: 250000 },
  { id: "gm", artist: "Glass Mile", initials: "GM", ticker: "GLSS", album: "Northbound", release: "Feb 2027", share: 10, price: 1, raised: 41000, goal: 60000 },
  { id: "ko", artist: "Kofi Ostrander", initials: "KO", ticker: "KOFI", album: "Lagos Lowlights (EP)", release: "Jan 2027", share: 12, price: 0.5, raised: 9000, goal: 40000 },
];
const MARKETS = [
  { id: "lv", artist: "Lune Vega", initials: "LV", genre: "Dream pop", question: "Passes 1M monthly listeners by Jun 30, 2027?", yes: 34, volume: "$182K", date: "Jun 30, 2027" },
  { id: "ko", artist: "Kofi Ostrander", initials: "KO", genre: "Afro-house", question: "Enters a top-100 chart before 2028?", yes: 12, volume: "$64K", date: "Dec 31, 2027" },
  { id: "gm", artist: "Glass Mile", initials: "GM", genre: "Indie rock", question: "Sells out a 2,000-cap headline show by spring?", yes: 61, volume: "$97K", date: "Apr 1, 2027" },
  { id: "ns", artist: "Nia Sol", initials: "NS", genre: "R&B", question: "Signs with a major label in 2027?", yes: 47, volume: "$231K", date: "Dec 31, 2027" },
];
const CTX = [
  { id: "songs", label: "Song vectors", meta: "48K tracks" },
  { id: "taste", label: "Artist taste", meta: "312 liked songs" },
  { id: "session", label: "This session", meta: "24 stems · 9 MIDI" },
  { id: "brand", label: "Brand assets", meta: "3 shoots · 2 campaigns" },
];
// Each module: label, retrieved references [title, source, context id, match] and suggestions [title, detail, target].
const STUDIO = {
  composition: {
    label: "Composition",
    refs: [
      ["Halcyon Drift, Mara Ione", "Liked song", "taste", "0.91"],
      ["Low Tide Choir, The Pale Rooms", "Song vectors · chord + form", "songs", "0.87"],
      ["“Saltwater” moodboard", "Photo shoot · cold blues, open coast", "brand", "0.74"],
    ],
    sugs: [
      ["Lift the last chorus a minor third", "7 of your 12 closest references modulate up for the final chorus. Try A♭ → B for the last 8 bars.", "MIDI · Lead vox guide, Keys"],
      ["Borrow the iv chord in bar 12", "A D♭m in the bridge gives the bittersweet turn your liked songs lean on.", "MIDI · Keys"],
      ["Shorten the intro to 8 bars", "Matched references reach the first vocal by 0:14; yours enters at 0:31.", "Arrangement · Intro"],
    ],
  },
  production: {
    label: "Production",
    refs: [
      ["Pad + vox stems (current)", "This session", "session", "—"],
      ["Glasswork, Ondine Park", "Song vectors · timbre", "songs", "0.89"],
      ["“Saltwater” moodboard", "Photo shoot · sparse, reverb-heavy", "brand", "0.71"],
    ],
    sugs: [
      ["Layer a tape-saturated pad under the verse", "Soft-synth pad into a saturator at 30% dry/wet. Matches the warm-pad cluster in your references.", "Track · Pad 2 (new)"],
      ["Swap the clap for a rim and snap stack", "Your most-saved songs use drier, shorter backbeats at around 90 BPM.", "Drum rack · C1"],
      ["Add a reversed vocal swell into the chorus", "Two bars, from the “undertow” ad-lib. Fits the coastal, airy brand world.", "Audio · Vox FX"],
    ],
  },
  mixing: {
    label: "Mixing",
    refs: [
      ["Halcyon Drift, Mara Ione", "Reference mix · spectral match", "taste", "0.88"],
      ["Full session (current)", "This session · masking analysis", "session", "—"],
      ["Northern Static, Vell", "Song vectors · stereo image", "songs", "0.82"],
    ],
    sugs: [
      ["Cut 280 Hz on the pad bus by 3 dB", "The pads mask the lead vocal here; reference mixes leave this band clear.", "EQ · Pad bus"],
      ["Sidechain bass to kick, 4:1, 40 ms release", "Low end is 2.1 dB hotter than your reference average and smears the kick.", "Compressor · Bass"],
      ["Widen backing vocals to 140%", "References carry backing vocals wide and the lead dead centre.", "Utility · BV bus"],
    ],
  },
  mastering: {
    label: "Mastering",
    refs: [
      ["Reference set average", "Artist taste · −8.7 LUFS, −1 dBTP", "taste", "0.93"],
      ["Velvet Hours masters", "Song vectors · same genre cluster", "songs", "0.84"],
      ["Spring campaign brief", "Brand assets · short-video-first rollout", "brand", "0.69"],
    ],
    sugs: [
      ["Target −9 LUFS integrated", "The current bounce sits at −12.4 LUFS. Set the limiter ceiling to −1 dBTP and add 3.4 dB of gain.", "Master · Limiter"],
      ["Gentle 1.5 dB high shelf at 10 kHz", "Adds the air your reference masters share without harshening the sibilance.", "Master · EQ"],
      ["Export a 15 s vertical-video cut", "The campaign brief puts short video first. Suggested loop: 1:02–1:17, the chorus hook.", "Export · Clip"],
    ],
  },
};
// Resolution source per milestone option, in the same order as the select (placeholder providers).
const SOURCES = ["a streaming-stats data provider", "a public chart archive", "a ticketing partner's sell-through report", "a public label announcement, checked by the oracle"];
const WALLETS = ["0x3f…a2", "0x9c…71", "mara-demo.eth", "0x14…de", "vinyl-demo.eth", "0xb0…5e"];
const SCENARIOS = [100000, 500000, 2000000];
const TICK_MS = 2200;

const usd = (n) => (n >= 1e6 ? `$${(n / 1e6).toFixed(n % 1e6 ? 1 : 0)}M` : n >= 1e3 ? `$${Math.round(n / 1e3)}K` : `$${n.toFixed(2)}`);
const money = (n) => `$${n.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
const $ = (selector, root = document) => root.querySelector(selector);

const el = (tag, className, text, attrs = {}) => {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  for (const [name, value] of Object.entries(attrs)) node.setAttribute(name, value);
  return node;
};
const tag = (text, extra = "tag-neutral") => el("span", `tag ${extra}`, text);
const button = (text, className, onClick, attrs = {}) => {
  const node = el("button", className, text, { type: "button", ...attrs });
  node.addEventListener("click", onClick);
  return node;
};
// A re-render replaces nodes, so hand keyboard focus back to the same control.
const keepFocus = (render) => {
  const key = document.activeElement?.dataset?.focus;
  render();
  if (key) $(`[data-focus="${key}"]`)?.focus();
};
const setPressed = (buttons, active) => {
  for (const node of buttons) node.setAttribute("aria-pressed", String(node === active));
};

const state = { tokenId: "lv", scenario: 1, raised: Object.fromEntries(TOKENS.map((t) => [t.id, t.raised])), flash: null, feed: [], marketId: "lv", side: "yes", studioTab: "composition", applied: new Set(), ctx: new Set(CTX.map((c) => c.id)), previewing: null, extra: {}, holdings: {}, positions: {} };
const controller = new AbortController();
const { signal } = controller;

// ---- Launchpad ----
const tokenList = $("#token-list");
const investAmount = $("#inv-amount");
const investReadout = $("#inv-readout");
const investCta = $("#inv-cta");
const investDone = $("#inv-done");
const scenarioButtons = [];

const renderTokens = () => keepFocus(() => {
  tokenList.replaceChildren();
  for (const t of TOKENS) {
    const raised = state.raised[t.id];
    const pct = Math.round((raised / t.goal) * 100);
    const card = el("article", "card");
    if (t.id === state.tokenId) card.classList.add("card-selected");
    if (t.id === state.flash) card.classList.add("card-flash");

    const head = el("div", "ds-row");
    head.append(el("strong", "", t.artist), tag(`$${t.ticker}`), tag(`${t.share}% of profits`, "tag-accent"));
    if (t.id === state.flash) head.append(el("span", "ds-num ds-muted", `+$${state.flashAmount.toLocaleString("en-US")}`));

    const meta = el("div", "ds-meta ds-num");
    for (const text of [`$${t.price.toFixed(2)} / token`, `${usd(raised)} of ${usd(t.goal)}`, `${pct}% funded`]) meta.append(el("span", "", text));
    const bar = el("div", "ds-bar", undefined, { role: "img", "aria-label": `${pct}% funded` });
    const fill = el("i");
    fill.style.setProperty("--w", `${pct}%`);
    bar.append(fill);

    const body = el("div");
    body.append(head, el("p", "card-body", `${t.album} · releases ${t.release}`), meta, bar);
    const listing = el("div", "ds-listing");
    listing.append(el("div", "ds-avatar", t.initials, { "aria-hidden": "true" }), body);

    const actions = el("div", "ds-row");
    actions.append(button("Invest", "btn btn-primary", () => selectToken(t.id), { "aria-label": `Invest in ${t.artist} (simulation)`, "data-focus": `tok-${t.id}` }));
    card.append(listing, actions);
    tokenList.append(card);
  }
});

const renderInvest = () => {
  const t = TOKENS.find((item) => item.id === state.tokenId);
  const amount = Math.max(0, Number(investAmount.value) || 0);
  const supply = t.goal / t.price;
  const tokens = amount / t.price;
  const fraction = tokens / supply;
  const pool = SCENARIOS[state.scenario] * (t.share / 100);
  $("#inv-title").textContent = `${t.artist} · ${t.album}`;
  $("#inv-terms").textContent = `${t.share}% of net album profits, split pro rata across ${Math.round(supply).toLocaleString("en-US")} tokens (placeholder terms).`;
  const rows = [
    ["Tokens", Math.round(tokens).toLocaleString("en-US")],
    ["Your share of holder pool", `${(fraction * 100).toFixed(3)}%`],
    ["Holder pool", usd(pool)],
    ["Your payout", money(pool * fraction)],
  ];
  investReadout.replaceChildren();
  for (const [label, value] of rows) {
    const dd = el("dd", label === "Your payout" ? "ds-final" : "", value);
    investReadout.append(el("dt", "", label), dd);
  }
  const funded = state.raised[t.id] >= t.goal;
  investCta.disabled = funded;
  investCta.textContent = funded ? "Raise closed · fully funded" : `Simulate · $${amount.toLocaleString("en-US")}`;
  const held = state.holdings[t.id];
  $("#inv-holding").textContent = held ? `${held.toLocaleString("en-US", { maximumFractionDigits: 1 })} $${t.ticker}` : "None";
};

const selectToken = (id) => {
  state.tokenId = id;
  investDone.hidden = true;
  renderTokens();
  renderInvest();
};

for (const [index, label] of ["$100K", "$500K", "$2M"].entries()) {
  const node = button(label, "btn btn-secondary btn-toggle", () => {
    state.scenario = index;
    setPressed(scenarioButtons, node);
    renderInvest();
  });
  scenarioButtons.push(node);
  $("#inv-scenarios").append(node);
}
setPressed(scenarioButtons, scenarioButtons[state.scenario]);

for (const node of document.querySelectorAll("[data-add-inv]")) {
  node.addEventListener("click", () => {
    investAmount.value = (Number(investAmount.value) || 0) + Number(node.dataset.addInv);
    investDone.hidden = true;
    renderInvest();
  }, { signal });
}
investAmount.addEventListener("input", () => { investDone.hidden = true; renderInvest(); }, { signal });
investCta.addEventListener("click", () => {
  const t = TOKENS.find((item) => item.id === state.tokenId);
  const amount = Math.max(0, Number(investAmount.value) || 0);
  if (!amount || state.raised[t.id] >= t.goal) return;
  state.holdings[t.id] = (state.holdings[t.id] || 0) + amount / t.price;
  investDone.hidden = false;
  renderInvest();
}, { signal });

// ---- Live feed ----
const feedList = $("#feed");
const renderFeed = () => {
  feedList.replaceChildren();
  for (const [i, ev] of state.feed.entries()) {
    const li = el("li");
    li.style.setProperty("--i", i);
    const ago = Math.floor((Date.now() - ev.at) / 1000);
    li.append(el("span", "", `${ev.who} → $${ev.ticker}`), el("span", "ds-when", `$${ev.amount.toLocaleString("en-US")} · ${ago < 3 ? "just now" : `${ago}s ago`}`));
    feedList.append(li);
  }
};

const tick = () => {
  const t = TOKENS[Math.floor(Math.random() * TOKENS.length)];
  const amount = Math.round((50 + Math.random() * 1400) / 10) * 10;
  state.raised[t.id] = Math.min(t.goal, state.raised[t.id] + amount);
  state.flash = t.id;
  state.flashAmount = amount;
  state.feed = [{ who: WALLETS[Math.floor(Math.random() * WALLETS.length)], ticker: t.ticker, amount, at: Date.now() }, ...state.feed].slice(0, 4);
  renderTokens();
  renderFeed();
  if (t.id === state.tokenId) renderInvest();
  setTimeout(() => { state.flash = null; renderTokens(); }, 900);
};

state.feed = [
  { who: "mara-demo.eth", ticker: "LUNE", amount: 500, at: Date.now() - 41000 },
  { who: "0x9c…71", ticker: "NIA", amount: 1200, at: Date.now() - 96000 },
];
renderTokens();
renderInvest();
renderFeed();

// The ticker runs only when motion is allowed, the section is on screen, the tab is visible and the user has not paused it.
const motionQuery = matchMedia("(prefers-reduced-motion: reduce)");
const pauseButton = $("#feed-toggle");
let timer = 0;
let onScreen = false;
let paused = motionQuery.matches;
const syncTicker = () => {
  clearInterval(timer);
  const running = !paused && onScreen && !document.hidden;
  if (running) timer = setInterval(tick, TICK_MS);
  pauseButton.setAttribute("aria-pressed", String(paused));
  pauseButton.textContent = paused ? "Resume live feed" : "Pause live feed";
};
pauseButton.addEventListener("click", () => { paused = !paused; syncTicker(); }, { signal });
document.addEventListener("visibilitychange", syncTicker, { signal });
motionQuery.addEventListener("change", (e) => { paused = e.matches; syncTicker(); }, { signal });
const observer = new IntersectionObserver(([entry]) => { onScreen = entry.isIntersecting; syncTicker(); });
observer.observe($("#invest"));
syncTicker();

// ---- Creator form ----
const modeButtons = [...document.querySelectorAll("[data-mode]")];
const forms = { token: $("#form-token"), market: $("#form-market") };
const listed = $("#listed");
const setMode = (mode) => {
  listed.hidden = true;
  forms.token.hidden = mode !== "token";
  forms.market.hidden = mode !== "market";
  setPressed(modeButtons, modeButtons.find((b) => b.dataset.mode === mode));
};
for (const node of modeButtons) node.addEventListener("click", () => setMode(node.dataset.mode), { signal });
setMode("token");

const goalInput = $("#goal");
const shareInput = $("#share");
const consequence = $("#consequence");
const renderConsequence = () => {
  const goal = Number(goalInput.value) || 0;
  consequence.textContent = `You receive ${usd(goal * 0.95)} after the 5% launch fee (placeholder). Holders get ${shareInput.value || 0}% of net album profits, paid each royalty period for 5 years (placeholder).`;
};
goalInput.addEventListener("input", renderConsequence, { signal });
shareInput.addEventListener("input", renderConsequence, { signal });
renderConsequence();
for (const node of document.querySelectorAll("[data-submit]")) {
  node.addEventListener("click", () => {
    forms.token.hidden = true;
    forms.market.hidden = true;
    listed.hidden = false;
    const token = node.dataset.submit === "token";
    $("#listed-title").textContent = token ? "Token launch queued for review" : "Market queued for listing";
    $("#listed-body").textContent = token
      ? "In the concept, the revenue-share agreement is drafted with the artist and the trustee; once signed, the token goes live on the launchpad."
      : "In the concept, the data source is verified first, then the Yes/No pool is deployed.";
  }, { signal });
}
$("#listed-reset").addEventListener("click", () => setMode(modeButtons.find((b) => b.getAttribute("aria-pressed") === "true")?.dataset.mode ?? "token"), { signal });

const milestone = $("#m-milestone");
const renderSource = () => { $("#m-source").textContent = SOURCES[milestone.selectedIndex] ?? SOURCES[0]; };
milestone.addEventListener("change", renderSource, { signal });
renderSource();

// ---- Studio mock ----
const studioTabs = $("#studio-tabs");
const studioList = $("#studio-list");
const studioCtx = $("#studio-ctx");
const studioRefs = $("#studio-refs");
const studioPrompt = $("#studio-prompt");
const studioButtons = [];
const renderStudio = () => keepFocus(() => {
  const mod = STUDIO[state.studioTab];
  const refs = mod.refs.filter(([, , ctx]) => state.ctx.has(ctx));
  $("#refs-label").textContent = `Retrieved for ${mod.label}`;
  $("#sugs-label").textContent = `Suggestions · ${mod.label}`;
  studioPrompt.placeholder = `Ask the ${mod.label.toLowerCase()} agent…`;

  studioCtx.replaceChildren();
  for (const c of CTX) {
    const on = state.ctx.has(c.id);
    const node = button("", `btn ${on ? "btn-secondary" : "btn-ghost"} bk-ctx`, () => {
      if (on) state.ctx.delete(c.id); else state.ctx.add(c.id);
      renderStudio();
    }, { "aria-pressed": String(on), "data-focus": `ctx-${c.id}` });
    node.append(el("span", "", c.label), el("span", "ds-muted", c.meta));
    studioCtx.append(node);
  }

  studioRefs.replaceChildren();
  for (const [title, src, , match] of refs) {
    const row = el("div", "bk-ref");
    const copy = el("div", "", title);
    copy.append(el("small", "", src));
    row.append(copy, el("span", "bk-match", match, { "aria-label": match === "—" ? "no match score" : `match ${match}` }));
    studioRefs.append(row);
  }
  $("#studio-norefs").hidden = refs.length > 0;

  studioList.replaceChildren();
  for (const [i, [title, detail, target]] of [...mod.sugs, ...(state.extra[state.studioTab] || [])].entries()) {
    const key = `${state.studioTab}:${i}`;
    const applied = state.applied.has(key);
    const previewing = state.previewing === key;
    const copy = el("div");
    copy.style.flex = "1 1 220px";
    copy.append(el("strong", "", title), el("p", "card-body", detail), el("div", "ds-muted", `→ ${target}`));
    const actions = el("div", "ds-row");
    if (applied) actions.append(tag("Applied (mock)", "tag-accent"));
    actions.append(
      button(applied ? "Undo" : "Apply", `btn ${applied ? "btn-secondary" : "btn-primary"}`, () => {
        if (applied) state.applied.delete(key); else state.applied.add(key);
        renderStudio();
      }, { "data-focus": `studio-${key}` }),
      button(previewing ? "Stop" : "Preview", "btn btn-ghost", () => {
        state.previewing = previewing ? null : key;
        renderStudio();
      }, { "aria-pressed": String(previewing), "data-focus": `preview-${key}` }),
    );
    const row = el("div", "ds-suggest");
    row.append(copy, actions);
    studioList.append(row);
  }
});
$("#studio-ask").addEventListener("submit", (e) => {
  e.preventDefault();
  const q = studioPrompt.value.trim();
  if (!q) return;
  const n = STUDIO[state.studioTab].refs.filter(([, , ctx]) => state.ctx.has(ctx)).length;
  const item = [q[0].toUpperCase() + q.slice(1), `Scripted draft from ${n} retrieved reference${n === 1 ? "" : "s"}. Review before applying.`, "Pending · new clip"];
  state.extra[state.studioTab] = [...(state.extra[state.studioTab] || []), item];
  studioPrompt.value = "";
  renderStudio();
}, { signal });
for (const name of Object.keys(STUDIO)) {
  const node = button(STUDIO[name].label, "btn btn-secondary btn-toggle", () => {
    state.studioTab = name;
    state.previewing = null;
    setPressed(studioButtons, node);
    renderStudio();
  });
  studioButtons.push(node);
  studioTabs.append(node);
}
setPressed(studioButtons, studioButtons[0]);
renderStudio();

// ---- Prediction markets (simulated) ----
const marketList = $("#market-list");
const mktAmount = $("#mkt-amount");
const mktReadout = $("#mkt-readout");
const mktDone = $("#mkt-done");
const sideButtons = [];
const renderMarkets = () => keepFocus(() => {
  marketList.replaceChildren();
  for (const m of MARKETS) {
    const card = el("article", `card${m.id === state.marketId ? " card-selected" : ""}`);
    const head = el("div", "ds-row");
    head.append(el("strong", "", m.artist), tag(m.genre));
    const meta = el("div", "ds-meta ds-num");
    for (const text of [`${m.volume} vol`, `Resolves ${m.date}`, `${m.yes}% chance`]) meta.append(el("span", "", text));
    const bar = el("div", "ds-bar", undefined, { role: "img", "aria-label": `${m.yes}% chance` });
    const fill = el("i");
    fill.style.setProperty("--w", `${m.yes}%`);
    bar.append(fill);
    const body = el("div");
    body.append(head, el("p", "card-body", m.question), meta, bar);
    const listing = el("div", "ds-listing");
    listing.append(el("div", "ds-avatar", m.initials, { "aria-hidden": "true" }), body);
    const actions = el("div", "ds-cols-2");
    actions.append(
      button(`Yes ${m.yes}¢`, "btn btn-primary", () => selectMarket(m.id, "yes"), { "data-focus": `yes-${m.id}` }),
      button(`No ${100 - m.yes}¢`, "btn btn-secondary", () => selectMarket(m.id, "no"), { "data-focus": `no-${m.id}` }),
    );
    card.append(listing, actions);
    marketList.append(card);
  }
});
const renderTrade = () => {
  const m = MARKETS.find((item) => item.id === state.marketId);
  const price = state.side === "yes" ? m.yes : 100 - m.yes;
  const amount = Math.max(0, Number(mktAmount.value) || 0);
  const shares = price ? amount / (price / 100) : 0;
  $("#mkt-title").textContent = m.artist;
  $("#mkt-question").textContent = m.question;
  $("#mkt-yes").textContent = `Yes · ${m.yes}¢`;
  $("#mkt-no").textContent = `No · ${100 - m.yes}¢`;
  setPressed(sideButtons, sideButtons[state.side === "yes" ? 0 : 1]);
  const rows = [
    ["Avg price", `${price}¢`],
    ["Shares", shares.toFixed(1)],
    ["To artist (1%)", money(amount * 0.01)],
    [`Payout if ${state.side}`, money(shares)],
  ];
  mktReadout.replaceChildren();
  for (const [label, value] of rows) mktReadout.append(el("dt", "", label), el("dd", label.startsWith("Payout") ? "ds-final" : "", value));
  $("#mkt-cta").textContent = `Simulate ${state.side === "yes" ? "Yes" : "No"} · $${amount.toLocaleString("en-US")}`;
  const pos = state.positions[m.id];
  $("#mkt-position").textContent = pos ? `${pos.yes.toFixed(1)} Yes · ${pos.no.toFixed(1)} No` : "None";
  $("#mkt-sell").disabled = !pos;
};
const selectMarket = (id, side) => {
  state.marketId = id;
  state.side = side;
  mktDone.hidden = true;
  renderMarkets();
  renderTrade();
};
sideButtons.push($("#mkt-yes"), $("#mkt-no"));
$("#mkt-yes").addEventListener("click", () => { state.side = "yes"; mktDone.hidden = true; renderTrade(); }, { signal });
$("#mkt-no").addEventListener("click", () => { state.side = "no"; mktDone.hidden = true; renderTrade(); }, { signal });
for (const node of document.querySelectorAll("[data-add-mkt]")) {
  node.addEventListener("click", () => { mktAmount.value = (Number(mktAmount.value) || 0) + Number(node.dataset.addMkt); renderTrade(); }, { signal });
}
mktAmount.addEventListener("input", () => { mktDone.hidden = true; renderTrade(); }, { signal });
$("#mkt-cta").addEventListener("click", () => {
  const m = MARKETS.find((item) => item.id === state.marketId);
  const price = state.side === "yes" ? m.yes : 100 - m.yes;
  const amount = Math.max(0, Number(mktAmount.value) || 0);
  if (!amount || !price) return;
  const pos = state.positions[m.id] || { yes: 0, no: 0 };
  pos[state.side] += amount / (price / 100);
  state.positions[m.id] = pos;
  mktDone.hidden = false;
  renderTrade();
}, { signal });
$("#mkt-sell").addEventListener("click", () => {
  delete state.positions[state.marketId];
  mktDone.hidden = true;
  renderTrade();
}, { signal });
renderMarkets();
renderTrade();

// Keep listeners across the back-forward cache; only the ticker stops while the page is hidden.
addEventListener("pagehide", () => clearInterval(timer), { signal });
addEventListener("pageshow", (e) => { if (e.persisted) syncTicker(); }, { signal });
