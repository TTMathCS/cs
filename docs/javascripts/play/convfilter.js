/* books/machine-learning/17: a 3 × 3 filter slid over a small picture. Each output pixel is the sum of the nine pixels
   under the filter times the filter's numbers. Pick a filter: blur averages, the edge filters respond where brightness
   changes. The picture (a crater on a slope) is drawn by this page. */
PLAY("convfilter", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 280, st = k.stage(W, H), g = st.g, out = k.out(), N = 40, img = [], fi = 1;
  for (var y = 0; y < N; y++) for (var x = 0; x < N; x++) { var d = Math.hypot(x - 22, y - 18), v = 0.35 + x * 0.008; if (d < 10) v -= 0.25 * (1 - d / 10); if (d > 9 && d < 12) v += 0.3; if (y > 32) v += 0.15; img.push(Math.max(0, Math.min(1, v))); }
  var FL = [["blur", [1, 1, 1, 1, 1, 1, 1, 1, 1].map(function (v) { return v / 9; })], ["vertical edges", [-1, 0, 1, -2, 0, 2, -1, 0, 1]], ["horizontal edges", [-1, -2, -1, 0, 0, 0, 1, 2, 1]], ["sharpen", [0, -1, 0, -1, 5, -1, 0, -1, 0]]];
  function px(a, x, y) { x = Math.max(0, Math.min(N - 1, x)); y = Math.max(0, Math.min(N - 1, y)); return a[y * N + x]; }
  function draw() {
    var f = FL[fi][1], o = [], edge = fi === 1 || fi === 2; g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    for (var y = 0; y < N; y++) for (var x = 0; x < N; x++) { var s = 0; for (var j = 0; j < 9; j++) s += f[j] * px(img, x + j % 3 - 1, y + Math.floor(j / 3) - 1); o.push(edge ? 0.5 + s * 1.5 : s); }
    var c = 5;
    for (y = 0; y < N; y++) for (x = 0; x < N; x++) { var v = Math.round(Math.max(0, Math.min(1, img[y * N + x])) * 255); g.fillStyle = "rgb(" + v + "," + Math.round(v * 0.7) + "," + Math.round(v * 0.5) + ")"; g.fillRect(20 + x * c, 40 + y * c, c, c); v = Math.round(Math.max(0, Math.min(1, o[y * N + x])) * 255); g.fillStyle = "rgb(" + v + "," + v + "," + v + ")"; g.fillRect(380 + x * c, 40 + y * c, c, c); }
    g.font = F(17, 600); g.fillStyle = C.ink2; g.textAlign = "center"; g.fillText("picture", 120, 30); g.fillText(FL[fi][0], 480, 30);
    g.font = F(17, 700, "m"); for (var j = 0; j < 9; j++) { var vv = f[j]; g.fillStyle = vv > 0 ? C.gold : vv < 0 ? C.ice : C.ink3; g.fillText(fi === 0 ? "1/9" : vv, 300 + (j % 3 - 1) * 36, 130 + (Math.floor(j / 3) - 1) * 30); }
    out.textContent = "The " + FL[fi][0] + " filter: " + (fi === 0 ? "each pixel becomes the average of its neighbourhood." : fi === 3 ? "the centre counts five times, its neighbours subtract." : "bright where brightness changes " + (fi === 1 ? "left to right" : "top to bottom") + ", grey where it is flat.");
  }
  k.buttons(FL.map(function (f, i) { return [f[0], function () { fi = i; draw(); }]; }), true);
  fi = 0; st.draw = draw; draw();
});
