/* books/machine-learning/15: XOR. The two red corners and two blue corners cannot be split by one straight line, however
   you turn it: at least one point is always wrong. A hidden layer of two units draws two lines, and the output unit
   combines them ("between the lines"), which separates them perfectly. */
PLAY("xorlines", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 280, st = k.stage(W, H), g = st.g, out = k.out(), ang = 30, off = 0, two = false;
  var P = [[0, 0, 0], [1, 1, 0], [0, 1, 1], [1, 0, 1]];
  function X(x) { return 170 + x * 220; } function Y(y) { return 225 - y * 170; }
  function draw() {
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H); var wrong = 0;
    if (two) {
      g.fillStyle = "rgba(217,96,59,0.22)"; g.beginPath(); [[-0.25, 0.75], [0.75, -0.25], [1.25, 0.25], [0.25, 1.25]].forEach(function (q, i) { if (i) g.lineTo(X(q[0]), Y(q[1])); else g.moveTo(X(q[0]), Y(q[1])); }); g.closePath(); g.fill();
      g.strokeStyle = C.gold; g.lineWidth = 3; [[[-0.25, 0.75], [0.75, -0.25]], [[0.25, 1.25], [1.25, 0.25]]].forEach(function (l) { g.beginPath(); g.moveTo(X(l[0][0]), Y(l[0][1])); g.lineTo(X(l[1][0]), Y(l[1][1])); g.stroke(); });
    } else {
      var t = ang * Math.PI / 180, nx = Math.cos(t), ny = Math.sin(t), c0 = 0.5 * nx + 0.5 * ny + off;
      P.forEach(function (p) { var side = p[0] * nx + p[1] * ny > c0 ? 1 : 0; if (side !== p[2]) wrong++; });
      var best = Math.min(wrong, 4 - wrong); if (best !== wrong) wrong = best;
      g.strokeStyle = C.gold; g.lineWidth = 3; g.beginPath(); g.moveTo(X(0.5 + off * nx - ny * 2), Y(0.5 + off * ny + nx * 2)); g.lineTo(X(0.5 + off * nx + ny * 2), Y(0.5 + off * ny - nx * 2)); g.stroke();
    }
    P.forEach(function (p) { g.fillStyle = p[2] ? C.red : C.earth; g.beginPath(); g.arc(X(p[0]), Y(p[1]), 16, 0, 7); g.fill(); g.fillStyle = C.ink; g.font = F(17, 700); g.textAlign = "center"; g.fillText(p[2], X(p[0]), Y(p[1]) + 6); });
    out.textContent = two ? "Two hidden units, two lines: red is the strip between them. All four points are right." : "One line: " + wrong + " point" + (wrong === 1 ? "" : "s") + " on the wrong side. No angle gets below 1.";
  }
  k.slider("Turn the line", 0, 179, 1, ang, function (v) { return v + "°"; }, function (v) { ang = +v; draw(); });
  k.slider("Shift the line", -0.6, 0.6, 0.05, off, function (v) { return (+v).toFixed(2); }, function (v) { off = +v; draw(); });
  k.buttons([["One line", function () { two = false; draw(); }], ["Two hidden units", function () { two = true; draw(); }]], true);
  st.draw = draw; draw();
});
