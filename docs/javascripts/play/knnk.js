/* books/machine-learning/09: k-nearest neighbours. Every spot on the map is coloured by the vote of its k closest
   training points. k = 1 follows every point, noise included; bigger k gives smoother regions. The points are made up. */
PLAY("knnk", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 300, st = k.stage(W, H), g = st.g, out = k.out(), K = 1, seed = 5, P = [];
  function rnd() { seed = (seed * 16807) % 2147483647; return seed / 2147483647; }
  for (var i = 0; i < 60; i++) { var x = rnd() * 560 + 20, y = rnd() * 260 + 20, c = (x - 300) * 0.4 + (y - 150) * 0.6 + Math.sin(x / 50) * 40 > 0 ? 1 : 0; if (rnd() < 0.12) c = 1 - c; P.push([x, y, c]); }
  function draw() {
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    for (var gx = 0; gx < W; gx += 10) for (var gy = 0; gy < H; gy += 10) {
      var d = P.map(function (p) { return [(p[0] - gx - 5) * (p[0] - gx - 5) + (p[1] - gy - 5) * (p[1] - gy - 5), p[2]]; }).sort(function (a, b) { return a[0] - b[0]; }), v = 0;
      for (var j = 0; j < K; j++) v += d[j][1]; g.fillStyle = v * 2 > K ? "rgba(217,96,59,0.28)" : "rgba(91,143,201,0.28)"; g.fillRect(gx, gy, 10, 10);
    }
    P.forEach(function (p) { g.fillStyle = p[2] ? C.red : C.earth; g.beginPath(); g.arc(p[0], p[1], 6, 0, 7); g.fill(); g.strokeStyle = C.bg; g.lineWidth = 1.5; g.stroke(); });
    out.textContent = "k = " + K + (K === 1 ? ": islands around every stray point." : K >= 15 ? ": very smooth; small real features start to vanish." : ": the vote smooths out the stray points.");
  }
  k.slider("k (neighbours that vote)", 1, 25, 2, K, function (v) { return v; }, function (v) { K = +v; draw(); });
  st.draw = draw; draw();
});
