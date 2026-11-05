/* books/machine-learning/06: the perceptron learning rule. Take each point in turn; if it is on the wrong side of the
   line, nudge the weights toward it (w ← w + y·x). On data a line can separate, this always stops. The points are made
   up. */
PLAY("perceptron", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 290, st = k.stage(W, H), g = st.g, out = k.out(), seed = 4, P = [], hist;
  function rnd() { seed = (seed * 16807) % 2147483647; return seed / 2147483647; }
  while (P.length < 30) { var x = rnd() * 2 - 1, y = rnd() * 2 - 1, m = 0.7 * x - y + 0.15; if (Math.abs(m) > 0.12) P.push([x, y, m > 0 ? 1 : -1]); }
  function run() { var w = [0.2, 1, 0.1], H2 = [[w.slice(), -1, 0]]; for (var ep = 0; ep < 6; ep++) P.forEach(function (p, i) { var s = w[0] * p[0] + w[1] * p[1] + w[2]; if (s * p[2] <= 0) { w[0] += 0.5 * p[2] * p[0]; w[1] += 0.5 * p[2] * p[1]; w[2] += 0.5 * p[2]; H2.push([w.slice(), i, 0]); } }); return H2; }
  hist = run();
  function X(x) { return 300 + x * 200; } function Y(y) { return 145 - y * 125; }
  function draw(t) {
    var idx = Math.min(hist.length - 1, Math.floor(t * hist.length)), w = hist[idx][0], wrong = 0;
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    if (Math.abs(w[1]) > 1e-6) { g.strokeStyle = C.gold; g.lineWidth = 3; g.beginPath(); g.moveTo(X(-1.4), Y(-(w[0] * -1.4 + w[2]) / w[1])); g.lineTo(X(1.4), Y(-(w[0] * 1.4 + w[2]) / w[1])); g.stroke(); }
    P.forEach(function (p, i) { var ok = (w[0] * p[0] + w[1] * p[1] + w[2]) * p[2] > 0; if (!ok) wrong++; g.fillStyle = p[2] > 0 ? C.red : C.earth; g.beginPath(); g.arc(X(p[0]), Y(p[1]), i === hist[idx][1] ? 10 : 6, 0, 7); g.fill(); if (!ok) { g.strokeStyle = C.ink; g.lineWidth = 2; g.stroke(); } });
    g.fillStyle = C.ink; g.font = F(19, 700); g.textAlign = "left"; g.fillText("update " + idx + "   wrong side: " + wrong, 20, 28);
    out.textContent = wrong ? "Points circled in white are on the wrong side; each mistake tilts the line toward it." : "Every point is on its own side: the perceptron stops after " + idx + " updates.";
  }
  var film = k.loop(10, draw, { label: "Updates" });
  st.draw = function () { draw(film.t()); };
});
