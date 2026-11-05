/* books/machine-learning/13: Lloyd's algorithm for k-means. Assign every point to its nearest centre, move each centre to
   the mean of its points, repeat until nothing changes. The points are made up, in three loose groups; New start drops
   the centres somewhere else, which can end in a worse answer. */
PLAY("kmeans", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 290, st = k.stage(W, H), g = st.g, out = k.out(), seed = 3, P = [], hist, cols = [C.gold, C.ice, C.green];
  function rnd() { seed = (seed * 16807) % 2147483647; return seed / 2147483647; }
  function gs() { return Math.sqrt(-2 * Math.log(rnd() + 1e-9)) * Math.cos(6.283 * rnd()); }
  [[160, 90], [420, 80], [300, 220]].forEach(function (c) { for (var i = 0; i < 25; i++) P.push([c[0] + gs() * 45, c[1] + gs() * 32]); });
  var s2 = 1;
  function run() {
    var r = s2; function rn() { r = (r * 16807) % 2147483647; return r / 2147483647; }
    var M = [0, 1, 2].map(function () { return [40 + rn() * 520, 30 + rn() * 230]; }), H2 = [];
    for (var it = 0; it < 12; it++) {
      var A = P.map(function (p) { var b = 0, bd = 1e9; M.forEach(function (m, j) { var d = (p[0] - m[0]) * (p[0] - m[0]) + (p[1] - m[1]) * (p[1] - m[1]); if (d < bd) { bd = d; b = j; } }); return b; });
      H2.push([M.map(function (m) { return m.slice(); }), A]);
      var N = M.map(function (m, j) { var sx = 0, sy = 0, n = 0; P.forEach(function (p, i) { if (A[i] === j) { sx += p[0]; sy += p[1]; n++; } }); return n ? [sx / n, sy / n] : m; });
      M = N;
    }
    return H2;
  }
  function draw(t) {
    var h = hist[Math.min(hist.length - 1, Math.floor(t * hist.length))], M = h[0], A = h[1], idx = Math.min(hist.length - 1, Math.floor(t * hist.length));
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    P.forEach(function (p, i) { g.fillStyle = cols[A[i]]; g.globalAlpha = 0.8; g.beginPath(); g.arc(p[0], p[1], 5, 0, 7); g.fill(); g.globalAlpha = 1; });
    M.forEach(function (m, j) { g.fillStyle = cols[j]; g.strokeStyle = C.ink; g.lineWidth = 3; g.beginPath(); g.moveTo(m[0], m[1] - 13); g.lineTo(m[0] + 13, m[1]); g.lineTo(m[0], m[1] + 13); g.lineTo(m[0] - 13, m[1]); g.closePath(); g.fill(); g.stroke(); });
    var sse = 0; P.forEach(function (p, i) { sse += Math.pow(p[0] - M[A[i]][0], 2) + Math.pow(p[1] - M[A[i]][1], 2); });
    g.fillStyle = C.ink; g.font = F(19, 700); g.textAlign = "left"; g.fillText("round " + (idx + 1) + "   spread " + Math.round(sse / 1000) + "k", 20, 30);
    out.textContent = idx === 0 ? "Centres dropped at random; each point joins the nearest." : "Each centre moved to the middle of its points, and points re-joined the nearest centre.";
  }
  hist = run();
  var film = k.loop(10, draw, { label: "Rounds" });
  k.buttons([["New start", function () { s2 = (s2 * 7 + 13) % 1000 + 1; hist = run(); film.set(0); film.play(); }]]);
  st.draw = function () { draw(film.t()); };
});
