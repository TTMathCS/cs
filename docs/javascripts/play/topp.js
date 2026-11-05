/* books/ai/17: nucleus (top-p) sampling. Sort the next-token probabilities, keep the smallest set whose total reaches p,
   and sample only from those. The probabilities are made up. Low p is safe and dull; p near 1 lets in the long tail. */
PLAY("topp", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 270, st = k.stage(W, H), g = st.g, out = k.out(), p = 0.9;
  var T = [["dust", 0.34], ["storm", 0.22], ["sky", 0.14], ["wind", 0.1], ["rover", 0.07], ["crater", 0.05], ["sunset", 0.03], ["ice", 0.02], ["music", 0.015], ["banana", 0.005]];
  function draw() {
    var cum = 0, keep = 0; T.forEach(function (t, i) { if (cum < p - 1e-9) { keep = i + 1; } cum += t[1]; });
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H); var kept = 0; for (var i = 0; i < keep; i++) kept += T[i][1];
    T.forEach(function (t, i) { var y = 14 + i * 24, on = i < keep; g.fillStyle = on ? C.ink : C.ink3; g.font = F(17, 600); g.textAlign = "right"; g.fillText(t[0], 110, y + 16); g.fillStyle = on ? C.gold : "rgba(244,230,212,0.15)"; g.fillRect(120, y + 2, t[1] * 1100, 18); g.fillStyle = on ? C.ink : C.ink3; g.textAlign = "left"; g.font = F(15, 600); g.fillText(on ? Math.round(t[1] / kept * 100) + "% after renormalising" : "cut", 128 + t[1] * 1100, y + 16); });
    out.textContent = "p = " + p.toFixed(2) + ": keeps the top " + keep + " token" + (keep > 1 ? "s" : "") + " (" + Math.round(kept * 100) + "% of the probability) and samples among them.";
  }
  k.slider("p", 0.3, 1, 0.01, p, function (v) { return (+v).toFixed(2); }, function (v) { p = +v; draw(); });
  st.draw = draw; draw();
});
