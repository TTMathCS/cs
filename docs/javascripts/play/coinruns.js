/* books/algorithms/21: concentration. Flip a fair coin n times and count heads; repeat 2,000 times and draw how the
   counts spread. As n grows the share of heads crowds ever closer to one half, which is what Chernoff bounds promise.
   The flips are random, made here. */
PLAY("coinruns", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 240, st = k.stage(W, H), g = st.g, out = k.out(), n = 100;
  function draw() {
    var bins = new Array(41).fill(0), far = 0;
    for (var r = 0; r < 2000; r++) { var h = 0; for (var i = 0; i < n; i++) if (Math.random() < 0.5) h++; var f = h / n; bins[Math.round(f * 40)]++; if (Math.abs(f - 0.5) >= 0.1) far++; }
    var mx = Math.max.apply(null, bins); g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    bins.forEach(function (b, i) { var x = 20 + i * 13.5, h = b / mx * 160; g.fillStyle = Math.abs(i / 40 - 0.5) >= 0.1 ? C.red : C.ice; g.fillRect(x, 190 - h, 11, h); });
    g.fillStyle = C.ink3; g.font = F(16, 600); g.textAlign = "center"; [0, 0.25, 0.5, 0.75, 1].forEach(function (v) { g.fillText(v, 25 + v * 540, 212); }); g.fillText("share of heads", 300, 234);
    out.textContent = n + " flips per run: " + far + " of 2,000 runs (" + (far / 20).toFixed(1) + "%) landed 10 points or more from one half (red).";
  }
  k.slider("Flips per run", 10, 1000, 10, n, function (v) { return v; }, function (v) { n = +v; draw(); });
  k.buttons([["Run again", function () { draw(); }]]);
  st.draw = draw; draw();
});
