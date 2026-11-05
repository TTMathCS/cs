/* books/machine-learning/11: choosing a split. Slide the cut; each side's Gini impurity is 1 − Σ p², and the split's
   score is the two sides' impurities weighted by size. A tree picks the cut with the lowest score. The 20 points are
   made up. */
PLAY("gini", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 220, st = k.stage(W, H), g = st.g, out = k.out(), cut = 4.5;
  var P = [[0.5, 0], [1, 0], [1.4, 0], [2, 0], [2.3, 1], [2.8, 0], [3.1, 0], [3.6, 0], [4.1, 1], [4.6, 0], [5.2, 1], [5.5, 1], [6, 0], [6.4, 1], [6.9, 1], [7.3, 1], [7.8, 1], [8.2, 1], [8.8, 1], [9.4, 1]];
  function gi(S) { if (!S.length) return 0; var p = S.filter(function (q) { return q[1]; }).length / S.length; return 1 - p * p - (1 - p) * (1 - p); }
  function score(c) { var L = P.filter(function (p) { return p[0] < c; }), R = P.filter(function (p) { return p[0] >= c; }); return [(L.length * gi(L) + R.length * gi(R)) / P.length, gi(L), gi(R), L.length, R.length]; }
  function draw() {
    var s = score(cut), best = 0.25, bs = 9; for (var c = 0.25; c < 10; c += 0.25) { var v = score(c)[0]; if (v < bs - 1e-9) { bs = v; best = c; } }
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    P.forEach(function (p) { g.fillStyle = p[1] ? C.red : C.earth; g.beginPath(); g.arc(30 + p[0] * 56, 90, 10, 0, 7); g.fill(); });
    var cx = 30 + cut * 56; g.strokeStyle = C.gold; g.lineWidth = 3; g.beginPath(); g.moveTo(cx, 50); g.lineTo(cx, 130); g.stroke();
    g.font = F(18, 600); g.fillStyle = C.ink2; g.textAlign = "center"; g.fillText("left: " + s[3] + " points, Gini " + s[1].toFixed(2), Math.max(140, cx / 2 + 15), 34); g.fillText("right: " + s[4] + ", Gini " + s[2].toFixed(2), Math.min(470, (cx + 590) / 2), 160);
    g.fillStyle = C.gold; g.font = F(21, 700); g.textAlign = "left"; g.fillText("split score " + s[0].toFixed(3), 20, 200);
    out.textContent = "Cut at " + cut + ": weighted impurity " + s[0].toFixed(3) + ". The best cut is at " + best + " (" + bs.toFixed(3) + ").";
  }
  k.slider("Cut position", 0.25, 9.75, 0.25, cut, function (v) { return (+v).toFixed(2); }, function (v) { cut = +v; draw(); });
  st.draw = draw; draw();
});
