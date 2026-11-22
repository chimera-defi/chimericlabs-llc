// Chart explorer for both bench pages; it clones the static SVGs, so without JS the static charts still carry everything.

const tip = document.createElement("div")
tip.id = "tip"
tip.setAttribute("role", "tooltip")
document.body.append(tip)

const showTip = (dot, ev) => {
  tip.textContent = dot.dataset.tip
  tip.style.display = "block"
  const r = dot.getBoundingClientRect()
  let x = (ev?.clientX ?? r.right) + 14
  let y = (ev?.clientY ?? r.top) + 14
  if (x + tip.offsetWidth > innerWidth - 8) x = innerWidth - tip.offsetWidth - 8
  if (y + tip.offsetHeight > innerHeight - 8) y -= tip.offsetHeight + 28
  tip.style.left = `${Math.max(8, x)}px`
  tip.style.top = `${Math.max(8, y)}px`
}
const hideTip = () => { tip.style.display = "none" }
const dotOf = (ev) => ev.target.closest?.("circle[data-tip]")

// One set of listeners covers the static charts and the explorer clones.
document.addEventListener("pointermove", (ev) => { const d = dotOf(ev); d ? showTip(d, ev) : hideTip() })
document.addEventListener("click", (ev) => { const d = dotOf(ev); if (d) showTip(d, ev) })
document.addEventListener("focusin", (ev) => { const d = dotOf(ev); d ? showTip(d) : hideTip() })
// A tap off the dots or a blur hides the tip, or it sticks over the chart on touch screens.
document.addEventListener("pointerdown", (ev) => { if (!dotOf(ev)) hideTip() })
document.addEventListener("focusout", (ev) => { if (dotOf(ev)) hideTip() })
document.addEventListener("keydown", (ev) => { if (ev.key === "Escape") hideTip() })

// Same rule as build_charts.py frontier2, so the redrawn line matches the static chart.
const beats = (q, p) => q !== p && q.x <= p.x && q.y <= p.y && (q.x < p.x || q.y < p.y)
const frontier = (pts, bothLow) => {
  if (bothLow) return new Set(pts.filter((p) => !pts.some((q) => beats(q, p))).map((p) => p.model))
  const on = new Set()
  let best = -1
  let lastX = null
  for (const p of [...pts].sort((a, b) => a.x - b.x || b.y - a.y)) {
    if (p.y > best || (p.y === best && p.x === lastX)) { on.add(p.model); lastX = p.x }
    best = Math.max(best, p.y)
  }
  return on
}

const restyle = (svg, hidden) => {
  const dots = [...svg.querySelectorAll("circle[data-model]")]
  const pts = dots.filter((c) => !hidden.has(c.dataset.model)).map((c) => ({ model: c.dataset.model, x: +c.dataset.x, y: +c.dataset.y, c }))
  const on = frontier(pts, svg.dataset.bothLow === "1")
  for (const c of dots) {
    const best = on.has(c.dataset.model)
    c.toggleAttribute("hidden", hidden.has(c.dataset.model))
    c.setAttribute("class", best ? "pb" : "pd")
    c.setAttribute("r", best ? 9 : 7)
    const state = best ? "on the frontier" : "beaten on this chart"
    for (const k of ["data-tip", "aria-label"]) c.setAttribute(k, c.getAttribute(k).replace(/(on the frontier|beaten on this chart)$/, state))
  }
  for (const t of svg.querySelectorAll("text[data-model]")) {
    t.toggleAttribute("hidden", hidden.has(t.dataset.model))
    t.setAttribute("class", on.has(t.dataset.model) ? "pl" : "pl2")
  }
  const line = pts.filter((p) => on.has(p.model)).sort((a, b) => a.c.cx.baseVal.value - b.c.cx.baseVal.value)
  svg.querySelector(".pf")?.setAttribute("points", line.map((p) => `${p.c.getAttribute("cx")},${p.c.getAttribute("cy")}`).join(" "))
}

for (const ex of document.querySelectorAll(".ex[data-charts]")) {
  const plot = ex.querySelector(".ex-plot")
  const svgs = new Map()
  for (const id of ex.dataset.charts.split(" ")) {
    const src = document.getElementById(id)
    if (!src) continue
    const svg = src.cloneNode(true)
    // Prefix ids so the clone does not collide with the static chart it copies.
    for (const el of [svg, ...svg.querySelectorAll("[id]")]) el.id = `x-${el.id}`
    svg.setAttribute("aria-labelledby", `x-${id}t x-${id}d`)
    svg.dataset.bothLow = (ex.dataset.bothLow ?? "").split(" ").includes(id) ? "1" : "0"
    svg.toggleAttribute("hidden", true)
    plot.append(svg)
    svgs.set(id, svg)
  }
  if (!svgs.size) continue

  const hidden = new Set()
  const chips = ex.querySelector(".ex-chips")
  const models = new Map([...plot.querySelectorAll("circle[data-model]")].map((c) => [c.dataset.model, c.dataset.family]))
  for (const [model, family] of [...models].sort(([a], [b]) => a.localeCompare(b))) {
    const b = document.createElement("button")
    b.type = "button"
    b.className = "btn btn-toggle"
    b.dataset.model = model
    b.dataset.family = family
    b.setAttribute("aria-pressed", "true")
    b.innerHTML = '<span class="dot" aria-hidden="true"></span>'
    b.append(model)
    chips.append(b)
  }
  chips.addEventListener("click", (ev) => {
    const b = ev.target.closest("button[data-model]")
    if (!b) return
    const show = b.getAttribute("aria-pressed") !== "true"
    b.setAttribute("aria-pressed", String(show))
    show ? hidden.delete(b.dataset.model) : hidden.add(b.dataset.model)
    for (const svg of svgs.values()) restyle(svg, hidden)
  })

  const view = () => {
    const pick = ex.querySelector(".ex-views input:checked")?.value
    for (const [id, svg] of svgs) svg.toggleAttribute("hidden", id !== pick)
    hideTip()
  }
  ex.querySelector(".ex-views")?.addEventListener("change", view)
  const colour = ex.querySelector(".ex-colour")
  colour?.addEventListener("change", () => { ex.dataset.colour = colour.value })
  view()
  ex.hidden = false
}
