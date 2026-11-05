/* books/algorithms/23: the vertex-cover 2-approximation. Take any edge not yet covered, put both of its ends in the
   cover, repeat. The picked edges share no ends, so the best cover needs one end of each: we are at most twice the best.
   A small made-up graph; press Play. */
PLAY("vcover", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 270, st = k.stage(W, H), g = st.g, out = k.out();
  var V = [[80, 60], [220, 50], [360, 60], [500, 70], [100, 200], [240, 160], [380, 200], [520, 190]];
  var E = [[0, 1], [1, 2], [2, 3], [0, 4], [1, 5], [5, 4], [5, 6], [2, 6], [6, 7], [3, 7], [5, 2]];
  var frames = [], cov = [], picked = [];
  E.forEach(function (e, i) { if (cov.indexOf(e[0]) < 0 && cov.indexOf(e[1]) < 0) { picked.push(i); cov.push(e[0], e[1]); frames.push({ c: cov.slice(), p: picked.slice() }); } });
  var best = 99; for (var m = 0; m < 256; m++) { var ok = E.every(function (e) { return (m >> e[0] & 1) || (m >> e[1] & 1); }); if (ok) { var b = 0; for (var i = 0; i < 8; i++) b += m >> i & 1; best = Math.min(best, b); } }
  function draw(t) {
    var n = Math.min(frames.length, Math.floor(t * (frames.length + 0.999))), f = n ? frames[n - 1] : { c: [], p: [] };
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    E.forEach(function (e, i) { var cv = f.c.indexOf(e[0]) >= 0 || f.c.indexOf(e[1]) >= 0; g.strokeStyle = f.p.indexOf(i) >= 0 ? C.gold : cv ? C.green : C.ink3; g.lineWidth = f.p.indexOf(i) >= 0 ? 6 : 3; g.beginPath(); g.moveTo(V[e[0]][0], V[e[0]][1]); g.lineTo(V[e[1]][0], V[e[1]][1]); g.stroke(); });
    V.forEach(function (v, i) { g.fillStyle = f.c.indexOf(i) >= 0 ? C.rust : C.ice; g.beginPath(); g.arc(v[0], v[1], 16, 0, 7); g.fill(); });
    g.textAlign = "left"; g.fillStyle = C.ink; g.font = F(18, 700); g.fillText("cover: " + f.c.length + " vertices", 20, 252);
    out.textContent = n < frames.length ? "Picked " + f.p.length + " uncovered edges (gold); both ends join the cover (red)." : "Every edge covered with " + f.c.length + " vertices. The best possible here is " + best + ", and " + f.c.length + " ≤ 2 × " + best + ".";
  }
  var film = k.loop(6, draw, { label: "Steps" }); st.draw = function () { draw(film.t()); };
});
