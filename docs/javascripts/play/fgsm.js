/* books/machine-learning/22: why tiny changes fool a linear model. Each of d inputs moves by at most ε against the sign
   of its weight; the score drops by ε times the sum of |weights|, which grows with d. Weights and score are made up
   (each |w| = 0.05, starting score +2). */
PLAY("fgsm", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 200, st = k.stage(W, H), g = st.g, out = k.out(), d = 784, ep = 0.02, s0 = 2, aw = 0.05;
  function draw() {
    var drop = ep * d * aw, s = s0 - drop, X = function (v) { return 300 + v * 50; };
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    g.strokeStyle = C.ink3; g.lineWidth = 2; g.beginPath(); g.moveTo(40, 100); g.lineTo(560, 100); g.stroke();
    g.strokeStyle = C.ink; g.beginPath(); g.moveTo(300, 70); g.lineTo(300, 130); g.stroke();
    g.textAlign = "center"; g.font = F(16, 700); g.fillStyle = C.green; g.fillText("right answer →", 450, 60); g.fillStyle = C.red; g.fillText("← wrong answer", 150, 60);
    var cs = Math.max(-5, Math.min(5, s));
    g.fillStyle = C.ice; g.beginPath(); g.arc(X(s0), 100, 12, 0, 7); g.fill();
    g.strokeStyle = C.gold; g.lineWidth = 4; g.beginPath(); g.moveTo(X(s0), 100); g.lineTo(X(cs), 100); g.stroke();
    g.fillStyle = s < 0 ? C.red : C.gold; g.beginPath(); g.arc(X(cs), 100, 12, 0, 7); g.fill();
    g.fillStyle = C.ink; g.font = F(17, 700); g.textAlign = "left"; g.fillText("score " + s0 + " → " + s.toFixed(2), 40, 160);
    out.textContent = d + " inputs, each nudged by only " + ep + ": the score falls by " + drop.toFixed(2) + (s < 0 ? ", and the answer flips." : ". Add more inputs or a bigger nudge.");
  }
  k.slider("Inputs d", 10, 3000, 10, d, function (v) { return v; }, function (v) { d = +v; draw(); });
  k.slider("Nudge per input ε", 0.001, 0.1, 0.001, ep, function (v) { return (+v).toFixed(3); }, function (v) { ep = +v; draw(); });
  st.draw = draw; draw();
});
