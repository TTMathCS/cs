/* books/ai/18: a PID controller driving a rover to a target 10 m ahead, with friction and a slope pushing back (a made-up
   model). P pushes in proportion to the error, I adds up past error to beat the steady push of the slope, D brakes as
   the error shrinks. Change the gains and press Play. */
PLAY("pid", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 260, st = k.stage(W, H), g = st.g, out = k.out(), Kp = 2, Ki = 0, Kd = 0;
  function run() { var x = 0, v = 0, I = 0, prev = 10, D = []; for (var t = 0; t < 400; t++) { var dt = 0.05, e = 10 - x; I += e * dt; var u = Kp * e + Ki * I + Kd * (e - prev) / dt; prev = e; u = Math.max(-8, Math.min(8, u)); v += (u - 0.8 * v - 1.5) * dt; x += v * dt; D.push(x); } return D; }
  function draw(t) {
    var D = run(), n = Math.max(1, Math.ceil(t * D.length)); g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    function X(i) { return 30 + i * 1.4; } function Y(x) { return 210 - x * 14; }
    g.strokeStyle = C.green; g.setLineDash([6, 6]); g.beginPath(); g.moveTo(30, Y(10)); g.lineTo(590, Y(10)); g.stroke(); g.setLineDash([]);
    g.strokeStyle = C.gold; g.lineWidth = 3; g.beginPath(); for (var i = 0; i < n; i++) { if (i) g.lineTo(X(i), Y(D[i])); else g.moveTo(X(i), Y(D[i])); } g.stroke();
    g.textAlign = "left"; g.font = F(17, 700); g.fillStyle = C.green; g.fillText("target 10 m", 34, Y(10) - 10);
    var x = D[n - 1], peak = Math.max.apply(null, D.slice(0, n));
    out.textContent = "Now at " + x.toFixed(2) + " m" + (peak > 10.2 ? ", overshot to " + peak.toFixed(1) + " m" : "") + (n === D.length && Math.abs(x - 10) > 0.2 ? "; stuck " + (10 - x).toFixed(1) + " m short: the slope wins against P alone. Add some I." : ".");
  }
  var film = k.loop(8, draw, { label: "Time" });
  k.slider("P", 0, 10, 0.1, Kp, function (v) { return (+v).toFixed(1); }, function (v) { Kp = +v; draw(film.t()); });
  k.slider("I", 0, 3, 0.05, Ki, function (v) { return (+v).toFixed(2); }, function (v) { Ki = +v; draw(film.t()); });
  k.slider("D", 0, 3, 0.05, Kd, function (v) { return (+v).toFixed(2); }, function (v) { Kd = +v; draw(film.t()); });
  st.draw = function () { draw(film.t()); };
});
