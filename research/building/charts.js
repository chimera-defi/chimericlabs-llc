/* Commits by project (donut) and commits per month against the before-AI baseline (bars).
   Reads charts-data.json, which scripts/build_building_page.py derives from research/data/.
   Use:  <div id="donut"></div><div id="bars"></div>
         <script src="/research/building/charts.js"></script>
         <script>ChimericCharts.load("/research/building/charts-data.json", {donut: "donut", bars: "bars"})</script>
   Colours come from the design-system CSS variables (--data-1.. , --color-divider, --ds-muted) with
   fallbacks, text uses currentColor, so light and dark both work. No dependencies. */
(function () {
  var NS = "http://www.w3.org/2000/svg";
  var MON = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(" ");
  function el(tag, attrs, parent) {
    var e = document.createElementNS(NS, tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  function svg(parent, vb, label) {
    var s = el("svg", { viewBox: vb, role: "img", "aria-label": label }, parent);
    s.style.cssText = "display:block;width:100%;height:auto;max-width:" + (vb.split(" ")[2] > 300 ? "420px" : "260px");
    return s;
  }
  function text(parent, x, y, str, anchor, size) {
    var t = el("text", { x: x, y: y, "text-anchor": anchor || "start", fill: "currentColor" }, parent);
    t.setAttribute("font-size", size || 11);
    t.textContent = str;
    return t;
  }
  var PAL = ["#e07a5f", "#3d9bd1", "#7cb518", "#d4a017", "#9b6bd1", "#2ec4b6", "#d1558a", "#8d99ae", "#f4a261", "#5b8c5a", "#b0b0c0", "#6c6f85"];
  function colour(c, i) {  // keep the page's own --data-N when it defines it, else a fixed palette
    var m = /^var\((--data-(\d+))\)$/.exec(c);
    if (m) return "var(" + m[1] + ", " + PAL[(+m[2] - 1) % 12] + ")";
    var o = /^var\((--[\w-]+)\)$/.exec(c);
    return o ? "var(" + o[1] + ", " + (/low/.test(o[1]) ? "#6c6f85" : "#b0b0c0") + ")" : c;
  }
  function fmt(n) { return n.toLocaleString("en-US"); }

  function donut(host, d) {
    var total = d.total, pct = d.donut.map(function (s) { return (100 * s.n / total).toFixed(1); });
    var top = d.donut.slice().sort(function (a, b) { return b.n - a.n; }).slice(0, 3).map(function (s) {
      return s.label + " " + (100 * s.n / total).toFixed(1) + "%"; });
    var wrap = document.createElement("div");
    wrap.style.cssText = "display:grid;gap:1.5rem;justify-items:center";
    host.appendChild(wrap);
    var s = svg(wrap, "0 0 200 200", "Commits by project since October 2025, " + fmt(total) + " in all. Largest: " + top.join(", ") + ".");
    var g = el("g", { transform: "rotate(-90 100 100)" }, s), cum = 0;
    d.donut.forEach(function (sl) {
      var a = Math.round(1000 * cum / total); cum += sl.n;
      var len = Math.max(Math.round(1000 * cum / total) - a - 3, 1);
      var c = el("circle", { cx: 100, cy: 100, r: 70, fill: "none", "stroke-width": 36, pathLength: 1000,
        "stroke-dasharray": len + " " + (1000 - len), "stroke-dashoffset": -a }, g);
      c.style.stroke = colour(sl.colour);
    });
    text(s, 100, 96, fmt(total), "middle", 22).setAttribute("font-weight", "700");
    text(s, 100, 118, "commits", "middle", 11);
    var ol = document.createElement("ol");
    ol.style.cssText = "list-style:none;padding:0;margin:0;display:grid;gap:.4rem;width:100%";
    d.donut.forEach(function (sl, i) {
      var li = document.createElement("li");
      li.style.cssText = "display:grid;grid-template-columns:1rem 1fr auto;gap:.5rem;align-items:center";
      li.innerHTML = '<i style="width:1rem;height:1rem;border-radius:2px;background:' + colour(sl.colour) + '"></i><span></span><span style="opacity:.75;font-variant-numeric:tabular-nums"></span>';
      li.children[1].textContent = sl.label;
      li.children[2].textContent = fmt(sl.n) + " \u00b7 " + pct[i] + "%";
      ol.appendChild(li);
    });
    wrap.appendChild(ol);
  }

  function bars(host, d) {
    var m = d.months, b = d.before_ai, base = b.commits / b.months;
    var L = 52, R = 56, T = 12, B = 28, W = 420, H = 220;
    var top = Math.ceil(Math.max.apply(null, m.map(function (x) { return x.n; })) / 1000) * 1000;
    var slot = (W - L - R) / m.length;
    function y(v) { return T + (H - T - B) * (1 - v / top); }
    var last = m[m.length - 1];
    var note = last.days < last.days_in_month ? " The last month is partial (" + last.days + " of " + last.days_in_month + " days)." : "";
    var s = svg(host, "0 0 " + W + " " + H, "Commits per month, " + MON[+m[0].month.slice(5) - 1] + " " + m[0].month.slice(0, 4) +
      " to " + MON[+last.month.slice(5) - 1] + " " + last.month.slice(0, 4) + ", from " + fmt(m[0].n) + " to " + fmt(last.n) +
      ". A dashed line at about " + Math.round(base) + " a month marks the " + b.from + "\u2013" + b.to + " average before AI agents." + note);
    for (var t = 0; t <= top; t += 1000) {
      var gl = el("line", { x1: L, x2: W - R, y1: y(t), y2: y(t) }, s);
      gl.style.cssText = "stroke:var(--color-divider,#8884);stroke-width:1";
      text(s, L - 6, y(t) + 4, fmt(t), "end", 10).setAttribute("opacity", ".75");
    }
    m.forEach(function (x, i) {
      var part = x.days < x.days_in_month, bx = L + i * slot + slot * 0.15;
      var r = el("rect", { x: bx, y: y(x.n), width: slot * 0.7, height: y(0) - y(x.n) }, s);
      r.style.cssText = "fill:var(--data-1,#c44);" + (part ? "fill-opacity:.55;stroke:var(--data-1,#c44);stroke-width:1.5;stroke-dasharray:4 3" : "");
      el("title", {}, r).textContent = MON[+x.month.slice(5) - 1] + " " + x.month.slice(0, 4) + ": " + fmt(x.n) + " commits" + (part ? " (partial: " + x.days + " of " + x.days_in_month + " days)" : "");
      if (i % 3 === 0) text(s, bx + slot * 0.35, H - 8, MON[+x.month.slice(5) - 1] + " \u2019" + x.month.slice(2, 4), "middle", 10).setAttribute("opacity", ".75");
    });
    var bl = el("line", { x1: L, x2: W - R, y1: y(base), y2: y(base) }, s);
    bl.style.cssText = "stroke:var(--ds-muted,#888);stroke-width:2;stroke-dasharray:6 4";
    text(s, W - R + 4, y(base) - 4, "\u2248" + Math.round(base) + "/mo", "start", 10);
    var cap = document.createElement("p");
    cap.style.cssText = "margin:.5rem 0 0;font-size:.9em;opacity:.8";
    cap.textContent = "Dashed line: before AI agents (" + b.from + "\u2013" + b.to + ", this GitHub account), about " + Math.round(base) + " commits a month." +
      (note ? " " + MON[+last.month.slice(5) - 1] + " is partial (lighter bar)." : "");
    host.appendChild(cap);
  }

  window.ChimericCharts = {
    render: function (d, ids) {
      if (ids.donut) { var a = document.getElementById(ids.donut); a.textContent = ""; donut(a, d); }
      if (ids.bars) { var b = document.getElementById(ids.bars); b.textContent = ""; bars(b, d); }
    },
    load: function (url, ids) {
      return fetch(url).then(function (r) { return r.json(); }).then(function (d) { window.ChimericCharts.render(d, ids); });
    }
  };
})();
