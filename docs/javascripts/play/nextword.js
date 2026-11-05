/* topics/Language-models: picking the next word. The model scores each possible next word; the temperature decides how
   adventurous the pick is: low always takes the top word, high spreads the chances out. The words and scores are made
   up to show the idea, as in the sketch on this page. */
PLAY("nextword", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 260, st = k.stage(W, H), g = st.g, out = k.out(), T = 1, text = "The cat sat on the";
  var Wd = [["mat", 5], ["floor", 3.8], ["sofa", 3.3], ["roof", 2.4], ["moon", 0.6], ["volcano", -0.5]];
  function probs() { var e = Wd.map(function (w) { return Math.exp(w[1] / Math.max(T, 0.05)); }), s = e.reduce(function (a, b) { return a + b; }, 0); return e.map(function (v) { return v / s; }); }
  function draw() {
    var p = probs(); g.fillStyle = C.bg; g.fillRect(0, 0, W, H); g.textAlign = "left";
    g.fillStyle = C.ink; g.font = F(20, 600); g.fillText(text + " …", 20, 32);
    Wd.forEach(function (w, i) {
      var y = 56 + i * 32; g.fillStyle = C.ink2; g.font = F(19, 600); g.textAlign = "right"; g.fillText(w[0], 120, y + 19);
      g.fillStyle = i === 0 ? C.gold : C.ice; g.fillRect(132, y + 2, 400 * p[i], 22); g.textAlign = "left"; g.fillStyle = C.ink; g.font = F(17, 600); g.fillText(Math.round(p[i] * 100) + "%", 140 + 400 * p[i], y + 19);
    });
    out.textContent = "Temperature " + T + ": “mat” is picked " + Math.round(p[0] * 100) + "% of the time, “volcano” " + (p[5] * 100 < 1 ? "under 1%" : Math.round(p[5] * 100) + "%") + ".";
  }
  k.slider("Temperature", 0.1, 3, 0.1, T, function (v) { return (+v).toFixed(1); }, function (v) { T = +v; draw(); });
  k.buttons([["Pick a word", function () { var p = probs(), r = Math.random(), i = 0; while (i < p.length - 1 && r > p[i]) { r -= p[i]; i++; } out.textContent = "Picked “" + Wd[i][0] + "”: " + text + " " + Wd[i][0] + "."; }]]);
  st.draw = draw; draw();
});
