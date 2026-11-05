/* books/algorithms/17: Edmonds-Karp on this page's network (Figure 17.2). Each step finds the shortest path with spare
   room, pushes its bottleneck, and repeats until no path is left: the flow is then 15, the same as the minimum cut. */
PLAY("maxflow", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 290, st = k.stage(W, H), g = st.g, out = k.out();
  var N = { s: [50, 150], a: [190, 55], b: [190, 245], c: [370, 55], d: [370, 245], t: [520, 150] };
  var E = [["s", "a", 10], ["s", "b", 8], ["a", "b", 2], ["a", "c", 5], ["b", "d", 10], ["c", "b", 7], ["c", "t", 7], ["d", "c", 6], ["d", "t", 10]];
  var f = E.map(function () { return 0; }), frames = [{ f: f.slice(), p: [], msg: "No flow yet. Press Play to push along shortest paths with room." }], total = 0;
  while (true) {
    var prev = { s: null }, Q = ["s"];
    while (Q.length && !("t" in prev)) { var u = Q.shift(); E.forEach(function (e, i) { if (e[0] === u && f[i] < e[2] && !(e[1] in prev)) { prev[e[1]] = [i, 1]; Q.push(e[1]); } if (e[1] === u && f[i] > 0 && !(e[0] in prev)) { prev[e[0]] = [i, -1]; Q.push(e[0]); } }); }
    if (!("t" in prev)) break;
    var path = [], v = "t", b = 1e9; while (v !== "s") { var pe = prev[v]; path.push(pe); b = Math.min(b, pe[1] > 0 ? E[pe[0]][2] - f[pe[0]] : f[pe[0]]); v = pe[1] > 0 ? E[pe[0]][0] : E[pe[0]][1]; }
    path.forEach(function (pe) { f[pe[0]] += pe[1] * b; }); total += b;
    frames.push({ f: f.slice(), p: path.map(function (pe) { return pe[0]; }), msg: "Path of " + (path.length) + " edges, bottleneck " + b + ": flow is now " + total + "." });
  }
  frames.push({ f: f.slice(), p: [], msg: "No path with room is left: the maximum flow is " + total + ", equal to the cut s→b, a→b, a→c (8 + 2 + 5)." });
  function draw(t) {
    var fr = frames[Math.min(frames.length - 1, Math.floor(t * frames.length))];
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    E.forEach(function (e, i) { var A = N[e[0]], B = N[e[1]], dx = B[0] - A[0], dy = B[1] - A[1], L = Math.hypot(dx, dy), ux = dx / L, uy = dy / L, x1 = A[0] + ux * 22, y1 = A[1] + uy * 22, x2 = B[0] - ux * 24, y2 = B[1] - uy * 24, on = fr.p.indexOf(i) >= 0;
      g.strokeStyle = on ? C.gold : fr.f[i] ? C.rust : C.ink3; g.lineWidth = on ? 5 : 2 + 4 * fr.f[i] / e[2]; g.beginPath(); g.moveTo(x1, y1); g.lineTo(x2, y2); g.stroke();
      g.fillStyle = g.strokeStyle; g.beginPath(); g.moveTo(x2, y2); g.lineTo(x2 - ux * 12 - uy * 7, y2 - uy * 12 + ux * 7); g.lineTo(x2 - ux * 12 + uy * 7, y2 - uy * 12 - ux * 7); g.fill();
      var mx = (x1 + x2) / 2 - uy * 16, my = (y1 + y2) / 2 + ux * 16 + 6; g.fillStyle = C.ink; g.font = F(17, 700); g.textAlign = "center"; g.fillText(fr.f[i] + "/" + e[2], mx, my); });
    Object.keys(N).forEach(function (n) { g.fillStyle = n === "s" || n === "t" ? C.green : C.ice; g.beginPath(); g.arc(N[n][0], N[n][1], 20, 0, 7); g.fill(); g.fillStyle = C.bg; g.font = F(20, 800); g.fillText(n, N[n][0], N[n][1] + 7); });
    out.textContent = fr.msg;
  }
  var film = k.loop(10, draw, { label: "Steps" }); st.draw = function () { draw(film.t()); };
});
