/* books/machine-learning/10: many lines separate two groups; the SVM picks the one with the widest empty band around
   it. Drag the angle to try lines (each kept in the middle of the gap), or press Widest. Made-up points. */
PLAY("svmmargin", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 300, st = k.stage(W, H), g = st.g, out = k.out(), ang = 20, sl;
  var A = [[120, 80], [170, 60], [150, 130], [210, 110], [100, 150], [240, 70]], B = [[330, 220], [400, 190], [360, 260], [450, 240], [300, 270], [420, 140]];
  function fit(t) { var r = t * Math.PI / 180, w = [Math.cos(r), Math.sin(r)], pa = A.map(function (p) { return p[0] * w[0] + p[1] * w[1]; }), pb = B.map(function (p) { return p[0] * w[0] + p[1] * w[1]; });
    var hiA = Math.max.apply(0, pa), loB = Math.min.apply(0, pb); return { w: w, m: (loB - hiA) / 2, c: (loB + hiA) / 2 }; }
  var bestT = 0, bm = -1e9; for (var t = 0; t < 180; t += 0.25) { var f = fit(t); if (f.m > bm) { bm = f.m; bestT = t; } }
  function line(f, off, col, wd, dash) { var d = [-f.w[1], f.w[0]], c = f.c + off, p = [f.w[0] * c, f.w[1] * c]; g.strokeStyle = col; g.lineWidth = wd; g.setLineDash(dash || []); g.beginPath(); g.moveTo(p[0] - d[0] * 900, p[1] - d[1] * 900); g.lineTo(p[0] + d[0] * 900, p[1] + d[1] * 900); g.stroke(); g.setLineDash([]); }
  function draw() {
    var f = fit(ang); g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    if (f.m > 0) { g.save(); var d = [-f.w[1], f.w[0]]; g.fillStyle = C.gold; g.globalAlpha = 0.18; g.beginPath(); [[-f.m, -900], [-f.m, 900], [f.m, 900], [f.m, -900]].forEach(function (q, i) { var c = f.c + q[0], x = f.w[0] * c + d[0] * q[1], y = f.w[1] * c + d[1] * q[1]; i ? g.lineTo(x, y) : g.moveTo(x, y); }); g.fill(); g.restore();
      line(f, -f.m, C.gold, 1.5, [5, 5]); line(f, f.m, C.gold, 1.5, [5, 5]); }
    line(f, 0, f.m > 0 ? C.ink : C.red, 3);
    A.forEach(function (p) { g.fillStyle = C.ice; g.beginPath(); g.arc(p[0], p[1], 10, 0, 7); g.fill(); });
    B.forEach(function (p) { g.fillStyle = C.rust; g.fillRect(p[0] - 9, p[1] - 9, 18, 18); });
    g.textAlign = "left"; g.fillStyle = C.ink; g.font = F(19, 700); g.fillText(f.m > 0 ? "margin " + f.m.toFixed(0) + " (best " + bm.toFixed(0) + ")" : "this line cannot separate them", 20, 30);
    out.textContent = f.m > 0 ? (Math.abs(f.m - bm) < 0.5 ? "The widest band: the points touching its edges are the support vectors." : "This line separates the groups, but the empty band around it is narrower than it could be.") : "No line at this angle has all circles on one side and all squares on the other.";
  }
  sl = k.slider("Angle of the line", 0, 179, 1, ang, function (v) { return v + "°"; }, function (v) { ang = +v; draw(); });
  k.buttons([["Widest", function () { sl.value = Math.round(bestT); sl.dispatchEvent(new Event("input")); ang = bestT; draw(); }]]);
  st.draw = draw; draw();
});
