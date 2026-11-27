// Requires the .mena-map SVG (groups .map-arcs, .map-dots, .map-labels, path .map-main, circle .map-hub)
// and a list #markets .markets whose <li> texts match the map labels.
// Markets map: routes draw out from Dubai as the map scrolls into view,
// and the dotted Europe route flows with the scroll.
(function () {
  var map = document.querySelector('.mena-map');
  if (!map || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var arcs = [].slice.call(map.querySelectorAll('.map-arcs path'));
  var dots = [].slice.call(map.querySelectorAll('.map-dots circle')).slice(0, arcs.length);
  var labels = [].slice.call(map.querySelectorAll('.map-labels text')).slice(0, arcs.length);
  var main = map.querySelector('.map-main');
  arcs.forEach(function (a) { a.setAttribute('pathLength', '1'); a.style.strokeDasharray = '1'; });
  // Draw order follows the country list; each route finishes before the next starts.
  var ORDER = ['Saudi Arabia', 'Qatar', 'Kuwait', 'Bahrain', 'Oman', 'Jordan', 'Lebanon', 'Iraq', 'Egypt', 'Morocco', 'Tunisia'];
  var slot = arcs.map(function (a, i) { var k = labels[i] ? ORDER.indexOf(labels[i].textContent.trim()) : -1; return k < 0 ? i : k; });
  var ticking = false;
  function update() {
    ticking = false;
    var r = map.getBoundingClientRect(), vh = window.innerHeight;
    // 0 when the map's top is a little inside the screen, 1 after a short further scroll.
    var p = Math.max(0, Math.min(1, (vh * 0.9 - r.top) / (vh * 0.42)));
    arcs.forEach(function (a, i) {
      var q = Math.max(0, Math.min(1, p * arcs.length - slot[i]));
      a.style.strokeDashoffset = (1 - q).toFixed(3);
      var o = Math.max(0, Math.min(1, (q - 0.7) / 0.3)).toFixed(2);
      if (dots[i]) dots[i].style.opacity = o;
      if (labels[i]) labels[i].style.opacity = o;
    });
    if (main) main.style.strokeDashoffset = (-window.pageYOffset * 0.12).toFixed(1);
  }
  window.addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
  window.addEventListener('resize', update);
  update();
})();

// Markets: pointing at a country (in the list or on the map) lights it up in the list
// and redraws its route on the map.
(function () {
  var map = document.querySelector('.mena-map'), list = document.querySelector('#markets .markets');
  if (!map || !list) return;
  var still = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var arcs = [].slice.call(map.querySelectorAll('.map-arcs path'));
  var dots = [].slice.call(map.querySelectorAll('.map-dots circle')).slice(0, arcs.length);
  var labels = [].slice.call(map.querySelectorAll('.map-labels text')).slice(0, arcs.length);
  var hub = map.querySelector('.map-hub'), items = {}, index = {}, running = [];
  [].slice.call(list.children).forEach(function (li) { items[li.textContent.trim()] = li; });
  labels.forEach(function (l, i) { index[l.textContent.trim()] = i; });
  function set(name, on) {
    var li = items[name], i = index[name];
    if (li) li.classList.toggle('on', on);
    if (name === 'United Arab Emirates') { if (hub) hub.classList.toggle('hot', on); return; }
    if (i === undefined) return;
    arcs[i].classList.toggle('hot', on); dots[i].classList.toggle('hot', on); labels[i].classList.toggle('hot', on);
    if (still || !arcs[i].animate) return;
    // While pointed at, the route keeps drawing from Dubai out to the country, over and over.
    if (running[i]) { running[i].cancel(); running[i] = null; }
    if (on) {
      if (!arcs[i].hasAttribute('pathLength')) { arcs[i].setAttribute('pathLength', '1'); arcs[i].style.strokeDasharray = '1'; }
      running[i] = arcs[i].animate(
        [{ strokeDashoffset: 1 }, { strokeDashoffset: 0, offset: 0.7 }, { strokeDashoffset: 0 }],
        { duration: 1100, easing: 'ease-out', iterations: Infinity });
    }
  }
  function bind(el, name) {
    el.addEventListener('mouseenter', function () { set(name, true); });
    el.addEventListener('mouseleave', function () { set(name, false); });
    el.addEventListener('focus', function () { set(name, true); });
    el.addEventListener('blur', function () { set(name, false); });
  }
  Object.keys(items).forEach(function (name) { items[name].tabIndex = 0; bind(items[name], name); });
  labels.forEach(function (l, i) { var name = l.textContent.trim(); bind(l, name); bind(dots[i], name); });
})();
