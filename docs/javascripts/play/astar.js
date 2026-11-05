/* books/ai/04: A* against uniform-cost search on a grid with walls. Both find a shortest path; A* adds the straight-line
   (Manhattan) distance still to go, so it looks mostly toward the goal. Weighted A* trusts the guess more: fewer squares
   looked at, but the path may be longer. The walls are made up; tap to change them. */
PLAY("astar", function (fig, k) {
  var C = k.C, F = k.F, Wd = 20, Hd = 11, cs = 26, W = 600, H = 320, ox = 40, oy = 14, wall = {}, w = 1, st, out, film, S = [1, 5], G = [18, 5];
  [[6, 1], [6, 2], [6, 3], [6, 4], [6, 5], [6, 6], [6, 7], [12, 3], [12, 4], [12, 5], [12, 6], [12, 7], [12, 8], [12, 9], [12, 10], [9, 0], [9, 1], [9, 2], [15, 2], [15, 3], [15, 4], [15, 5]].forEach(function (c) { wall[c] = 1; });
  st = k.stage(W, H, function (x, y) { var c = [Math.floor((x - ox) / cs), Math.floor((y - oy) / cs)]; if (c[0] < 0 || c[0] >= Wd || c[1] < 0 || c[1] >= Hd || c + "" === S + "" || c + "" === G + "") return; wall[c] = !wall[c]; film.set(1); });
  out = k.out(); var g = st.g;
  function search(hw) {
    var open = [[S, 0]], gs = {}, from = {}, order = []; gs[S] = 0;
    while (open.length) {
      var bi = 0; for (var i = 1; i < open.length; i++) if (open[i][1] < open[bi][1]) bi = i;
      var c = open.splice(bi, 1)[0][0]; if (order.some(function (o) { return o + "" === c + ""; })) continue; order.push(c);
      if (c + "" === G + "") break;
      [[1, 0], [-1, 0], [0, 1], [0, -1]].forEach(function (m) { var n = [c[0] + m[0], c[1] + m[1]]; if (n[0] < 0 || n[0] >= Wd || n[1] < 0 || n[1] >= Hd || wall[n]) return; var ng = gs[c] + 1; if (!(n in gs) || ng < gs[n]) { gs[n] = ng; from[n] = c; open.push([n, ng + hw * (Math.abs(n[0] - G[0]) + Math.abs(n[1] - G[1])) + 1e-6 * (Math.abs(n[0] - G[0]) + Math.abs(n[1] - G[1]))]); } });
    }
    var path = []; if (G in from) { var p = G; while (p) { path.push(p + ""); p = from[p]; } }
    return { order: order, path: path };
  }
  function draw(t) {
    var r = search(w), n = Math.ceil(t * r.order.length), seen = {}; r.order.slice(0, n).forEach(function (c) { seen[c] = 1; });
    var done = n >= r.order.length; g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    for (var x = 0; x < Wd; x++) for (var y = 0; y < Hd; y++) { var c = [x, y]; g.fillStyle = wall[c] ? "#5a4434" : done && r.path.indexOf(c + "") >= 0 ? C.gold : seen[c] ? "rgba(156,201,234,0.45)" : "rgba(244,230,212,0.07)"; g.fillRect(ox + x * cs + 1, oy + y * cs + 1, cs - 2, cs - 2); }
    g.fillStyle = C.green; g.fillRect(ox + S[0] * cs + 4, oy + S[1] * cs + 4, cs - 8, cs - 8); g.fillStyle = C.red; g.fillRect(ox + G[0] * cs + 4, oy + G[1] * cs + 4, cs - 8, cs - 8);
    g.fillStyle = C.ink; g.font = F(19, 700); g.textAlign = "left"; g.fillText((w === 0 ? "uniform cost" : w === 1 ? "A*" : "weighted A* (×" + w + ")") + ": looked at " + n + (done ? ", path " + (r.path.length - 1) + " steps" : ""), ox, 312);
    out.textContent = done ? (w === 0 ? "Uniform cost spreads out in every direction." : w === 1 ? "A* heads for the goal and still finds a shortest path." : "Weighted A* looks at fewer squares; its path can be longer than the shortest.") + " " + n + " squares looked at." : "Searching…";
  }
  film = k.loop(8, draw, { label: "Search" });
  k.buttons([["A*", function () { w = 1; film.set(0); film.play(); }], ["Uniform cost", function () { w = 0; film.set(0); film.play(); }], ["Weighted A* ×3", function () { w = 3; film.set(0); film.play(); }]], true);
  st.draw = function () { draw(film.t()); };
});
