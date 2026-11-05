/* books/algorithms/02: the growth ladder. Move n and see how many steps lg n, n, n lg n, n² and 2ⁿ take, and how long
   each would run at this page's speed of 10⁹ steps per second. */
PLAY("growth", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 290, st = k.stage(W, H), g = st.g, out = k.out(), e = 6;
  var R = [["lg n", function (n) { return Math.log2(n); }, C.green], ["n", function (n) { return n; }, C.ice], ["n lg n", function (n) { return n * Math.log2(n); }, C.gold], ["n²", function (n) { return n * n; }, C.rust], ["2ⁿ", function (n) { return Math.pow(2, n); }, C.red]];
  function time(s) { s /= 1e9; if (s < 1e-6) return "under a microsecond"; if (s < 1e-3) return (s * 1e6).toFixed(0) + " µs"; if (s < 1) return (s * 1e3).toFixed(0) + " ms"; if (s < 120) return s.toFixed(0) + " s"; if (s < 7200) return (s / 60).toFixed(0) + " min"; if (s < 172800) return (s / 3600).toFixed(0) + " hours"; if (s < 3.15e7 * 2) return (s / 86400).toFixed(0) + " days"; var y = s / 3.156e7; return y < 1e6 ? Math.round(y).toLocaleString("en") + " years" : y < 1e300 ? "about 10^" + Math.floor(Math.log10(y)) + " years" : "longer than we can write"; }
  function draw() {
    var n = Math.pow(10, e); g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    g.textAlign = "left"; g.fillStyle = C.ink; g.font = F(20, 700); g.fillText("n = " + (e <= 6 ? n.toLocaleString("en") : "10^" + e), 20, 32);
    R.forEach(function (r, i) {
      var v = r[1](n), L = Math.log10(Math.max(v, 1)), w = Math.min(1, L / 30) * 220, y = 50 + i * 40;
      g.fillStyle = C.ink2; g.font = F(18, 700); g.fillText(r[0], 20, y + 20);
      g.fillStyle = r[2]; g.fillRect(100, y + 4, Math.max(3, w), 22);
      g.fillStyle = C.ink; g.font = F(17, 600); g.fillText(time(v), 100 + Math.max(3, w) + 10, y + 21);
    });
    g.fillStyle = C.ink3; g.font = F(15, 500); g.fillText("bar length: digits in the step count", 20, H - 14);
    out.textContent = "At 10⁹ steps a second, n = " + n.toLocaleString("en") + ": n lg n takes " + time(R[2][1](n)) + ", n² takes " + time(R[3][1](n)) + ".";
  }
  k.slider("n = 10 to the power", 1, 9, 1, e, function (v) { return v; }, function (v) { e = +v; draw(); });
  st.draw = draw; draw();
});
