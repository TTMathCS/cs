/* books/machine-learning/03: the dot product. Tap to move the tip of the blue vector b; a·b = |a||b|cos θ is positive
   when they point the same way, zero at a right angle and negative when they point apart. */
PLAY("dotprod", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 280, a = [3, 1], b = [1, 2.5], st, out, cx = 250, cy = 170, s = 40;
  st = k.stage(W, H, function (x, y) { b = [Math.round((x - cx) / s * 2) / 2, Math.round((cy - y) / s * 2) / 2]; draw(); });
  out = k.out(); var g = st.g;
  function arrow(v, c) { var x = cx + v[0] * s, y = cy - v[1] * s, an = Math.atan2(y - cy, x - cx); g.strokeStyle = c; g.fillStyle = c; g.lineWidth = 4; g.beginPath(); g.moveTo(cx, cy); g.lineTo(x, y); g.stroke(); g.beginPath(); g.moveTo(x, y); g.lineTo(x - 14 * Math.cos(an - 0.4), y - 14 * Math.sin(an - 0.4)); g.lineTo(x - 14 * Math.cos(an + 0.4), y - 14 * Math.sin(an + 0.4)); g.fill(); }
  function draw() {
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H); g.strokeStyle = C.line; g.lineWidth = 1;
    for (var i = -6; i <= 8; i++) { g.beginPath(); g.moveTo(cx + i * s, 0); g.lineTo(cx + i * s, H); g.stroke(); } for (i = -3; i <= 4; i++) { g.beginPath(); g.moveTo(0, cy - i * s); g.lineTo(W, cy - i * s); g.stroke(); }
    var d = a[0] * b[0] + a[1] * b[1], la = Math.hypot(a[0], a[1]), lb = Math.hypot(b[0], b[1]), th = lb ? Math.acos(Math.max(-1, Math.min(1, d / la / lb))) * 180 / Math.PI : 0;
    var p = d / la; g.strokeStyle = "rgba(246,196,83,0.6)"; g.setLineDash([5, 5]); g.beginPath(); g.moveTo(cx + b[0] * s, cy - b[1] * s); g.lineTo(cx + a[0] / la * p * s, cy - a[1] / la * p * s); g.stroke(); g.setLineDash([]);
    arrow(a, C.gold); arrow(b, C.ice);
    g.fillStyle = d > 0.01 ? C.green : d < -0.01 ? C.red : C.ink; g.font = F(22, 700); g.textAlign = "left"; g.fillText("a·b = " + a[0] + "×" + b[0] + " + " + a[1] + "×" + b[1] + " = " + d, 20, 34);
    out.textContent = "a = (3, 1), b = (" + b[0] + ", " + b[1] + "): angle " + Math.round(th) + "°, dot product " + d + (Math.abs(d) < 0.01 ? ", a right angle." : d > 0 ? ", pointing the same way." : ", pointing apart.");
  }
  st.draw = draw; draw();
});
