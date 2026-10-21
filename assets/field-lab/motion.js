/* Field Lab v3 motion: first-visit intro overlay and the telemetry-band particle field. */
(() => {
  const root = document.documentElement;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Intro. The inline head script sets html.intro; the overlay is empty (all glyphs are CSS content).
  if (root.classList.contains('intro')) {
    const o = document.createElement('div');
    o.className = 'fl-intro';
    o.setAttribute('aria-hidden', 'true');
    o.innerHTML = '<i class="gv"></i><i class="gh"></i><i class="hint"></i>';
    document.body.append(o);
    const end = () => { o.remove(); root.classList.remove('intro'); };
    o.addEventListener('animationend', (e) => e.animationName === 'fl-out' && end());
    for (const t of ['pointerdown', 'keydown']) addEventListener(t, end, { once: true });
  }

  // Particle field: mint squares drift right, ~14% are hot accent squares with a pulsing ring.
  const cv = document.querySelector('.site-band canvas');
  if (!cv) return;
  const cx = cv.getContext('2d'), band = cv.parentElement;
  let P = [], W, H, col, last = 0, raf = 0;
  const token = (n) => getComputedStyle(root).getPropertyValue(n).trim();

  function size() {
    const dpr = Math.min(2, devicePixelRatio || 1), r = cv.getBoundingClientRect();
    W = r.width; H = r.height;
    cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
    cx.setTransform(dpr, 0, 0, dpr, 0, 0);
    col = { mint: token('--band-mint'), acc: token('--accent'), line: token('--band-line') };
    P = Array.from({ length: Math.max(40, Math.min(150, Math.round(W * H / 7000))) }, () => ({
      x: Math.random() * W, y: Math.random() * H, vx: 12 + Math.random() * 38,
      s: 2 + Math.floor(Math.random() * 3), hot: Math.random() < .14, ph: Math.random() * 6,
    }));
  }

  function draw(t) {
    cx.clearRect(0, 0, W, H);
    cx.globalAlpha = .28; cx.fillStyle = col.line;
    for (let x = 0; x < W; x += 80) cx.fillRect(x, 0, 1, H);
    for (const p of P) {
      cx.fillStyle = p.hot ? col.acc : col.mint; cx.globalAlpha = p.hot ? 1 : .75;
      cx.fillRect(p.x, p.y, p.s, p.s);
      if (p.hot) {
        const k = (Math.sin(t / 500 + p.ph) + 1) / 2, r = 4 + k * 10;
        cx.globalAlpha = .55 * (1 - k); cx.strokeStyle = col.acc;
        cx.strokeRect(p.x + p.s / 2 - r, p.y + p.s / 2 - r, r * 2, r * 2);
      }
    }
    cx.globalAlpha = 1;
  }

  function step(t) {
    const dt = Math.min(.05, (t - last) / 1000); last = t;
    for (const p of P) if ((p.x += p.vx * dt) > W + 60) { p.x = -10; p.y = Math.random() * H; }
    draw(t); raf = requestAnimationFrame(step);
  }

  size(); draw(0);
  let rt; addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(() => { size(); draw(performance.now()); }, 150); });
  if (!reduce && 'IntersectionObserver' in window) {
    new IntersectionObserver(([e]) => {
      cancelAnimationFrame(raf);
      if (e.isIntersecting) { last = performance.now(); raf = requestAnimationFrame(step); }
    }).observe(band);
  }
})();
