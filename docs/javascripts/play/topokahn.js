/* books/algorithms/15: a topological order of this page's course graph, found by repeatedly taking a course with no
   unmet prerequisite (Kahn's method). Press Play. */
PLAY("topokahn", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 300, st = k.stage(W, H), g = st.g, out = k.out();
  var N = { intro: [70, 60], discrete: [70, 200], data: [210, 130], algos: [350, 70], systems: [350, 200], theory: [500, 50], compilers: [500, 170] };
  var E = [["intro", "data"], ["discrete", "data"], ["data", "algos"], ["data", "systems"], ["algos", "theory"], ["algos", "compilers"], ["systems", "compilers"], ["discrete", "theory"]];
  var indeg = {}, order = [], Q = []; Object.keys(N).forEach(function (n) { indeg[n] = 0; }); E.forEach(function (e) { indeg[e[1]]++; });
  Object.keys(N).forEach(function (n) { if (!indeg[n]) Q.push(n); });
  while (Q.length) { var u = Q.shift(); order.push(u); E.forEach(function (e) { if (e[0] === u && !--indeg[e[1]]) Q.push(e[1]); }); }
  function draw(t) {
    var m = Math.min(order.length, Math.floor(t * (order.length + 0.999))), done = order.slice(0, m);
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    E.forEach(function (e) { var A = N[e[0]], B = N[e[1]], dx = B[0] - A[0], dy = B[1] - A[1], L = Math.hypot(dx, dy), ux = dx / L, uy = dy / L, x2 = B[0] - ux * 44, y2 = B[1] - uy * 22;
      g.strokeStyle = done.indexOf(e[0]) >= 0 ? C.line : C.ink3; g.lineWidth = 2; g.beginPath(); g.moveTo(A[0] + ux * 44, A[1] + uy * 22); g.lineTo(x2, y2); g.stroke();
      g.fillStyle = g.strokeStyle; g.beginPath(); g.moveTo(x2, y2); g.lineTo(x2 - ux * 10 - uy * 6, y2 - uy * 10 + ux * 6); g.lineTo(x2 - ux * 10 + uy * 6, y2 - uy * 10 - ux * 6); g.fill(); });
    Object.keys(N).forEach(function (n) { var i = done.indexOf(n), ready = i < 0 && E.every(function (e) { return e[1] !== n || done.indexOf(e[0]) >= 0; });
      g.fillStyle = i >= 0 ? C.green : ready ? C.gold : C.ice; g.beginPath(); g.ellipse(N[n][0], N[n][1], 50, 20, 0, 0, 7); g.fill(); g.fillStyle = C.bg; g.font = F(16, 800); g.textAlign = "center"; g.fillText(n, N[n][0], N[n][1] + 6); });
    g.textAlign = "left"; g.fillStyle = C.ink; g.font = F(17, 700); var L = done.map(function (n, i) { return (i + 1) + "." + n; }); g.fillText(L.slice(0, 4).join(" "), 20, 250); g.fillText(L.slice(4).join(" "), 20, 278);
    out.textContent = m < order.length ? "Gold: every prerequisite is done, so it can be taken next. Taken so far: " + m + "." : "One valid order: " + order.join(", ") + ". Every arrow points forward in it.";
  }
  var film = k.loop(8, draw, { label: "Steps" }); st.draw = function () { draw(film.t()); };
});
