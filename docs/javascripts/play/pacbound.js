/* books/machine-learning/21: the finite-class bound m ≥ (ln|H| + ln(1/δ)) / ε. This page's example: |H| = 101, ε = 0.05,
   δ = 0.05 gives 153 examples. Move the sliders. */
PLAY("pacbound", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 200, st = k.stage(W, H), g = st.g, out = k.out(), lh = 2, ep = 0.05, de = 0.05;
  function draw() {
    var Hn = Math.round(Math.pow(10, lh)), a = Math.log(Hn), b = Math.log(1 / de), m = Math.ceil((a + b) / ep);
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H); g.textAlign = "left";
    g.fillStyle = C.ink2; g.font = F(18, 600); g.fillText("examples needed", 20, 34);
    g.fillStyle = C.ink; g.font = F(40, 800); g.fillText(m.toLocaleString("en"), 20, 82);
    var tot = a + b, w = 560; g.fillStyle = C.gold; g.fillRect(20, 110, w * a / tot, 26); g.fillStyle = C.ice; g.fillRect(20 + w * a / tot, 110, w * b / tot, 26);
    g.font = F(16, 600); g.fillStyle = C.gold; g.fillText("ln|H| = " + a.toFixed(1), 20, 160); g.fillStyle = C.ice; g.fillText("ln(1/δ) = " + b.toFixed(1), 220, 160);
    g.fillStyle = C.ink3; g.fillText("then ÷ ε = " + ep, 20, 184);
    out.textContent = "|H| = " + Hn.toLocaleString("en") + ", ε = " + ep + ", δ = " + de + ": at least " + m.toLocaleString("en") + " examples. Ten times more hypotheses adds only ln 10 ≈ 2.3 to the top.";
  }
  k.slider("|H| = 10 to the power", 0.5, 9, 0.05, lh, function (v) { return Math.round(Math.pow(10, v)).toLocaleString("en"); }, function (v) { lh = +v; draw(); });
  k.slider("ε (error allowed)", 0.01, 0.3, 0.01, ep, function (v) { return (+v).toFixed(2); }, function (v) { ep = +v; draw(); });
  k.slider("δ (chance of failure)", 0.001, 0.2, 0.001, de, function (v) { return (+v).toFixed(3); }, function (v) { de = +v; draw(); });
  st.draw = draw; draw();
});
