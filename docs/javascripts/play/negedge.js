/* books/algorithms/16: why Dijkstra needs non-negative weights. From S, Dijkstra settles A at distance 2 because it is
   closest, and never looks back; but the road S → B → A costs 5 − 4 = 1. Bellman-Ford relaxes every edge again and
   finds it. The tiny graph is made up. */
PLAY("negedge", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 250, st = k.stage(W, H), g = st.g, out = k.out(), alg = 0;
  var P = { S: [80, 130], A: [300, 50], B: [300, 210], T: [520, 130] }, E = [["S", "A", 2], ["S", "B", 5], ["B", "A", -4], ["A", "T", 3]];
  function draw() {
    var d = alg === 0 ? { S: 0, A: 2, B: 5, T: 5 } : { S: 0, A: 1, B: 5, T: 4 }, used = alg === 0 ? ["S-A", "A-T"] : ["S-B", "B-A", "A-T"];
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    E.forEach(function (e) { var a = P[e[0]], b = P[e[1]], on = used.indexOf(e[0] + "-" + e[1]) >= 0; g.strokeStyle = on ? C.gold : C.line; g.lineWidth = on ? 5 : 3; g.beginPath(); g.moveTo(a[0], a[1]); g.lineTo(b[0], b[1]); g.stroke(); var mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2; g.fillStyle = C.bg; g.beginPath(); g.arc(mx, my, 16, 0, 7); g.fill(); g.fillStyle = e[2] < 0 ? C.red : C.ink; g.font = F(19, 700); g.textAlign = "center"; g.fillText(e[2], mx, my + 6); });
    for (var key in P) { g.fillStyle = C.ice; g.beginPath(); g.arc(P[key][0], P[key][1], 20, 0, 7); g.fill(); g.fillStyle = C.bg; g.font = F(18, 800); g.fillText(key, P[key][0], P[key][1] + 6); g.fillStyle = C.gold; g.font = F(18, 700); g.fillText(d[key], P[key][0], P[key][1] + (key === "B" ? 46 : -28)); }
    out.textContent = alg === 0 ? "Dijkstra settles A at 2 and T at 5, and never revisits A: wrong." : "Bellman-Ford relaxes every edge again: A is really 1 (via B) and T is 4.";
  }
  k.buttons([["Dijkstra", function () { alg = 0; draw(); }], ["Bellman-Ford", function () { alg = 1; draw(); }]], true);
  st.draw = draw; draw();
});
