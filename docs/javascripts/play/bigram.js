/* books/ai/16: a bigram language model. It counts which word follows which in a tiny text (written for this page), then
   writes by picking each next word in proportion to those counts. It sounds locally right and globally aimless, which
   is what n-gram models do. */
PLAY("bigram", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 230, st = k.stage(W, H), g = st.g, out = k.out(), text = "", last = "the";
  var corpus = "the rover drives to the crater . the rover takes a picture of the rock . the dust covers the panels . the wind cleans the panels . the rover drives to the hill . a picture of the hill goes to earth . the team on earth looks at the picture .";
  var T = {}, w = corpus.split(" "); for (var i = 0; i + 1 < w.length; i++) { (T[w[i]] = T[w[i]] || {})[w[i + 1]] = (T[w[i]][w[i + 1]] || 0) + 1; }
  function next(a) { var o = T[a] || T["."], tot = 0, r; for (var b in o) tot += o[b]; r = Math.random() * tot; for (b in o) { r -= o[b]; if (r < 0) return b; } return "."; }
  function wrap(s, n) { var L = [], cur = ""; s.split(" ").forEach(function (x) { if ((cur + " " + x).length > n) { L.push(cur); cur = x; } else cur = cur ? cur + " " + x : x; }); if (cur) L.push(cur); return L; }
  function draw() {
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H); g.textAlign = "left";
    g.fillStyle = C.ink3; g.font = F(17, 600); g.fillText("after “" + last + "” it has seen:", 20, 28);
    var o = T[last] || {}, tot = 0, b; for (b in o) tot += o[b]; var x = 20; g.font = F(17, 700);
    for (b in o) { var s = b + " " + Math.round(o[b] / tot * 100) + "%"; g.fillStyle = C.gold; g.fillText(s, x, 54); x += g.measureText(s).width + 16; if (x > 560) break; }
    g.fillStyle = C.ink; g.font = F(20, 600); wrap(text || "(press Next word)", 48).slice(-5).forEach(function (l, i) { g.fillText(l, 20, 96 + i * 28); });
  }
  k.buttons([["Next word", function () { var n = next(last); text += (text ? " " : "") + n; last = n; draw(); out.textContent = ""; }], ["Write 20", function () { for (var i = 0; i < 20; i++) { var n = next(last); text += (text ? " " : "") + n; last = n; } draw(); }], ["Start again", function () { text = ""; last = "the"; draw(); }]]);
  out.textContent = "Its whole knowledge is the table of which word followed which.";
  st.draw = draw; draw();
});
