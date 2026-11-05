/* books/ai/03: breadth-first against depth-first on the same grid, from the same start. BFS keeps a queue and spreads in
   rings; DFS keeps a stack and dives down one corridor before backing up. The numbers are the order each square is
   reached. */
PLAY("bfsdfs", function (fig, k) {
  var C = k.C, F = k.F, N = 7, cs = 34, W = 600, H = 270, st = k.stage(W, H), g = st.g, out = k.out(), dfs = false;
  function order() { var S = [3, 3], seen = {}, list = [S], ord = []; seen[S] = 1; while (list.length) { var c = dfs ? list.pop() : list.shift(); ord.push(c); [[0, -1], [1, 0], [0, 1], [-1, 0]].forEach(function (m) { var n = [c[0] + m[0], c[1] + m[1]]; if (n[0] < 0 || n[1] < 0 || n[0] >= N || n[1] >= N || seen[n]) return; seen[n] = 1; list.push(n); }); } return ord; }
  function draw(t) {
    var o = order(), n = Math.ceil(t * o.length); g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    for (var i = 0; i < N * N; i++) { var x = i % N, y = Math.floor(i / N); g.fillStyle = "rgba(244,230,212,0.07)"; g.fillRect(180 + x * cs + 1, 12 + y * cs + 1, cs - 2, cs - 2); }
    for (i = 0; i < n; i++) { var c = o[i]; g.fillStyle = i === 0 ? C.green : "rgba(" + (dfs ? "246,196,83" : "156,201,234") + "," + (1 - i / o.length * 0.7) + ")"; g.fillRect(180 + c[0] * cs + 1, 12 + c[1] * cs + 1, cs - 2, cs - 2); g.fillStyle = C.bg; g.font = F(15, 700); g.textAlign = "center"; g.fillText(i, 180 + c[0] * cs + cs / 2, 12 + c[1] * cs + cs / 2 + 5); }
    g.textAlign = "left"; g.fillStyle = C.ink; g.font = F(20, 700); g.fillText(dfs ? "depth-first" : "breadth-first", 20, 40); g.fillStyle = C.ink3; g.font = F(17, 600); g.fillText(dfs ? "a stack: last in, first out" : "a queue: first in, first out", 20, 66);
    out.textContent = dfs ? "Depth-first dives down one path and only backs up at a dead end." : "Breadth-first reaches every square at distance 1, then 2, then 3…";
  }
  var film = k.loop(9, draw, { label: "Order" });
  k.buttons([["Breadth-first", function () { dfs = false; film.set(0); film.play(); }], ["Depth-first", function () { dfs = true; film.set(0); film.play(); }]], true);
  st.draw = function () { draw(film.t()); };
});
