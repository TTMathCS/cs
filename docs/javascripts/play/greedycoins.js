/* books/algorithms/12: the cashier's greedy rule against the true fewest coins (found by dynamic programming), with this
   page's coin systems: Canadian-style 25, 10, 5, 1 where greedy is always right, and 4, 3, 1 where it can fail (6 =
   4 + 1 + 1 against 3 + 3). */
PLAY("greedycoins", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 230, st = k.stage(W, H), g = st.g, out = k.out(), amt = 6, coins = [4, 3, 1];
  function greedy(a) { var r = []; coins.forEach(function (c) { while (a >= c) { r.push(c); a -= c; } }); return r; }
  function best(a) { var D = [[]]; for (var x = 1; x <= a; x++) { var b = null; coins.forEach(function (c) { if (c <= x && D[x - c] && (!b || D[x - c].length + 1 < b.length)) b = D[x - c].concat([c]); }); D.push(b); } return D[a].sort(function (p, q) { return q - p; }); }
  function row(y, lab, L, col) { g.fillStyle = C.ink3; g.font = F(18, 600); g.textAlign = "left"; g.fillText(lab + ": " + L.length + " coins", 20, y); L.forEach(function (c, i) { var x = 40 + i * 52; g.fillStyle = col; g.beginPath(); g.arc(x, y + 34, 22, 0, 7); g.fill(); g.fillStyle = C.bg; g.font = F(18, 800); g.textAlign = "center"; g.fillText(c, x, y + 40); }); }
  function draw() { var a = greedy(amt), b = best(amt); g.fillStyle = C.bg; g.fillRect(0, 0, W, H); row(30, "greedy", a, a.length > b.length ? C.red : C.gold); row(130, "fewest", b, C.green); out.textContent = amt + " with coins " + coins.join(", ") + ": greedy uses " + a.length + ", the best is " + b.length + (a.length > b.length ? ". Greedy took the big coin and was stuck." : "."); }
  k.slider("Amount", 1, 30, 1, amt, function (v) { return v; }, function (v) { amt = +v; draw(); });
  k.buttons([["Coins 4, 3, 1", function () { coins = [4, 3, 1]; draw(); }], ["Coins 25, 10, 5, 1", function () { coins = [25, 10, 5, 1]; draw(); }]], true);
  st.draw = draw; draw();
});
