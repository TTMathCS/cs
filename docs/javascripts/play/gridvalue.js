/* books/ai/14: value iteration on a small grid world (made up): +1 at the goal, −1 in the pit, a small cost per move,
   and a move that slips sideways 20% of the time. Each sweep sets every square's value to the best expected reward of
   its moves; the arrows are the resulting policy. */
PLAY("gridvalue", function (fig, k) {
  var C = k.C, F = k.F, Wd = 4, Hd = 3, cs = 84, W = 600, H = 280, st = k.stage(W, H), g = st.g, out = k.out(), cost = 0.04, sl;
  var wall = "1,1", goal = "3,0", pit = "3,1", M = [[0, -1, "↑"], [1, 0, "→"], [0, 1, "↓"], [-1, 0, "←"]];
  function solve(sweeps) {
    var V = {}; for (var x = 0; x < Wd; x++) for (var y = 0; y < Hd; y++) V[x + "," + y] = 0; V[goal] = 1; V[pit] = -1; var P = {};
    function go(x, y, m) { var nx = x + m[0], ny = y + m[1], key = nx + "," + ny; return nx < 0 || nx >= Wd || ny < 0 || ny >= Hd || key === wall ? x + "," + y : key; }
    for (var s = 0; s < sweeps; s++) { var NV = {}; for (var key in V) { if (key === goal || key === pit || key === wall) { NV[key] = V[key]; continue; } var xy = key.split(",").map(Number), best = -9, bm = 0; M.forEach(function (m, i) { var side1 = M[(i + 1) % 4], side2 = M[(i + 3) % 4], q = -cost + 0.8 * V[go(xy[0], xy[1], m)] + 0.1 * V[go(xy[0], xy[1], side1)] + 0.1 * V[go(xy[0], xy[1], side2)]; if (q > best) { best = q; bm = i; } }); NV[key] = best; P[key] = bm; } V = NV; }
    return [V, P];
  }
  var sweeps = 25;
  function draw() {
    var r = solve(sweeps), V = r[0], P = r[1]; g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    for (var x = 0; x < Wd; x++) for (var y = 0; y < Hd; y++) {
      var key = x + "," + y, px = 40 + x * cs, py = 20 + y * cs, v = V[key];
      g.fillStyle = key === wall ? "#5a4434" : v >= 0 ? "rgba(159,201,138," + (0.1 + 0.6 * v) + ")" : "rgba(217,96,59," + (0.1 - 0.6 * v) + ")"; g.fillRect(px + 2, py + 2, cs - 4, cs - 4);
      if (key === wall) continue; g.fillStyle = C.ink; g.textAlign = "center"; g.font = F(18, 700, "m"); g.fillText(v.toFixed(2), px + cs / 2, py + cs / 2 + 26);
      if (key !== goal && key !== pit && P[key] !== undefined) { g.font = F(30, 700); g.fillText(M[P[key]][2], px + cs / 2, py + cs / 2 + 2); } else { g.font = F(26, 800); g.fillText(key === goal ? "+1" : "−1", px + cs / 2, py + cs / 2 + 2); }
    }
    out.textContent = "After " + sweeps + " sweep" + (sweeps > 1 ? "s" : "") + ": values spread out from the goal and the pit; the arrows point the best way from each square.";
  }
  k.slider("Sweeps", 1, 30, 1, sweeps, function (v) { return v; }, function (v) { sweeps = +v; draw(); });
  k.slider("Cost of each move", 0, 0.5, 0.01, cost, function (v) { return (+v).toFixed(2); }, function (v) { cost = +v; draw(); });
  st.draw = draw; draw();
});
