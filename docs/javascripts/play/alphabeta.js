/* books/ai/06: minimax with alpha-beta pruning on a small game tree (the leaf values are made up). MAX picks the largest
   child, MIN the smallest. Once a branch cannot change the answer, its remaining leaves are skipped (crossed out). */
PLAY("alphabeta", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 290, st = k.stage(W, H), g = st.g, out = k.out();
  var L = [3, 12, 8, 2, 4, 6, 14, 5, 2], ev = [], vals = {}, seen = {}, cut = {};
  (function () {   // record the order in which alpha-beta looks at things
    var best = -1e9, alpha = -1e9;
    for (var b = 0; b < 3; b++) {
      var m = 1e9;
      for (var j = 0; j < 3; j++) { var i = b * 3 + j; ev.push(["leaf", i]); m = Math.min(m, L[i]); if (m <= alpha) { for (var r = j + 1; r < 3; r++) ev.push(["cut", b * 3 + r]); break; } }
      ev.push(["min", b, m]); best = Math.max(best, m); alpha = best; ev.push(["root", best]);
    }
  })();
  function draw(t) {
    var n = Math.ceil(t * ev.length), rootv = null, mins = {}, leaves = {}, cuts = {};
    ev.slice(0, n).forEach(function (e) { if (e[0] === "leaf") leaves[e[1]] = 1; if (e[0] === "cut") cuts[e[1]] = 1; if (e[0] === "min") mins[e[1]] = e[2]; if (e[0] === "root") rootv = e[1]; });
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    var rx = 300, ry = 40, mx = [110, 300, 490];
    for (var b = 0; b < 3; b++) {
      g.strokeStyle = C.line; g.lineWidth = 2; g.beginPath(); g.moveTo(rx, ry); g.lineTo(mx[b], 130); g.stroke();
      for (var j = 0; j < 3; j++) { var i = b * 3 + j, lx = mx[b] + (j - 1) * 55; g.strokeStyle = C.line; g.beginPath(); g.moveTo(mx[b], 130); g.lineTo(lx, 230); g.stroke();
        g.fillStyle = cuts[i] ? "rgba(217,96,59,0.2)" : leaves[i] ? C.ice : "rgba(244,230,212,0.12)"; g.fillRect(lx - 20, 214, 40, 34); g.fillStyle = cuts[i] ? C.red : C.bg; g.font = F(19, 700); g.textAlign = "center"; g.fillText(cuts[i] ? "✕" : leaves[i] ? L[i] : "?", lx, 238); }
      g.fillStyle = C.earth; g.beginPath(); g.moveTo(mx[b], 150); g.lineTo(mx[b] - 22, 112); g.lineTo(mx[b] + 22, 112); g.closePath(); g.fill(); g.fillStyle = C.ink; g.font = F(18, 700); g.fillText(b in mins ? mins[b] : "", mx[b], 132);
    }
    g.fillStyle = C.gold; g.beginPath(); g.moveTo(rx, 20); g.lineTo(rx - 24, 60); g.lineTo(rx + 24, 60); g.closePath(); g.fill(); g.fillStyle = C.bg; g.font = F(18, 700); g.fillText(rootv === null ? "" : rootv, rx, 54);
    g.textAlign = "left"; g.fillStyle = C.ink3; g.font = F(16, 600); g.fillText("▲ MAX   ▼ MIN", 20, 30);
    var nc = Object.keys(cuts).length; out.textContent = rootv !== null && n >= ev.length ? "MAX can get " + rootv + ". Alpha-beta skipped " + nc + " of the 9 leaves without changing the answer." : "Looking at leaves left to right…";
  }
  var film = k.loop(10, draw, { label: "Steps" });
  st.draw = function () { draw(film.t()); };
});
