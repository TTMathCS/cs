/* topics/Shortest-routes: the water idea from this page. Water poured at Home spreads along every road at the same
   speed and reaches each place in order of distance; the first time it reaches a place, it came the shortest way.
   Tap a place to make it the destination. The map and road lengths are made up. */
PLAY("water", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 290, st, out, film, dest = 5;
  var P = [[60, 150, "Home"], [200, 60, "Park"], [210, 230, "Shop"], [360, 140, "Library"], [500, 60, "Pool"], [530, 200, "School"]];
  var E = [[0, 1, 4], [0, 2, 3], [1, 2, 2], [1, 3, 5], [2, 3, 6], [1, 4, 9], [3, 4, 3], [3, 5, 4], [4, 5, 5], [2, 5, 11]];
  st = k.stage(W, H, function (x, y) { var b = 1, bd = 1e9; P.forEach(function (p, i) { var d = (p[0] - x) * (p[0] - x) + (p[1] - y) * (p[1] - y); if (i && d < bd) { bd = d; b = i; } }); dest = b; film.set(0); film.play(); });
  out = k.out(); var g = st.g;
  function dij() { var d = P.map(function () { return 1e9; }), from = [], done = []; d[0] = 0; for (var r = 0; r < P.length; r++) { var u = -1; d.forEach(function (v, i) { if (!done[i] && (u < 0 || v < d[u])) u = i; }); done[u] = 1; E.forEach(function (e) { var v = e[0] === u ? e[1] : e[1] === u ? e[0] : -1; if (v >= 0 && d[u] + e[2] < d[v]) { d[v] = d[u] + e[2]; from[v] = u; } }); } return [d, from]; }
  function draw(t) {
    var r = dij(), d = r[0], from = r[1], now = t * (d[dest] + 2), onPath = {};
    if (now >= d[dest]) { var c = dest; while (c) { onPath[c + "," + from[c]] = onPath[from[c] + "," + c] = 1; c = from[c]; } }
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    E.forEach(function (e) {
      var a = P[e[0]], b = P[e[1]], da = d[e[0]], db = d[e[1]];
      g.strokeStyle = onPath[e[0] + "," + e[1]] ? C.gold : C.line; g.lineWidth = onPath[e[0] + "," + e[1]] ? 6 : 3; g.beginPath(); g.moveTo(a[0], a[1]); g.lineTo(b[0], b[1]); g.stroke();
      [[e[0], e[1], da], [e[1], e[0], db]].forEach(function (s) { var f = Math.max(0, Math.min(1, (now - s[2]) / e[2])); if (f <= 0) return; var A = P[s[0]], B = P[s[1]]; g.strokeStyle = "rgba(156,201,234,0.75)"; g.lineWidth = 3; g.beginPath(); g.moveTo(A[0], A[1]); g.lineTo(A[0] + (B[0] - A[0]) * f, A[1] + (B[1] - A[1]) * f); g.stroke(); });
      g.fillStyle = C.bg; g.beginPath(); g.arc((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 12, 0, 7); g.fill(); g.fillStyle = C.ink2; g.font = F(17, 700); g.textAlign = "center"; g.fillText(e[2], (a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 6);
    });
    P.forEach(function (p, i) { var wet = d[i] <= now; g.fillStyle = i === dest ? C.red : wet ? C.ice : C.mars; g.beginPath(); g.arc(p[0], p[1], 14, 0, 7); g.fill(); g.fillStyle = C.ink; g.font = F(18, 700); g.textAlign = "center"; g.fillText(p[2] + (wet ? " " + d[i] : ""), p[0], p[1] + (p[1] < 140 || i === 5 ? -22 : 36)); });
    out.textContent = now >= d[dest] ? "Water reached " + P[dest][2] + " after " + d[dest] + ": that is the shortest route, in gold." : "The water has spread " + Math.floor(now) + " so far.";
  }
  film = k.loop(10, draw, { label: "Water" });
  st.draw = function () { draw(film.t()); };
});
