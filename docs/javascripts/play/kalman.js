/* books/ai/13: a 1-D Kalman filter tracking a rover driving at a steady speed from noisy position readings (made up).
   Each step predicts where it should be, then blends in the new reading by the Kalman gain: more trust in the reading
   when the prediction is uncertain, less when the readings are noisy. */
PLAY("kalman", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 280, st = k.stage(W, H), g = st.g, out = k.out(), R = 4;
  function run() {
    var s = 5; function rn() { s = (s * 16807) % 2147483647; return s / 2147483647; } function gs() { return Math.sqrt(-2 * Math.log(rn() + 1e-9)) * Math.cos(6.283 * rn()); }
    var x = 0, est = 0, P = 10, Q = 0.05, D = [];
    for (var t = 0; t < 50; t++) { x += 0.5 + gs() * 0.2; var z = x + gs() * Math.sqrt(R); est += 0.5; P += Q; var K = P / (P + R); est += K * (z - est); P *= (1 - K); D.push([x, z, est, K]); }
    return D;
  }
  function draw(t) {
    var D = run(), n = Math.max(1, Math.ceil(t * D.length)); g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    function X(i) { return 30 + i * 11; } function Y(v) { return 250 - v * 8.5; }
    g.strokeStyle = C.green; g.lineWidth = 2; g.beginPath(); for (var i = 0; i < n; i++) { if (i) g.lineTo(X(i), Y(D[i][0])); else g.moveTo(X(i), Y(D[i][0])); } g.stroke();
    for (i = 0; i < n; i++) { g.fillStyle = C.red; g.beginPath(); g.arc(X(i), Y(D[i][1]), 3.5, 0, 7); g.fill(); }
    g.strokeStyle = C.gold; g.lineWidth = 3; g.beginPath(); for (i = 0; i < n; i++) { if (i) g.lineTo(X(i), Y(D[i][2])); else g.moveTo(X(i), Y(D[i][2])); } g.stroke();
    g.textAlign = "left"; g.font = F(17, 700); g.fillStyle = C.green; g.fillText("true position", 30, 24); g.fillStyle = C.red; g.fillText("readings", 170, 24); g.fillStyle = C.gold; g.fillText("Kalman estimate", 270, 24);
    var e1 = 0, e2 = 0; D.slice(0, n).forEach(function (d) { e1 += Math.abs(d[1] - d[0]); e2 += Math.abs(d[2] - d[0]); });
    out.textContent = "Reading noise " + Math.sqrt(R).toFixed(1) + " m: readings are off by " + (e1 / n).toFixed(2) + " m on average, the estimate by " + (e2 / n).toFixed(2) + " m. Gain now " + D[n - 1][3].toFixed(2) + ".";
  }
  var film = k.loop(8, draw, { label: "Time" });
  k.slider("Reading noise", 0.5, 4, 0.1, Math.sqrt(R), function (v) { return (+v).toFixed(1) + " m"; }, function (v) { R = v * v; draw(film.t()); });
  st.draw = function () { draw(film.t()); };
});
