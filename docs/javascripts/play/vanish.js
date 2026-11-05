/* books/machine-learning/16: vanishing gradients. Going back through each layer multiplies the gradient by that layer's
   slope. The sigmoid's slope is at most 0.25, so after many layers almost nothing is left for the first ones; ReLU's
   slope is 1 where it is active. The bars show the best case for each. */
PLAY("vanish", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 240, st = k.stage(W, H), g = st.g, out = k.out(), L = 10;
  function draw() {
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    var bw = Math.min(40, 540 / L - 4);
    for (var i = 0; i < L; i++) {
      var depth = L - i, sg = Math.pow(0.25, depth - 1), x = 30 + i * (540 / L);
      var hs = Math.max(1, 80 * (1 + Math.log10(sg) / 8)); g.fillStyle = C.ice; g.fillRect(x, 120 - hs, bw / 2 - 1, hs);
      g.fillStyle = C.gold; g.fillRect(x + bw / 2, 40, bw / 2 - 1, 80);
    }
    g.strokeStyle = C.line; g.beginPath(); g.moveTo(20, 120); g.lineTo(580, 120); g.stroke();
    g.font = F(17, 600); g.textAlign = "left"; g.fillStyle = C.ink3; g.fillText("first layer", 24, 142); g.textAlign = "right"; g.fillText("last layer", 576, 142);
    var s = Math.pow(0.25, L - 1); g.textAlign = "left"; g.font = F(19, 700); g.fillStyle = C.ice; g.fillText("sigmoid: first layer gets " + (s < 1e-3 ? s.toExponential(1).replace("e", "×10^") : s.toFixed(4)), 20, 180); g.fillStyle = C.gold; g.fillText("ReLU (active): first layer gets 1", 20, 210);
    out.textContent = L + " layers: with sigmoids the first layer's gradient is at most 0.25^" + (L - 1) + " ≈ " + s.toExponential(1) + " of the last layer's, so it barely learns. (Bars on a log scale.)";
  }
  k.slider("Layers", 2, 30, 1, L, function (v) { return v; }, function (v) { L = +v; draw(); });
  st.draw = draw; draw();
});
