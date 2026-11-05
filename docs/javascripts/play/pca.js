/* books/machine-learning/14: principal components. A cloud of points (made up) and the direction you choose; the bar
   shows how much of the spread the points keep when squashed onto that line. The first principal component is the
   direction that keeps the most; press Find it to turn to it. */
PLAY("pca", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 290, st = k.stage(W, H), g = st.g, out = k.out(), ang = 0, seed = 8, P = [], sl;
  function rnd() { seed = (seed * 16807) % 2147483647; return seed / 2147483647; }
  function gs() { return Math.sqrt(-2 * Math.log(rnd() + 1e-9)) * Math.cos(6.283 * rnd()); }
  for (var i = 0; i < 70; i++) { var a = gs() * 2.2, b = gs() * 0.6; P.push([a * 0.86 - b * 0.5, a * 0.5 + b * 0.86]); }
  var sxx = 0, syy = 0, sxy = 0; P.forEach(function (p) { sxx += p[0] * p[0]; syy += p[1] * p[1]; sxy += p[0] * p[1]; });
  var best = 0.5 * Math.atan2(2 * sxy, sxx - syy) * 180 / Math.PI, total = sxx + syy;
  function draw() {
    var t = ang * Math.PI / 180, ux = Math.cos(t), uy = Math.sin(t), keep = 0; g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    var cx = 230, cy = 145, s = 26;
    g.strokeStyle = C.gold; g.lineWidth = 2.5; g.beginPath(); g.moveTo(cx - ux * 220, cy + uy * 220); g.lineTo(cx + ux * 220, cy - uy * 220); g.stroke();
    P.forEach(function (p) { var d = p[0] * ux + p[1] * uy; keep += d * d; var qx = cx + d * ux * s, qy = cy - d * uy * s, px = cx + p[0] * s, py = cy - p[1] * s; g.strokeStyle = "rgba(244,230,212,0.2)"; g.lineWidth = 1; g.beginPath(); g.moveTo(px, py); g.lineTo(qx, qy); g.stroke(); g.fillStyle = C.ice; g.beginPath(); g.arc(px, py, 4, 0, 7); g.fill(); g.fillStyle = C.gold; g.beginPath(); g.arc(qx, qy, 3, 0, 7); g.fill(); });
    var share = keep / total; g.fillStyle = "rgba(244,230,212,0.1)"; g.fillRect(500, 50, 50, 160); g.fillStyle = C.gold; g.fillRect(500, 210 - 160 * share, 50, 160 * share);
    g.fillStyle = C.ink; g.font = F(20, 700); g.textAlign = "center"; g.fillText(Math.round(share * 100) + "%", 525, 38); g.font = F(16, 600); g.fillStyle = C.ink3; g.fillText("spread kept", 525, 234);
    out.textContent = "Direction " + Math.round(ang) + "°: the line keeps " + Math.round(share * 100) + "% of the spread." + (Math.abs(((ang - best) % 180 + 180) % 180) < 2 ? " This is the first principal component." : "");
  }
  sl = k.slider("Direction", 0, 179, 1, ang, function (v) { return v + "°"; }, function (v) { ang = +v; draw(); });
  k.buttons([["Find it", function () { sl.value = Math.round((best + 180) % 180); sl.dispatchEvent(new Event("input")); }]]);
  st.draw = draw; draw();
});
