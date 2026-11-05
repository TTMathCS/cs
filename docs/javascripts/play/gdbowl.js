/* books/machine-learning/05: gradient descent on a long, narrow bowl, f(x, y) = x² + 10y². Each step moves against the
   gradient by the learning rate times its size. Too small crawls; just right converges; too big bounces across the
   narrow direction and blows up (for this bowl, any rate above 0.1). Momentum smooths the zig-zag. */
PLAY("gdbowl", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 300, st = k.stage(W, H), g = st.g, out = k.out(), lr = 0.08, mom = false;
  function path() { var x = -4.5, y = 2.4, vx = 0, vy = 0, P = [[x, y]]; for (var i = 0; i < 40; i++) { var gx = 2 * x, gy = 20 * y; if (mom) { vx = 0.8 * vx - lr * 0.3 * gx; vy = 0.8 * vy - lr * 0.3 * gy; x += vx; y += vy; } else { x -= lr * gx; y -= lr * gy; } P.push([x, y]); if (Math.abs(x) > 50 || Math.abs(y) > 50) break; } return P; }
  function draw(t) {
    var P = path(), n = Math.max(1, Math.ceil(t * P.length)); g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    for (var c = 1; c <= 6; c++) { var r = c * c * 0.9; g.strokeStyle = "rgba(244,230,212," + (0.05 + c * 0.02) + ")"; g.beginPath(); g.ellipse(300, 150, Math.sqrt(r) * 55, Math.sqrt(r / 10) * 55, 0, 0, 7); g.stroke(); }
    g.strokeStyle = C.gold; g.lineWidth = 2.5; g.beginPath();
    for (var i = 0; i < n; i++) { var px = 300 + P[i][0] * 55, py = 150 - P[i][1] * 55; if (i) g.lineTo(px, py); else g.moveTo(px, py); } g.stroke();
    for (i = 0; i < n; i++) { g.fillStyle = i === n - 1 ? C.ink : C.gold; g.beginPath(); g.arc(300 + P[i][0] * 55, 150 - P[i][1] * 55, 4, 0, 7); g.fill(); }
    g.fillStyle = C.green; g.beginPath(); g.arc(300, 150, 6, 0, 7); g.fill();
    var e = P[n - 1], f = e[0] * e[0] + 10 * e[1] * e[1]; g.fillStyle = C.ink; g.font = F(19, 700); g.textAlign = "left"; g.fillText("step " + (n - 1) + "   loss " + (f > 1e4 ? "huge" : f.toFixed(3)), 20, 30);
    out.textContent = !isFinite(f) || f > 1e4 ? "Rate " + lr + ": each step overshoots further, and it blows up." : lr > 0.1 && !mom ? "Rate " + lr + ": bouncing across the narrow direction." : f < 0.01 ? "Reached the bottom (green) in " + (n - 1) + " steps." : "Rate " + lr + ": still going down.";
  }
  var film = k.loop(8, draw, { label: "Steps" });
  k.slider("Learning rate", 0.005, 0.11, 0.005, lr, function (v) { return (+v).toFixed(3); }, function (v) { lr = +(+v).toFixed(3); draw(film.t()); });
  k.buttons([["Plain", function () { mom = false; film.set(0); film.play(); }], ["With momentum", function () { mom = true; film.set(0); film.play(); }]], true);
  st.draw = function () { draw(film.t()); };
});
