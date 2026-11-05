/* books/machine-learning/08: under- and overfitting. Ten training points from a smooth curve plus noise, fitted by
   polynomials of rising degree. Training error keeps falling; error on fresh points from the same curve falls, then
   rises once the curve starts chasing the noise. The data are made up. */
PLAY("polyfit", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 290, st = k.stage(W, H), g = st.g, out = k.out(), deg = 3, seed = 21;
  function rnd() { seed = (seed * 16807) % 2147483647; return seed / 2147483647 - 0.5; }
  function truth(x) { return Math.sin(2.5 * x) + 0.4 * x; }
  var TR = [], TE = []; for (var i = 0; i < 10; i++) { var x = -1 + 2 * (i + 0.3 * rnd() + 0.5) / 10; TR.push([x, truth(x) + 0.45 * rnd()]); } for (i = 0; i < 40; i++) { x = -1 + 2 * (i + 0.5) / 40; TE.push([x, truth(x) + 0.45 * rnd()]); }
  function fit(d) {   // least squares by the normal equations, with a whisper of ridge so high degrees stay solvable
    var n = d + 1, A = [], b = []; for (var r = 0; r < n; r++) { A.push([]); b.push(0); for (var c = 0; c < n; c++) A[r].push(r === c ? 1e-9 : 0); }
    TR.forEach(function (p) { for (var r = 0; r < n; r++) { b[r] += Math.pow(p[0], r) * p[1]; for (var c = 0; c < n; c++) A[r][c] += Math.pow(p[0], r + c); } });
    for (r = 0; r < n; r++) { var m = r; for (c = r + 1; c < n; c++) if (Math.abs(A[c][r]) > Math.abs(A[m][r])) m = c; var t = A[r]; A[r] = A[m]; A[m] = t; t = b[r]; b[r] = b[m]; b[m] = t; for (c = r + 1; c < n; c++) { var f = A[c][r] / A[r][r]; for (var j = r; j < n; j++) A[c][j] -= f * A[r][j]; b[c] -= f * b[r]; } }
    var w = []; for (r = n - 1; r >= 0; r--) { var s = b[r]; for (c = r + 1; c < n; c++) s -= A[r][c] * w[c]; w[r] = s / A[r][r]; } return w;
  }
  function ev(w, x) { var s = 0; for (var i = w.length - 1; i >= 0; i--) s = s * x + w[i]; return s; }
  function mse(w, D) { var s = 0; D.forEach(function (p) { var e = ev(w, p[0]) - p[1]; s += e * e; }); return s / D.length; }
  function X(x) { return 300 + x * 270; } function Y(y) { return 160 - y * 70; }
  function draw() {
    var w = fit(deg); g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    TE.forEach(function (p) { g.fillStyle = "rgba(156,201,234,0.45)"; g.beginPath(); g.arc(X(p[0]), Y(p[1]), 4, 0, 7); g.fill(); });
    g.save(); g.beginPath(); g.rect(0, 34, W, 256); g.clip(); g.strokeStyle = C.gold; g.lineWidth = 3; g.beginPath(); for (var x = -1; x <= 1; x += 0.005) { var y = Y(ev(w, x)); if (x === -1) g.moveTo(X(x), y); else g.lineTo(X(x), y); } g.stroke(); g.restore();
    TR.forEach(function (p) { g.fillStyle = C.red; g.beginPath(); g.arc(X(p[0]), Y(p[1]), 7, 0, 7); g.fill(); });
    var a = mse(w, TR), b = mse(w, TE); g.textAlign = "left"; g.font = F(19, 700); g.fillStyle = C.red; g.fillText("training error " + a.toFixed(3), 20, 24); g.fillStyle = C.ice; g.fillText("fresh-data error " + (b > 99 ? "huge" : b.toFixed(3)), 300, 24);
    out.textContent = "Degree " + deg + (deg <= 1 ? ": too simple, it underfits." : deg >= 7 ? ": it threads every red point and chases the noise; fresh points are fitted badly." : ": close to the shape of the data.");
  }
  k.slider("Polynomial degree", 0, 9, 1, deg, function (v) { return v; }, function (v) { deg = +v; draw(); });
  st.draw = draw; draw();
});
