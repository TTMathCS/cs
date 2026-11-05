/* books/algorithms/20: the convex hull by gift wrapping. Start at the leftmost point; keep turning to the point that
   leaves every other point on one side, using the orientation test, until you are back. Tap to add a point. The points
   are made up. */
PLAY("hull", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 280, st, out, film, P = [], seed = 6;
  function rnd() { seed = (seed * 16807) % 2147483647; return seed / 2147483647; }
  for (var i = 0; i < 22; i++) P.push([60 + rnd() * 480, 40 + rnd() * 200]);
  st = k.stage(W, H, function (x, y) { P.push([x, y]); film.set(1); });
  out = k.out(); var g = st.g;
  function orient(a, b, c) { return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]); }
  function wrap() { var s = 0; P.forEach(function (p, i) { if (p[0] < P[s][0]) s = i; }); var Hl = [s], cur = s; for (var guard = 0; guard < 100; guard++) { var nx = (cur + 1) % P.length; for (var j = 0; j < P.length; j++) if (orient(P[cur], P[nx], P[j]) < 0) nx = j; if (nx === s) break; Hl.push(nx); cur = nx; } return Hl; }
  function draw(t) {
    var Hl = wrap(), n = Math.max(1, Math.ceil(t * (Hl.length + 1))); g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    g.strokeStyle = C.gold; g.lineWidth = 3; g.beginPath(); for (var i = 0; i < Math.min(n, Hl.length + 1); i++) { var p = P[Hl[i % Hl.length]]; if (i) g.lineTo(p[0], p[1]); else g.moveTo(p[0], p[1]); } g.stroke();
    P.forEach(function (p, i) { g.fillStyle = Hl.indexOf(i) >= 0 && Hl.indexOf(i) < n ? C.gold : C.ice; g.beginPath(); g.arc(p[0], p[1], 6, 0, 7); g.fill(); });
    out.textContent = n > Hl.length ? "Back at the start: " + Hl.length + " of " + P.length + " points are on the hull." : "Wrapping: " + n + " hull points so far.";
  }
  film = k.loop(8, draw, { label: "Wrap" });
  st.draw = function () { draw(film.t()); };
});
