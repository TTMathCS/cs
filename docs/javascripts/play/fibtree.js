/* foundations/recursion.md: the calls of a plain recursive fib(n) = fib(n−1) + fib(n−2), drawn as a tree. The same
   small values are worked out again and again: fib(n) makes 2·fib(n+1) − 1 calls. With a memo (remembering each answer)
   it makes about 2n. */
PLAY("fibtree", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 360, st = k.stage(W, H), g = st.g, out = k.out(), n = 6;
  function fib(m) { return m < 2 ? m : fib(m - 1) + fib(m - 2); }
  function draw(t) {
    var nodes = [], depth = 0;
    (function walk(m, x0, x1, d, px, py) { var x = (x0 + x1) / 2, y = 40 + d * 44; nodes.push([m, x, y, px, py]); depth = Math.max(depth, d);
      if (m >= 2) { var mid = x0 + (x1 - x0) * (fib(m) ? fib(m) / (fib(m) + fib(m - 1)) : 0.5); walk(m - 1, x0, mid, d + 1, x, y); walk(m - 2, mid, x1, d + 1, x, y); } })(n, 10, W - 10, 0, null, null);
    var show = Math.floor(t * nodes.length);
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    for (var i = 0; i < show; i++) { var q = nodes[i]; if (q[3] != null) { g.strokeStyle = C.line; g.lineWidth = 1.5; g.beginPath(); g.moveTo(q[3], q[4]); g.lineTo(q[1], q[2]); g.stroke(); } }
    for (i = 0; i < show; i++) { q = nodes[i]; var rep = q[0] === 2; g.fillStyle = rep ? C.gold : q[0] < 2 ? C.ink3 : C.rust; g.beginPath(); g.arc(q[1], q[2], 11, 0, 7); g.fill();
      g.font = F(12, 700, "m"); g.fillStyle = C.bg; g.textAlign = "center"; g.fillText(q[0], q[1], q[2] + 4); }
    g.textAlign = "left"; g.font = F(18, 600, "m"); g.fillStyle = C.ink; g.fillText(show + " calls", 14, H - 14);
    out.textContent = "fib(" + n + ") makes " + nodes.length + " calls; fib(2) alone, in gold, is worked out " + fib(n - 1) + " times. With a memo, about " + (2 * n - 1) + " calls.";
  }
  st.draw = function () { draw(film.t()); };
  var film = k.loop(10, draw, { start0: true, label: "Calls" });
  k.slider("n", 3, 8, 1, n, function (v) { return v; }, function (v) { n = v; film.set(film.t()); });
});
