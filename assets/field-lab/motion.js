/* Field Lab v3 motion: first-visit intro overlay and the telemetry-band particle field. */
const root = document.documentElement;
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

// Intro. The head gate sets html.intro; the overlay is empty (all glyphs are CSS content).
if (root.classList.contains('intro')) {
  const ctl = new AbortController(), { signal } = ctl;
  const overlay = Object.assign(document.createElement('div'), { className: 'fl-intro', ariaHidden: 'true' });
  const end = () => { ctl.abort(); overlay.remove(); root.classList.remove('intro'); };
  overlay.innerHTML = '<i class="gv"></i><i class="gh"></i><i class="hint"></i>';
  overlay.addEventListener('animationend', (e) => e.animationName === 'fl-out' && end(), { signal });
  for (const type of ['pointerdown', 'keydown']) addEventListener(type, end, { once: true, signal });
  document.body.append(overlay);
}

// Particle field: mint squares drift right; ~14% are hot accent squares with a pulsing ring.
const cv = document.querySelector('.site-band canvas');
if (cv) {
  const cx = cv.getContext('2d');
  const token = (name) => getComputedStyle(root).getPropertyValue(name).trim();
  let ps, W, H, col, last = 0, raf = 0, timer;

  const size = () => {
    const dpr = Math.min(devicePixelRatio, 2), r = cv.getBoundingClientRect();
    ({ width: W, height: H } = r);
    cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
    cx.setTransform(dpr, 0, 0, dpr, 0, 0);
    col = { mint: token('--band-mint'), acc: token('--accent'), line: token('--band-line') };
    ps = Array.from({ length: Math.max(40, Math.min(150, Math.round(W * H / 7000))) }, () => ({
      x: Math.random() * W, y: Math.random() * H, vx: 12 + Math.random() * 38,
      s: 2 + Math.floor(Math.random() * 3), hot: Math.random() < .14, ph: Math.random() * 6,
    }));
  };

  const draw = (t) => {
    cx.clearRect(0, 0, W, H);
    cx.globalAlpha = .28; cx.fillStyle = col.line;
    for (let x = 0; x < W; x += 80) cx.fillRect(x, 0, 1, H);
    for (const { x, y, s, hot, ph } of ps) {
      cx.fillStyle = hot ? col.acc : col.mint; cx.globalAlpha = hot ? 1 : .75;
      cx.fillRect(x, y, s, s);
      if (!hot) continue;
      const k = (Math.sin(t / 500 + ph) + 1) / 2, r = 4 + k * 10;
      cx.globalAlpha = .55 * (1 - k); cx.strokeStyle = col.acc;
      cx.strokeRect(x + s / 2 - r, y + s / 2 - r, r * 2, r * 2);
    }
    cx.globalAlpha = 1;
  };

  const step = (t) => {
    const dt = Math.min(.05, (t - last) / 1000);
    last = t;
    for (const p of ps) if ((p.x += p.vx * dt) > W + 60) [p.x, p.y] = [-10, Math.random() * H];
    draw(t); raf = requestAnimationFrame(step);
  };

  size(); draw(0);
  addEventListener('resize', () => { clearTimeout(timer); timer = setTimeout(() => { size(); draw(performance.now()); }, 150); });
  if (!reduce) new IntersectionObserver(([e]) => {
    cancelAnimationFrame(raf);
    if (e.isIntersecting) { last = performance.now(); raf = requestAnimationFrame(step); }
  }).observe(cv.parentElement);
}
