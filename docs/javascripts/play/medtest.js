/* books/ai/12: Bayes' rule with natural frequencies, starting from this page's example: a condition 1 in 100 people have,
   a test that catches 90% of them and wrongly flags 5% of the rest. Of 10,000 people, how many positives are real? */
PLAY("medtest", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 270, st = k.stage(W, H), g = st.g, out = k.out(), prev = 1, sens = 90, fpr = 5;
  function draw() {
    var N = 10000, ill = N * prev / 100, tp = ill * sens / 100, fp = (N - ill) * fpr / 100, p = tp / (tp + fp);
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    var cols = 50, rows = 20, cw = 7, per = N / (cols * rows), xi = 0;   // each square is 10 people
    var ntp = Math.round(tp / per), nfn = Math.round((ill - tp) / per), nfp = Math.round(fp / per);
    for (var r = 0; r < rows; r++) for (var c = 0; c < cols; c++) { var i = r * cols + c, col = i < ntp ? C.red : i < ntp + nfn ? "rgba(217,96,59,0.4)" : i < ntp + nfn + nfp ? C.gold : "rgba(244,230,212,0.12)"; g.fillStyle = col; g.fillRect(20 + c * (cw + 1.5), 20 + r * (cw + 1.5), cw, cw); }
    g.textAlign = "left"; g.font = F(17, 600); g.fillStyle = C.red; g.fillText("ill, test positive: " + Math.round(tp), 20, 216); g.fillStyle = C.gold; g.fillText("well, test positive: " + Math.round(fp), 250, 216);
    g.fillStyle = C.ink; g.font = F(21, 700); g.fillText("a positive is real " + (p * 100).toFixed(1) + "% of the time", 20, 252);
    out.textContent = "Of 10,000 people, " + Math.round(ill) + " are ill and " + Math.round(tp) + " of them test positive; " + Math.round(fp) + " well people also test positive. " + Math.round(tp) + " / " + Math.round(tp + fp) + " = " + p.toFixed(4) + ". Each square is 10 people.";
  }
  k.slider("How common", 0.1, 20, 0.1, prev, function (v) { return (+v).toFixed(1) + "%"; }, function (v) { prev = +v; draw(); });
  k.slider("Caught by the test", 50, 100, 1, sens, function (v) { return v + "%"; }, function (v) { sens = +v; draw(); });
  k.slider("False positives", 0.1, 20, 0.1, fpr, function (v) { return (+v).toFixed(1) + "%"; }, function (v) { fpr = +v; draw(); });
  st.draw = draw; draw();
});
