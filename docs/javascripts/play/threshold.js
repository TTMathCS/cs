/* books/machine-learning/07: choosing a threshold. A classifier gives each case a score; cases above the threshold are
   called positive. Moving it trades precision (how many flagged cases are real) against recall (how many real cases are
   flagged). The two score distributions are made up: 100 positives and 900 negatives. */
PLAY("threshold", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 290, st = k.stage(W, H), g = st.g, out = k.out(), th = 0.5;
  function nd(x, m, s) { return Math.exp(-0.5 * (x - m) * (x - m) / (s * s)) / (s * Math.sqrt(2 * Math.PI)); }
  function cdf(x, m, s) { var t = 1 / (1 + 0.2316419 * Math.abs((x - m) / s)), d = 0.3989423 * Math.exp(-0.5 * Math.pow((x - m) / s, 2)), p = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274)))); return (x - m) / s > 0 ? 1 - p : p; }
  function draw() {
    var Pn = 100, Nn = 900, tp = Pn * (1 - cdf(th, 0.65, 0.12)), fp = Nn * (1 - cdf(th, 0.35, 0.12)), fn = Pn - tp, tn = Nn - fp;
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    [[0.35, Nn, C.ice], [0.65, Pn, C.red]].forEach(function (d) { g.fillStyle = d[2]; g.globalAlpha = 0.6; g.beginPath(); g.moveTo(30, 160); for (var x = 0; x <= 1; x += 0.005) g.lineTo(30 + x * 540, 160 - nd(x, d[0], 0.12) * 36); g.lineTo(570, 160); g.fill(); g.globalAlpha = 1; });
    var tx = 30 + th * 540; g.strokeStyle = C.gold; g.lineWidth = 3; g.beginPath(); g.moveTo(tx, 20); g.lineTo(tx, 170); g.stroke();
    g.font = F(17, 600); g.textAlign = "left"; g.fillStyle = C.ice; g.fillText("negatives (900)", 30, 30); g.fillStyle = C.red; g.fillText("positives (100)", 440, 30);
    var prec = tp / (tp + fp || 1), rec = tp / Pn;
    g.fillStyle = C.ink; g.font = F(19, 700, "m"); g.fillText("caught " + Math.round(tp) + "  missed " + Math.round(fn), 30, 206); g.fillText("false alarms " + Math.round(fp), 30, 234);
    g.fillStyle = C.gold; g.font = F(21, 700); g.fillText("precision " + Math.round(prec * 100) + "%   recall " + Math.round(rec * 100) + "%", 30, 270);
    out.textContent = "Threshold " + th.toFixed(2) + ": " + Math.round(prec * 100) + "% of flagged cases are real; " + Math.round(rec * 100) + "% of real cases are flagged. Accuracy " + Math.round((tp + tn) / 10) + "%.";
  }
  k.slider("Threshold", 0.2, 0.9, 0.01, th, function (v) { return (+v).toFixed(2); }, function (v) { th = +v; draw(); });
  st.draw = draw; draw();
});
