/* topics/Sorting-and-searching: is sorting worth it? In a list of a million, a plain search looks at half the list on
   average; sorting once takes about n·log2(n) steps and then each binary search about log2(n) = 20. Slide the number
   of searches. Step counts are rough, ignoring constant factors. */
PLAY("sortfirst", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 220, st = k.stage(W, H), g = st.g, out = k.out(), q = 10, n = 1e6;
  function fmt(x) { return x >= 1e9 ? (x / 1e9).toFixed(1) + " thousand million" : x >= 1e6 ? (x / 1e6).toFixed(1) + " million" : Math.round(x).toLocaleString("en"); }
  function draw() {
    var plain = q * n / 2, sorted = n * Math.log2(n) + q * Math.log2(n), mx = Math.max(plain, sorted);
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H); g.textAlign = "left";
    [[plain, "search without sorting", C.red], [sorted, "sort once, then binary search", C.green]].forEach(function (r, i) {
      var y = 30 + i * 84; g.fillStyle = C.ink3; g.font = F(18, 600); g.fillText(r[1], 20, y);
      g.fillStyle = r[2]; g.fillRect(20, y + 10, Math.max(3, 560 * r[0] / mx), 28); g.fillStyle = C.ink; g.font = F(20, 700); g.fillText(fmt(r[0]) + " steps", 20, y + 64);
    });
    out.textContent = q + " search" + (q > 1 ? "es" : "") + " in a million items: " + (plain < sorted ? "just look; sorting is not worth it yet." : "sort first; it pays off from about 40 searches.");
  }
  k.slider("Number of searches", 1, 1000, 1, q, function (v) { return v; }, function (v) { q = +v; draw(); });
  st.draw = draw; draw();
});
