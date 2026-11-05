/* books/machine-learning/19: attention as a table. For the word you tap, each bar is how much it attends to every word
   (one row of softmax(QKᵀ/√d)). These weights are made up to show the idea, the kind a trained head might learn: "it"
   looking back at what it refers to. */
PLAY("attnmap", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 260, st, out, sel = 7;
  var Wd = ["The", "rover", "crossed", "the", "dune", "because", "it", "was", "flat"];
  var S = { 6: [0.2, 3.2, 0.5, 0.2, 2.4, 0.3, 0.6, 0.1, 0.2], 7: [0.1, 0.6, 0.3, 0.1, 1.2, 0.2, 2.6, 0.8, 0.4], 8: [0.1, 0.4, 0.3, 0.2, 2.8, 0.2, 1.4, 1.2, 0.5], 2: [0.3, 2.8, 1.2, 0.2, 1.5, 0.1, 0.1, 0.1, 0.1] };
  st = k.stage(W, H, function (x, y) { var i = Math.floor((x - 15) / 63); if (i >= 0 && i < Wd.length) { sel = i; draw(); } });
  out = k.out(); var g = st.g;
  function row(i) { var s = S[i] || Wd.map(function (_, j) { return j === i ? 2 : 0.5 - Math.abs(i - j) * 0.05; }), e = s.map(Math.exp), t = e.reduce(function (a, b) { return a + b; }, 0); return e.map(function (v) { return v / t; }); }
  function draw() {
    var r = row(sel); g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    Wd.forEach(function (w, j) { var x = 15 + j * 63, h = r[j] * 300; g.fillStyle = j === sel ? C.ink3 : C.gold; g.fillRect(x + 8, 180 - h, 46, h); g.fillStyle = j === sel ? C.gold : C.ink; g.font = F(17, j === sel ? 800 : 600); g.textAlign = "center"; g.fillText(w, x + 31, 206); g.fillStyle = C.ink3; g.font = F(15, 600); g.fillText(Math.round(r[j] * 100) + "%", x + 31, 172 - h); });
    var top = 0; r.forEach(function (v, j) { if (j !== sel && v > r[top]) top = j; }); if (top === sel) top = (sel + 1) % Wd.length;
    out.textContent = "“" + Wd[sel] + "” attends most to “" + Wd[top] + "”. Tap another word.";
  }
  st.draw = draw; draw();
});
