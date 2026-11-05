/* books/ai/05: simulated annealing on a travelling-salesman tour of 25 made-up sites. Each move reverses a piece of the
   tour; a longer tour is still accepted with chance e^(−Δ/T), so early on (hot) it can climb out of traps, and as T
   cools it settles. Plain hill climbing accepts only improvements. */
PLAY("anneal", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 300, st = k.stage(W, H), g = st.g, out = k.out(), P = [], seed = 12, hist, hot = true;
  function rnd() { seed = (seed * 16807) % 2147483647; return seed / 2147483647; }
  for (var i = 0; i < 25; i++) P.push([30 + rnd() * 400, 30 + rnd() * 240]);
  function len(T) { var s = 0; for (var i = 0; i < T.length; i++) { var a = P[T[i]], b = P[T[(i + 1) % T.length]]; s += Math.hypot(a[0] - b[0], a[1] - b[1]); } return s; }
  function run() {
    var r = 7; function rn() { r = (r * 16807) % 2147483647; return r / 2147483647; }
    var T = P.map(function (_, i) { return i; }), L = len(T), H2 = [], temp = hot ? 40 : 0;
    for (var it = 0; it < 20000; it++) {
      var a = 1 + Math.floor(rn() * 23), b = a + 1 + Math.floor(rn() * (24 - a)), N = T.slice(0, a).concat(T.slice(a, b + 1).reverse(), T.slice(b + 1)), NL = len(N);
      if (NL < L || (temp > 0.01 && rn() < Math.exp(-(NL - L) / temp))) { T = N; L = NL; }
      if (hot) temp *= 0.9995;
      if (it % 200 === 0) H2.push([T.slice(), L, temp]);
    }
    H2.push([T.slice(), L, temp]); return H2;
  }
  function draw(t) {
    var h = hist[Math.min(hist.length - 1, Math.floor(t * hist.length))]; g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    g.strokeStyle = C.gold; g.lineWidth = 2.5; g.beginPath(); h[0].forEach(function (i, j) { if (j) g.lineTo(P[i][0], P[i][1]); else g.moveTo(P[i][0], P[i][1]); }); g.closePath(); g.stroke();
    P.forEach(function (p) { g.fillStyle = C.ice; g.beginPath(); g.arc(p[0], p[1], 6, 0, 7); g.fill(); });
    g.textAlign = "left"; g.fillStyle = C.ink; g.font = F(20, 700); g.fillText("length " + Math.round(h[1]), 450, 50);
    g.fillStyle = hot ? C.red : C.ink3; g.font = F(18, 600); g.fillText(hot ? "T = " + h[2].toFixed(1) : "no heat", 450, 80);
    out.textContent = (hot ? "Annealing" : "Hill climbing") + ": tour length " + Math.round(h[1]) + (t >= 1 ? " at the end." : ".");
  }
  hist = run(); var film = k.loop(10, draw, { label: "Moves" });
  k.buttons([["Annealing", function () { hot = true; hist = run(); film.set(0); film.play(); }], ["Hill climbing", function () { hot = false; hist = run(); film.set(0); film.play(); }]], true);
  st.draw = function () { draw(film.t()); };
});
