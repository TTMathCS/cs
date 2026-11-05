/* books/machine-learning/04: least squares. Tap to add points (tap a point to remove it); the line is the one with the
   smallest sum of squared vertical distances, found exactly by the normal equations. R² is the share of the spread in
   y that the line explains. The starting points are made up. */
PLAY("linefit", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 300, st, out, P = [[1, 2.1], [2, 2.9], [3, 3.2], [4, 4.8], [5, 5.1], [6, 5.9], [7, 7.4], [8, 7.6]];
  function X(x) { return 50 + x * 55; } function Y(y) { return 270 - y * 25; }
  st = k.stage(W, H, function (px, py) { var x = (px - 50) / 55, y = (270 - py) / 25, hit = -1; P.forEach(function (p, i) { if (Math.abs(X(p[0]) - px) < 14 && Math.abs(Y(p[1]) - py) < 14) hit = i; }); if (hit >= 0) P.splice(hit, 1); else if (x >= 0 && x <= 9.6 && y >= 0 && y <= 10.4) P.push([x, y]); draw(); });
  out = k.out(); var g = st.g;
  function draw() {
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    g.strokeStyle = C.line; g.beginPath(); g.moveTo(50, 10); g.lineTo(50, 270); g.lineTo(590, 270); g.stroke();
    var n = P.length, mx = 0, my = 0; P.forEach(function (p) { mx += p[0] / n; my += p[1] / n; });
    var sxy = 0, sxx = 0, syy = 0; P.forEach(function (p) { sxy += (p[0] - mx) * (p[1] - my); sxx += (p[0] - mx) * (p[0] - mx); syy += (p[1] - my) * (p[1] - my); });
    if (n < 2 || sxx === 0) { P.forEach(function (p) { g.fillStyle = C.gold; g.beginPath(); g.arc(X(p[0]), Y(p[1]), 7, 0, 7); g.fill(); }); out.textContent = "Add at least two points at different x."; return; }
    var b = sxy / sxx, a = my - b * mx, sse = 0; P.forEach(function (p) { var r = p[1] - (a + b * p[0]); sse += r * r; g.strokeStyle = "rgba(217,96,59,0.8)"; g.lineWidth = 2; g.beginPath(); g.moveTo(X(p[0]), Y(p[1])); g.lineTo(X(p[0]), Y(a + b * p[0])); g.stroke(); });
    g.strokeStyle = C.ice; g.lineWidth = 3; g.beginPath(); g.moveTo(X(0), Y(a)); g.lineTo(X(9.8), Y(a + b * 9.8)); g.stroke();
    P.forEach(function (p) { g.fillStyle = C.gold; g.beginPath(); g.arc(X(p[0]), Y(p[1]), 7, 0, 7); g.fill(); });
    var r2 = syy ? 1 - sse / syy : 1; g.fillStyle = C.ink; g.font = F(20, 700); g.textAlign = "left"; g.fillText("y = " + a.toFixed(2) + " + " + b.toFixed(2) + "x    R² = " + r2.toFixed(2), 64, 30);
    out.textContent = n + " points. Red lines are the errors whose squares the fit makes as small as possible.";
  }
  st.draw = draw; draw();
});
