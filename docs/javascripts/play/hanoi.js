/* books/algorithms/03: the Towers of Hanoi. To move n discs, move n − 1 out of the way, move the biggest, move the n − 1
   back on top: 2^n − 1 moves in all. Choose the number of discs and press Play. */
PLAY("hanoi", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 260, st = k.stage(W, H), g = st.g, out = k.out(), N = 4, moves, film;
  function make() { moves = []; (function go(n, a, b, c) { if (!n) return; go(n - 1, a, c, b); moves.push([a, c, n]); go(n - 1, b, a, c); })(N, 0, 1, 2); }
  function draw(t) {
    var m = Math.min(moves.length, Math.floor(t * (moves.length + 0.999))), P = [[], [], []], i;
    for (i = N; i >= 1; i--) P[0].push(i); for (i = 0; i < m; i++) P[moves[i][1]].push(P[moves[i][0]].pop());
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    for (var p = 0; p < 3; p++) { var px = 110 + p * 190; g.fillStyle = C.ink3; g.fillRect(px - 3, 60, 6, 160); g.fillRect(px - 80, 220, 160, 6);
      P[p].forEach(function (d, j) { var w = 30 + d * (120 / N); g.fillStyle = [C.gold, C.ice, C.green, C.rust, C.mars, C.earth, "#d8b4f0", C.red][(d - 1) % 8]; g.fillRect(px - w / 2, 220 - (j + 1) * 18, w, 16); }); }
    g.textAlign = "left"; g.fillStyle = C.ink; g.font = F(20, 700); g.fillText("move " + m + " of " + moves.length, 20, 32);
    out.textContent = N + " discs need 2^" + N + " − 1 = " + moves.length + " moves." + (N >= 6 ? " With 64 discs, one move a second would take about 585 billion years." : "");
  }
  make(); film = k.loop(10, draw, { label: "Moves" });
  k.slider("Discs", 1, 8, 1, N, function (v) { return v; }, function (v) { N = +v; make(); draw(film.t()); });
  st.draw = function () { draw(film.t()); };
});
