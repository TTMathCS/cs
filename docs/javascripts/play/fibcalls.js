/* books/algorithms/13: plain recursive Fibonacci makes C(n) = 2F(n+1) − 1 calls (this page's claim), while the memo
   version solves each of the n + 1 subproblems once. Move n and compare. */
PLAY("fibcalls", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 220, st = k.stage(W, H), g = st.g, out = k.out(), n = 5;
  function fib(m) { var a = 0, b = 1; for (var i = 0; i < m; i++) { var t = a + b; a = b; b = t; } return a; }
  function draw() {
    var plain = 2 * fib(n + 1) - 1, memo = n + 1, L = Math.log10(plain);
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H); g.textAlign = "left";
    g.fillStyle = C.ink; g.font = F(20, 700); g.fillText("F" + n + " = " + fib(n).toLocaleString("en"), 20, 34);
    g.fillStyle = C.ink2; g.font = F(18, 700); g.fillText("plain recursion", 20, 80); g.fillText("with a memo", 20, 150);
    g.fillStyle = C.rust; g.fillRect(20, 90, Math.max(4, 560 * Math.min(1, L / 13)), 22);
    g.fillStyle = C.green; g.fillRect(20, 160, Math.max(4, 560 * Math.log10(memo) / 13), 22);
    g.fillStyle = C.ink; g.font = F(18, 700); g.textAlign = "right";
    g.fillText(plain.toLocaleString("en") + " calls", 580, 80); g.fillText(memo + " calls", 580, 150);
    out.textContent = "F" + n + ": " + plain.toLocaleString("en") + " calls against " + memo + (plain > memo ? ", " + Math.round(plain / memo).toLocaleString("en") + " times as many." : ".") + " (Bar length: digits.)";
  }
  k.slider("n", 1, 60, 1, n, function (v) { return v; }, function (v) { n = +v; draw(); });
  st.draw = draw; draw();
});
