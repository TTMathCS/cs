/* books/machine-learning/20: the forward half of a diffusion model. A picture (drawn by this page) is mixed with more and
   more random noise, x_t = √ᾱ·x₀ + √(1−ᾱ)·noise, until nothing of it is left. The model is trained to run this
   backwards, one small step at a time. */
PLAY("noising", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 270, st = k.stage(W, H), g = st.g, out = k.out(), N = 48, img = [], nz = [], step = 0;
  for (var y = 0; y < N; y++) for (var x = 0; x < N; x++) { var d = Math.hypot(x - 24, y - 24), v = d < 16 ? 0.9 - d / 40 : 0.08; if (Math.abs(x - 24) < 3 && y > 30 && y < 44) v = 0.1; img.push(v); }
  for (var i = 0; i < N * N; i++) { var u = Math.random() + 1e-9, w = Math.random(); nz.push(Math.sqrt(-2 * Math.log(u)) * Math.cos(6.283 * w)); }
  function draw() {
    var T = 1000, t = step, ab = Math.exp(-0.5 * (t / T) * (t / T) * 20 - t / T * 0.1), c = 4.8; g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    for (var i = 0; i < N * N; i++) { var v = Math.sqrt(ab) * (img[i] * 2 - 1) + Math.sqrt(1 - ab) * nz[i] * 0.6; v = Math.round(Math.max(0, Math.min(1, (v + 1) / 2)) * 255); g.fillStyle = "rgb(" + v + "," + Math.round(v * 0.75) + "," + Math.round(v * 0.55) + ")"; g.fillRect(70 + (i % N) * c, 20 + Math.floor(i / N) * c, c, c); }
    g.textAlign = "left"; g.fillStyle = C.ink; g.font = F(20, 700); g.fillText("step " + t, 330, 60); g.fillStyle = C.ink3; g.font = F(18, 600); g.fillText("picture left: " + Math.round(Math.sqrt(ab) * 100) + "%", 330, 92);
    out.textContent = t === 0 ? "Step 0: the clean picture." : ab < 0.001 ? "Step " + t + ": pure noise. Generating means running this backwards." : "Step " + t + ": " + Math.round(Math.sqrt(ab) * 100) + "% picture, the rest noise.";
  }
  k.slider("Noise step", 0, 1000, 10, step, function (v) { return v + " of 1000"; }, function (v) { step = +v; draw(); });
  st.draw = draw; draw();
});
