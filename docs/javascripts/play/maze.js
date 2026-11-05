/* graphs/bfs.md: breadth-first search spreading through a grid, one layer at a time, like a ripple. Each square is a
   node joined to its four neighbours; dark squares are walls. When the ripple reaches the goal, following each square
   back to the one that found it gives a shortest path. Press New to draw new walls. */
PLAY("maze", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 400, st = k.stage(W, H), g = st.g, out = k.out(), CW = 30, RH = 20, wall, dist, from, order, S = [1, 1], T = [27, 17];
  function make() { for (var tries = 0; tries < 60; tries++) { build(); if (dist[T[1] * CW + T[0]] >= 0) return; } }
  function build() { wall = []; for (var y = 0; y < RH; y++) for (var x = 0; x < CW; x++) wall.push(x === 0 || y === 0 || x === CW - 1 || y === RH - 1 || Math.random() < 0.28);
    wall[S[1] * CW + S[0]] = wall[T[1] * CW + T[0]] = false;
    dist = new Array(CW * RH).fill(-1); from = new Array(CW * RH).fill(-1); order = []; var q = [S[1] * CW + S[0]]; dist[q[0]] = 0;
    while (q.length) { var c = q.shift(); order.push(c); [[1, 0], [-1, 0], [0, 1], [0, -1]].forEach(function (d) { var n = c + d[0] + d[1] * CW; if (!wall[n] && dist[n] < 0) { dist[n] = dist[c] + 1; from[n] = c; q.push(n); } }); } }
  function draw(t) {
    var s = 20, ox = 0, oy = 0, maxd = Math.max.apply(null, dist), now = t * (maxd + 4), goal = T[1] * CW + T[0];
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    for (var i = 0; i < CW * RH; i++) { var x = (i % CW) * s, y = Math.floor(i / CW) * s;
      if (wall[i]) { g.fillStyle = "#3a2117"; g.fillRect(x, y, s, s); continue; }
      if (dist[i] >= 0 && dist[i] <= now) { var f = dist[i] / Math.max(1, maxd); g.fillStyle = "rgba(156,201,234," + (0.65 - 0.45 * f) + ")"; g.fillRect(x + 1, y + 1, s - 2, s - 2); } }
    if (dist[goal] >= 0 && dist[goal] <= now) { g.strokeStyle = C.gold; g.lineWidth = 4; g.beginPath(); for (var c = goal; c >= 0; c = from[c]) g.lineTo((c % CW) * s + s / 2, Math.floor(c / CW) * s + s / 2); g.stroke(); }
    g.fillStyle = C.green; g.fillRect(S[0] * s + 3, S[1] * s + 3, s - 6, s - 6); g.fillStyle = C.gold; g.fillRect(T[0] * s + 3, T[1] * s + 3, s - 6, s - 6);
    out.textContent = dist[goal] < 0 ? "The walls cut the goal off: BFS visits everything it can reach and stops. Press New." :
      dist[goal] <= now ? "Found: the shortest path is " + dist[goal] + " steps. BFS reached every square at distance " + dist[goal] + " before going further." : "Layer " + Math.floor(now) + ": every square this many steps from the start.";
  }
  make(); st.draw = function () { draw(film.t()); };
  var film = k.loop(10, draw, { start0: true, label: "Time" });
  k.buttons([["New walls", function () { make(); film.set(0); film.play(); }]]);
});
