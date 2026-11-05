/* books/ai/15: a four-armed bandit with ε-greedy. Each arm pays 1 with its own hidden chance (made up: 0.2, 0.5, 0.45,
   0.7). Mostly the agent pulls the arm that has paid best so far; with chance ε it tries a random one. Too little
   exploring can lock onto a worse arm; too much wastes pulls. */
PLAY("bandit", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 260, st = k.stage(W, H), g = st.g, out = k.out(), eps = 0.1, p = [0.2, 0.5, 0.45, 0.7], seedv = 9;
  function run() {
    var s = seedv; function rn() { s = (s * 16807) % 2147483647; return s / 2147483647; }
    var n = [0, 0, 0, 0], w = [0, 0, 0, 0], tot = 0, H2 = [];
    for (var t = 0; t < 500; t++) { var a; if (rn() < eps || t < 4) a = t < 4 ? t : Math.floor(rn() * 4); else { var b = 0; for (var i = 1; i < 4; i++) if (w[i] / n[i] > w[b] / n[b]) b = i; a = b; } var r = rn() < p[a] ? 1 : 0; n[a]++; w[a] += r; tot += r; if (t % 5 === 4) H2.push([n.slice(), w.slice(), tot, t + 1]); }
    return H2;
  }
  var hist = run();
  function draw(t) {
    var h = hist[Math.min(hist.length - 1, Math.floor(t * hist.length))]; g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    for (var i = 0; i < 4; i++) {
      var x = 40 + i * 130, est = h[0][i] ? h[1][i] / h[0][i] : 0, bh = h[0][i] / h[3] * 120;
      g.fillStyle = i === 3 ? C.gold : C.ice; g.fillRect(x, 168 - bh, 70, bh);
      g.fillStyle = C.ink; g.font = F(18, 700); g.textAlign = "center"; g.fillText("arm " + (i + 1), x + 35, 190); g.font = F(16, 600); g.fillStyle = C.ink3; g.fillText(h[0][i] + " pulls", x + 35, 210); g.fillText("est " + est.toFixed(2), x + 35, 160 - bh);
    }
    g.textAlign = "left"; g.fillStyle = C.ink; g.font = F(19, 700); g.fillText("pull " + h[3] + "   reward " + h[2], 20, 26);
    out.textContent = "ε = " + eps + ": " + h[2] + " points from " + h[3] + " pulls (always pulling the best arm would average " + Math.round(0.7 * h[3]) + "). Arm 4 is secretly the best.";
  }
  var film = k.loop(10, draw, { label: "Pulls" });
  k.slider("ε (how often to explore)", 0, 0.5, 0.01, eps, function (v) { return (+v).toFixed(2); }, function (v) { eps = +v; hist = run(); draw(film.t()); });
  k.buttons([["New run", function () { seedv = (seedv * 37 + 11) % 99991 + 1; hist = run(); film.set(0); film.play(); }]]);
  st.draw = function () { draw(film.t()); };
});
