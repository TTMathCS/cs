/* books/ai/02: this page's light-time model. Both orbits as circles in one plane, Earth at 1 AU and Mars at 1.5237 AU;
   with θ the angle between them seen from the Sun, d = √(1 + 1.5237² − 2·1.5237·cos θ) AU, and the one-way time is d/c. */
PLAY("lighttime", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 280, st = k.stage(W, H), g = st.g, out = k.out(), th = 90;
  function draw() {
    var t = th * Math.PI / 180, aM = 1.5237, d = Math.sqrt(1 + aM * aM - 2 * aM * Math.cos(t)), km = d * 149.6e6, min = km / 299792.458 / 60;
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    var cx = 160, cy = 140, s = 78; g.strokeStyle = C.line; g.lineWidth = 1.5; g.beginPath(); g.arc(cx, cy, s, 0, 7); g.stroke(); g.beginPath(); g.arc(cx, cy, s * aM, 0, 7); g.stroke();
    g.fillStyle = C.gold; g.beginPath(); g.arc(cx, cy, 12, 0, 7); g.fill();
    var ex = cx + s, ey = cy, mx = cx + s * aM * Math.cos(t), my = cy - s * aM * Math.sin(t);
    g.strokeStyle = C.ink2; g.setLineDash([5, 5]); g.beginPath(); g.moveTo(ex, ey); g.lineTo(mx, my); g.stroke(); g.setLineDash([]);
    g.fillStyle = C.earth; g.beginPath(); g.arc(ex, ey, 9, 0, 7); g.fill(); g.fillStyle = C.mars; g.beginPath(); g.arc(mx, my, 8, 0, 7); g.fill();
    g.textAlign = "left"; g.fillStyle = C.ink; g.font = F(22, 700); g.fillText(Math.round(km / 1e6) + " million km", 330, 80);
    g.fillStyle = C.gold; g.font = F(26, 700); g.fillText(min.toFixed(1) + " min one way", 330, 124);
    g.fillStyle = C.ice; g.font = F(19, 600); g.fillText((2 * min).toFixed(0) + " min to ask and hear back", 330, 160);
    out.textContent = "Angle " + th + "°: " + d.toFixed(3) + " AU. A command and its answer take " + (2 * min).toFixed(0) + " minutes, so the rover must decide small things itself.";
  }
  k.slider("Angle between Earth and Mars", 0, 180, 1, th, function (v) { return v + "°"; }, function (v) { th = +v; draw(); });
  st.draw = draw; draw();
});
