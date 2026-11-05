/* books/algorithms/22: why trying everything fails for the travelling salesman. A round trip through n cities can be
   made in (n − 1)!/2 different orders. Even checking a billion tours a second (a generous guess), the time explodes. */
PLAY("bruteforce", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 210, st = k.stage(W, H), g = st.g, out = k.out(), n = 10;
  function fact(m) { var r = 1; for (var i = 2; i <= m; i++) r *= i; return r; }
  function span(s) { var y = s / 3.156e7; if (s < 1) return "under a second"; if (s < 3600) return Math.round(s / 60) + " minutes"; if (s < 86400 * 2) return Math.round(s / 3600) + " hours"; if (y < 2) return Math.round(s / 86400) + " days"; if (y < 1e6) return Math.round(y).toLocaleString("en") + " years"; if (y < 1e9) return Math.round(y / 1e6).toLocaleString("en") + " million years"; return (y / 1e9).toLocaleString("en", { maximumFractionDigits: 0 }) + " billion years" + (y > 1.38e10 ? " (longer than the universe has existed)" : ""); }
  function draw() {
    var tours = fact(n - 1) / 2, s = tours / 1e9; g.fillStyle = C.bg; g.fillRect(0, 0, W, H); g.textAlign = "left";
    g.fillStyle = C.ink3; g.font = F(18, 600); g.fillText(n + " cities: different round trips", 20, 34);
    g.fillStyle = C.gold; g.font = F(30, 700); g.fillText(tours < 1e15 ? Math.round(tours).toLocaleString("en") : tours.toExponential(2).replace("e+", " × 10^"), 20, 76);
    g.fillStyle = C.ink3; g.font = F(18, 600); g.fillText("at a billion a second:", 20, 124);
    g.fillStyle = s > 3.156e7 ? C.red : C.ink; g.font = F(26, 700); g.fillText(span(s), 20, 162);
    out.textContent = "Each extra city multiplies the work by about n. That is why NP-hard problems are attacked with clever search, approximation and heuristics.";
  }
  k.slider("Cities", 4, 30, 1, n, function (v) { return v; }, function (v) { n = +v; draw(); });
  st.draw = draw; draw();
});
