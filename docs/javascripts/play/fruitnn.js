/* books/machine-learning/01: the nearest-neighbour learner on this page's ten fruit (length and width in cm). Tap
   anywhere to place a new fruit; it takes the label of the closest one. */
PLAY("fruitnn", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 330, out, P = [[7.0, 7.2, 0], [7.6, 7.5, 0], [6.8, 6.9, 0], [8.0, 7.8, 0], [7.2, 7.4, 0], [8.5, 5.9, 1], [9.2, 6.3, 1], [8.0, 5.6, 1], [9.6, 6.6, 1], [8.8, 6.1, 1]], q = [8.3, 6.8];
  var x0 = 6.5, x1 = 10, y0 = 5.4, y1 = 8.0;
  function X(v) { return 70 + (v - x0) / (x1 - x0) * 500; } function Y(v) { return 280 - (v - y0) / (y1 - y0) * 250; }
  var st = k.stage(W, H, function (x, y) { q = [x0 + (x - 70) / 500 * (x1 - x0), y0 + (280 - y) / 250 * (y1 - y0)]; draw(); }), g = st.g; out = k.out();
  function draw() {
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    var best = 0, bd = 1e9; P.forEach(function (p, i) { var d = Math.hypot(p[0] - q[0], p[1] - q[1]); if (d < bd) { bd = d; best = i; } });
    g.strokeStyle = C.line; g.lineWidth = 1; for (var v = 7; v <= 10; v++) { g.beginPath(); g.moveTo(X(v), 30); g.lineTo(X(v), 280); g.stroke(); }
    for (v = 6; v <= 8; v++) { g.beginPath(); g.moveTo(70, Y(v)); g.lineTo(570, Y(v)); g.stroke(); }
    g.fillStyle = C.ink3; g.font = F(15, 600); g.textAlign = "center"; for (v = 7; v <= 10; v++) g.fillText(v, X(v), 300); g.fillText("length (cm)", 320, 322);
    g.textAlign = "right"; for (v = 6; v <= 8; v++) g.fillText(v, 60, Y(v) + 5);
    g.strokeStyle = C.ink; g.setLineDash([5, 4]); g.beginPath(); g.moveTo(X(q[0]), Y(q[1])); g.lineTo(X(P[best][0]), Y(P[best][1])); g.stroke(); g.setLineDash([]);
    P.forEach(function (p) { g.fillStyle = p[2] ? "#f2dc4a" : "#f08a24"; g.beginPath(); g.arc(X(p[0]), Y(p[1]), 10, 0, 7); g.fill(); });
    var lab = P[best][2]; g.strokeStyle = lab ? "#f2dc4a" : "#f08a24"; g.lineWidth = 4; g.beginPath(); g.arc(X(q[0]), Y(q[1]), 12, 0, 7); g.stroke();
    g.textAlign = "left"; g.font = F(18, 700); g.fillStyle = "#f08a24"; g.fillText("● orange", 80, 24); g.fillStyle = "#f2dc4a"; g.fillText("● lemon", 200, 24);
    out.textContent = "New fruit " + q[0].toFixed(1) + " × " + q[1].toFixed(1) + " cm: nearest is fruit " + (best + 1) + ", " + bd.toFixed(2) + " cm away, so it is called " + (lab ? "a lemon" : "an orange") + ". Tap to move it.";
  }
  st.draw = draw; draw();
});
