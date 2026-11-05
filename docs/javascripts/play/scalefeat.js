/* books/machine-learning/02: why scaling matters for distances. Houses described by area (square metres) and number of
   rooms (made up). Unscaled, area's big numbers decide the nearest neighbour on their own; standardised (each feature
   minus its mean, divided by its spread), both count. */
PLAY("scalefeat", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 260, st = k.stage(W, H), g = st.g, out = k.out(), sc = false;
  var D = [[120, 2, "A"], [124, 5, "B"], [180, 3, "C"], [90, 2, "D"], [150, 4, "E"]], Q = [122, 2];
  function draw() {
    var mx = [0, 0], sd = [0, 0], all = D.concat([[Q[0], Q[1]]]);
    all.forEach(function (p) { mx[0] += p[0] / all.length; mx[1] += p[1] / all.length; }); all.forEach(function (p) { sd[0] += Math.pow(p[0] - mx[0], 2) / all.length; sd[1] += Math.pow(p[1] - mx[1], 2) / all.length; }); sd = sd.map(Math.sqrt);
    function v(p) { return sc ? [(p[0] - mx[0]) / sd[0], (p[1] - mx[1]) / sd[1]] : [p[0], p[1]]; }
    var q = v(Q), best = 0, bd = 1e9; D.forEach(function (p, i) { var a = v(p), d = Math.hypot(a[0] - q[0], a[1] - q[1]); p.d = d; if (d < bd) { bd = d; best = i; } });
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H); g.textAlign = "left";
    g.fillStyle = C.ink; g.font = F(19, 700); g.fillText("new house: " + Q[0] + " m², " + Q[1] + " rooms", 20, 30);
    D.forEach(function (p, i) { var y = 56 + i * 36; g.fillStyle = i === best ? C.gold : C.ink2; g.font = F(18, i === best ? 700 : 500, "m"); g.fillText(p[2] + ": " + p[0] + " m², " + p[1] + " rooms", 20, y + 18); g.fillText("distance " + p.d.toFixed(2), 330, y + 18); });
    out.textContent = sc ? "Standardised: rooms count as much as area, and the nearest is " + D[best][2] + "." : "Unscaled: a difference of 1 room is worth 1 m², so area decides alone; the nearest is " + D[best][2] + ", with 3 more rooms.";
  }
  k.buttons([["Raw numbers", function () { sc = false; draw(); }], ["Standardised", function () { sc = true; draw(); }]], true);
  st.draw = draw; draw();
});
