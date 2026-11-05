/* first-steps/04: the numbering from this page on an 8 × 8 grid. 0 in the start, 1 next to it, 2 next to the 1s, and so
   on; then walk back from F, always to a number one smaller. Tap squares to add or remove walls. */
PLAY("ripple", function (fig, k) {
  var C = k.C, F = k.F, N = 8, cs = 34, W = 600, H = 300, ox = 160, oy = 14, st, out, film;
  var wall = {}, S = [0, 7], G = [7, 0];
  [[1, 1], [1, 2], [1, 3], [1, 4], [3, 6], [3, 5], [3, 4], [3, 3], [5, 1], [5, 2], [5, 3], [5, 4], [6, 6], [5, 6]].forEach(function (c) { wall[c] = 1; });
  st = k.stage(W, H, function (x, y) { var c = [Math.floor((x - ox) / cs), Math.floor((y - oy) / cs)]; if (c[0] < 0 || c[0] >= N || c[1] < 0 || c[1] >= N || c + "" === S + "" || c + "" === G + "") return; wall[c] = !wall[c]; draw(film.t()); });
  out = k.out(); var g = st.g;
  function bfs() { var d = {}, q = [S]; d[S] = 0; while (q.length) { var c = q.shift(); [[1, 0], [-1, 0], [0, 1], [0, -1]].forEach(function (m) { var n = [c[0] + m[0], c[1] + m[1]]; if (n[0] < 0 || n[0] >= N || n[1] < 0 || n[1] >= N || wall[n] || n in d) return; d[n] = d[c] + 1; q.push(n); }); } return d; }
  function draw(t) {
    var d = bfs(), max = 0; for (var key in d) max = Math.max(max, d[key]);
    var goal = d[G], now = t * ((goal === undefined ? max : goal) + 3);
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    var path = {}; if (goal !== undefined && now >= goal + 1) { var c = G; path[c] = 1; while (d[c] > 0) { var nb = [[1, 0], [-1, 0], [0, 1], [0, -1]].map(function (m) { return [c[0] + m[0], c[1] + m[1]]; }).filter(function (n) { return d[n] === d[c] - 1; })[0]; c = nb; path[c] = 1; } }
    for (var x = 0; x < N; x++) for (var y = 0; y < N; y++) {
      var p = [x, y], px = ox + x * cs, py = oy + y * cs, v = d[p];
      g.fillStyle = wall[p] ? "#5a4434" : path[p] ? C.gold : "rgba(244,230,212,0.08)"; g.fillRect(px + 1, py + 1, cs - 2, cs - 2);
      if (!wall[p] && v !== undefined && v <= now) { g.fillStyle = path[p] ? C.bg : C.ice; g.font = F(18, 700); g.textAlign = "center"; g.fillText(v, px + cs / 2, py + cs / 2 + 6); }
    }
    g.font = F(20, 800); g.textAlign = "center"; g.fillStyle = C.green; g.fillText("S", ox - 18, oy + S[1] * cs + 24); g.fillStyle = C.red; g.fillText("F", ox + N * cs + 18, oy + G[1] * cs + 24);
    out.textContent = goal === undefined ? "F never gets a number: the walls cut it off from S." : now >= goal + 1 ? "F got " + goal + ": walking back one smaller each time gives a shortest path, " + goal + " steps." : "Writing " + Math.floor(now) + " in every open square next to a " + Math.max(0, Math.floor(now) - 1) + "…";
  }
  film = k.loop(10, draw, { label: "Numbers" });
  st.draw = function () { draw(film.t()); };
});
