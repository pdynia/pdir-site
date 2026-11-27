// Requires <canvas class="hero-art" aria-hidden="true"></canvas> as the first child of the hero section.
// Hero line art: thin lines fanning out from a point off-screen, drawn on canvas.
// They wave gently all the time and the whole fan rotates as the page scrolls.
(function () {
  var cv = document.querySelector('canvas.hero-art');
  if (!cv || !cv.getContext || !window.requestAnimationFrame) return;
  var still = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var rad = Math.PI / 180, SEG = 28, N = 150, BW = 1440, BH = 700, MAX_ROT = 0.6;
  var ctx = cv.getContext('2d'), W = 0, H = 0, k = 1, ox = 0;
  var rot = 0, rotTarget = 0, wave = 0, visible = true, prev = null;
  function size() {
    var r = cv.getBoundingClientRect(), dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = r.width; H = r.height; cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    k = Math.max(W / BW, H / BH); ox = W - BW * k;
    ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.lineWidth = 1;
  }
  function draw() {
    ctx.clearRect(0, 0, W, H);
    for (var i = 0; i < N; i++) {
      var u = i / (N - 1);
      // Origin beyond the top-right corner; the fan is wider than the view so it can rotate.
      var ga = (50 + 170 * u) * rad - rot, gb = (80 + 150 * u) * rad - rot;
      var px = 1580 + 160 * Math.cos(ga), py = -150 + 160 * Math.sin(ga);
      var dx = 1180 + 1650 * Math.cos(gb) - px, dy = -140 + 1650 * Math.sin(gb) - py;
      var len = Math.sqrt(dx * dx + dy * dy) || 1, nx = -dy / len, ny = dx / len;
      ctx.strokeStyle = 'rgba(178,210,163,' + (0.16 + 0.5 * Math.sin(Math.PI * u)).toFixed(3) + ')';
      ctx.beginPath();
      for (var j = 0; j <= SEG; j++) {
        var s = j / SEG;
        // Slight wave across the line, pinned at both ends.
        var off = 9 * Math.sin(Math.PI * s) * Math.sin(s * 2.2 * Math.PI * 2 + u * 5 - wave);
        var x = ox + (px + dx * s + nx * off) * k, y = (py + dy * s + ny * off) * k;
        if (j) ctx.lineTo(x, y); else ctx.moveTo(x, y);
      }
      ctx.stroke();
    }
  }
  function frame(ms) {
    if (prev === null) prev = ms;
    wave += Math.min(ms - prev, 100) / 1000 * 0.35; prev = ms;
    rot += (rotTarget - rot) * 0.08;
    draw();
    if (visible) requestAnimationFrame(frame); else prev = null;
  }
  function onScroll() { rotTarget = Math.min(MAX_ROT, window.pageYOffset * 0.0008); }
  size(); draw();
  window.addEventListener('resize', function () { size(); draw(); });
  if (still) return;
  onScroll(); rot = rotTarget;
  window.addEventListener('scroll', onScroll, { passive: true });
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (e) {
      var now = e[0].isIntersecting;
      if (now && !visible) { visible = true; requestAnimationFrame(frame); }
      visible = now;
    }).observe(cv);
  }
  requestAnimationFrame(frame);
})();
