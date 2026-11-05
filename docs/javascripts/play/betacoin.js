/* books/machine-learning/12: updating a belief about a coin. Start with a flat Beta(1, 1) prior on the chance of heads;
   after h heads and t tails the posterior is Beta(1 + h, 1 + t). Flip and watch the curve narrow around the truth. The
   hidden coin lands heads 70% of the time. */
PLAY("betacoin", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 250, st = k.stage(W, H), g = st.g, out = k.out(), h = 0, t = 0;
  function lbeta(a, b) { function lg(x) { var c = [76.18009172947146, -86.50532032941677, 24.01409824083091, -1.231739572450155, 0.1208650973866179e-2, -0.5395239384953e-5], y = x, tmp = x + 5.5, ser = 1.000000000190015; tmp -= (x + 0.5) * Math.log(tmp); for (var j = 0; j < 6; j++) ser += c[j] / ++y; return -tmp + Math.log(2.5066282746310005 * ser / x); } return lg(a) + lg(b) - lg(a + b); }
  function draw() {
    var a = 1 + h, b = 1 + t, lb = lbeta(a, b), pts = [], mx = 0;
    for (var x = 0.0025; x < 1; x += 0.005) { var y = Math.exp((a - 1) * Math.log(x) + (b - 1) * Math.log(1 - x) - lb); pts.push([x, y]); mx = Math.max(mx, y); }
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    g.strokeStyle = C.green; g.setLineDash([5, 5]); g.beginPath(); g.moveTo(30 + 0.7 * 540, 30); g.lineTo(30 + 0.7 * 540, 210); g.stroke(); g.setLineDash([]);
    g.fillStyle = "rgba(156,201,234,0.35)"; g.strokeStyle = C.ice; g.lineWidth = 3; g.beginPath(); g.moveTo(30, 210); pts.forEach(function (p) { g.lineTo(30 + p[0] * 540, 210 - p[1] / Math.max(mx, 1) * 170); }); g.lineTo(570, 210); g.fill(); g.stroke();
    g.fillStyle = C.ink3; g.font = F(16, 600); g.textAlign = "center"; [0, 0.5, 1].forEach(function (v) { g.fillText(v, 30 + v * 540, 232); }); g.fillStyle = C.green; g.fillText("true 0.7", 30 + 0.7 * 540, 24);
    g.fillStyle = C.ink; g.font = F(19, 700); g.textAlign = "left"; g.fillText(h + " heads, " + t + " tails", 20, 28);
    out.textContent = h + t === 0 ? "No flips yet: every chance from 0 to 1 looks equally likely." : "Posterior Beta(" + a + ", " + b + "): best guess " + ((a - 1) / (a + b - 2 || 1)).toFixed(2) + ", mean " + (a / (a + b)).toFixed(2) + ".";
  }
  function flip(n) { for (var i = 0; i < n; i++) { if (Math.random() < 0.7) h++; else t++; } draw(); }
  k.buttons([["Flip once", function () { flip(1); }], ["Flip 10", function () { flip(10); }], ["Flip 100", function () { flip(100); }], ["Start again", function () { h = t = 0; draw(); }]]);
  st.draw = draw; draw();
});
