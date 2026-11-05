/* books/algorithms/07: a Bloom filter. n items each set k bits out of m; a query for an item never added answers "maybe"
   only if all its k bits happen to be set. The chance is about (1 − e^(−kn/m))^k, best near k = (m/n)·ln 2. The bars
   compare that formula with a test of 2,000 random queries here. */
PLAY("bloom", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 240, st = k.stage(W, H), g = st.g, out = k.out(), bpi = 8, K = 4;
  function sim() { var n = 200, m = n * bpi, bits = new Uint8Array(m), s = 1, i, j; function rn() { s = (s * 16807) % 2147483647; return s; } for (i = 0; i < n; i++) for (j = 0; j < K; j++) bits[rn() % m] = 1; var fp = 0; for (i = 0; i < 2000; i++) { var all = true; for (j = 0; j < K; j++) if (!bits[rn() % m]) all = false; if (all) fp++; } var set = 0; for (i = 0; i < m; i++) set += bits[i]; return [fp / 2000, set / m]; }
  function draw() {
    var f = Math.pow(1 - Math.exp(-K / bpi), K), r = sim(), best = Math.max(1, Math.round(bpi * Math.LN2)); g.fillStyle = C.bg; g.fillRect(0, 0, W, H); g.textAlign = "left";
    g.fillStyle = C.ink3; g.font = F(18, 600); g.fillText("bits set: " + Math.round(r[1] * 100) + "%", 20, 30);
    [[f, "formula", C.gold], [r[0], "tested", C.ice]].forEach(function (b, i) { var y = 60 + i * 60, w = Math.min(540, Math.max(2, Math.sqrt(b[0]) * 540)); g.fillStyle = b[2]; g.fillRect(20, y, w, 34); g.fillStyle = C.ink; g.font = F(19, 700); g.fillText(b[1] + ": " + (b[0] * 100).toFixed(2) + "% false positives", 20, y + 56 - 4); });
    out.textContent = bpi + " bits per item and k = " + K + ": about " + (f * 100).toFixed(2) + "% false positives. The best k here is about " + best + ". (Bars on a square-root scale.)";
  }
  k.slider("Bits per item (m/n)", 2, 20, 1, bpi, function (v) { return v; }, function (v) { bpi = +v; draw(); });
  k.slider("Hash functions k", 1, 12, 1, K, function (v) { return v; }, function (v) { K = +v; draw(); });
  st.draw = draw; draw();
});
