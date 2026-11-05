/* first-steps/06: nearest neighbour with the six fruits from this page's table. Tap anywhere to put a new fruit on the
   graph: the guess is the label of the closest example. Weight and yellowness are scaled so that 100 g counts like
   10 points of yellowness. */
PLAY("fruit", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 300, st, out, p = [110, 7];
  var D = [[180, 2, "apple"], [160, 3, "apple"], [200, 1, "apple"], [100, 9, "lemon"], [120, 8, "lemon"], [90, 10, "lemon"]];
  function X(w) { return 70 + (w - 60) / 160 * 500; } function Y(y) { return 250 - y * 22; }
  st = k.stage(W, H, function (x, y) { p = [Math.round(60 + (x - 70) / 500 * 160), Math.max(0, Math.min(10, Math.round((250 - y) / 22 * 2) / 2))]; draw(); });
  out = k.out(); var g = st.g;
  function draw() {
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    g.strokeStyle = C.line; g.beginPath(); g.moveTo(70, 20); g.lineTo(70, 250); g.lineTo(580, 250); g.stroke();
    g.fillStyle = C.ink3; g.font = F(16, 600); g.textAlign = "center"; g.fillText("weight (grams) →", 330, 284); [80, 120, 160, 200].forEach(function (w) { g.fillText(w, X(w), 268); });
    g.save(); g.translate(26, 140); g.rotate(-Math.PI / 2); g.fillText("yellowness →", 0, 0); g.restore();
    var best = 0, bd = 1e9; D.forEach(function (d, i) { var dd = Math.pow((d[0] - p[0]) / 10, 2) + Math.pow(d[1] - p[1], 2); if (dd < bd) { bd = dd; best = i; } });
    g.strokeStyle = C.ink; g.setLineDash([5, 5]); g.beginPath(); g.moveTo(X(p[0]), Y(p[1])); g.lineTo(X(D[best][0]), Y(D[best][1])); g.stroke(); g.setLineDash([]);
    D.forEach(function (d) { g.fillStyle = d[2] === "apple" ? C.red : C.gold; g.beginPath(); g.arc(X(d[0]), Y(d[1]), 11, 0, 7); g.fill(); });
    g.fillStyle = C.ink; g.beginPath(); g.arc(X(p[0]), Y(p[1]), 9, 0, 7); g.fill(); g.strokeStyle = C.ice; g.lineWidth = 3; g.stroke(); g.lineWidth = 1;
    g.textAlign = "left"; g.font = F(18, 700); g.fillStyle = C.red; g.fillText("● apples", 440, 36); g.fillStyle = C.gold; g.fillText("● lemons", 440, 62);
    out.textContent = "New fruit: " + p[0] + " g, yellowness " + p[1] + ". Closest example: " + D[best][2] + " (" + D[best][0] + " g, " + D[best][1] + "), so the guess is " + D[best][2] + ".";
  }
  st.draw = draw; draw();
});
