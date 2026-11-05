/* foundations/big-o.md: how the common growth rates race. For n items, the number of steps each kind of algorithm
   takes, and how long that is at a billion simple steps a second (a round figure for one modern core). */
PLAY("growth", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 380, st = k.stage(W, H), g = st.g, out = k.out(), n = 1000;
  var R = [["O(log n)", function (n) { return Math.log2(n); }], ["O(n)", function (n) { return n; }], ["O(n log n)", function (n) { return n * Math.log2(n); }],
    ["O(n²)", function (n) { return n * n; }], ["O(2ⁿ)", function (n) { return Math.pow(2, n); }]];
  function t(s) { var Y = 3.156e7; return !isFinite(s) ? "forever" : s < 1e-6 ? Math.max(1, Math.round(s * 1e9)) + " ns" : s < 1e-3 ? Math.round(s * 1e6) + " µs" : s < 1 ? Math.round(s * 1e3) + " ms" : s < 60 ? s.toFixed(1) + " s" : s < 3600 ? Math.round(s / 60) + " min" : s < 86400 ? Math.round(s / 3600) + " h" : s < Y ? Math.round(s / 86400) + " days" : s < 1e12 * Y ? (s / Y).toPrecision(2) + " years" : "longer than the universe"; }
  function draw() {
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    g.font = F(26, 600, "d"); g.fillStyle = C.ink; g.fillText("n = " + n.toLocaleString("en"), 20, 36);
    R.forEach(function (r, i) { var steps = r[1](n), y = 70 + i * 52, frac = Math.min(1, Math.log10(Math.max(1, steps)) / 18);
      g.fillStyle = "rgba(244,230,212,0.08)"; g.fillRect(150, y, 420, 24); g.fillStyle = [C.green, C.ice, C.gold, C.rust, C.red][i]; g.fillRect(150, y, 420 * frac, 24);
      g.font = F(17, 600, "m"); g.fillStyle = C.ink; g.fillText(r[0], 20, y + 18); g.font = F(15, 600); g.fillStyle = C.ink; var tx = 150 + 420 * frac + 8; if (tx > 470) { tx = 158; g.fillStyle = C.bg; } g.fillText(t(steps / 1e9), tx, y + 18); });
    g.font = F(14, 500); g.fillStyle = C.ink3; g.fillText("bars: number of steps, on a scale that multiplies by ten at each step along", 20, H - 40);
  }
  st.draw = draw;
  k.slider("Items, n", 0, 600, 1, 300, function (v) { return Math.round(Math.pow(10, v / 100)).toLocaleString("en"); }, function (v) {
    n = Math.round(Math.pow(10, v / 100)); draw(); out.textContent = "At a billion steps a second, " + n.toLocaleString("en") + " items: n² takes " + t(n * n / 1e9) + ", n log n " + t(n * Math.log2(n) / 1e9) + "."; });
});
