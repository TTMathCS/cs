/* books/algorithms/10: path compression. A find walks up to the root; afterwards every node it passed points straight at
   the root, so the next find from any of them takes one step. The chain of 8 nodes is made up. */
PLAY("unionfind", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 270, st = k.stage(W, H), g = st.g, out = k.out(), comp = false;
  function draw(t) {
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H); var n = 8, done = comp && t > 0.5, walk = Math.min(n - 1, Math.floor(t * 2 * n));
    var pos = []; for (var i = 0; i < n; i++) pos.push(done ? [80 + i * 62, i ? 190 : 50] : [80 + i * 62, 50 + i * 24]);
    if (done) pos[0] = [300, 50];
    for (i = 1; i < n; i++) { var to = done ? 0 : i - 1; g.strokeStyle = C.ink3; g.lineWidth = 2; g.beginPath(); g.moveTo(pos[i][0], pos[i][1]); g.lineTo(pos[to][0], pos[to][1]); g.stroke(); }
    for (i = 0; i < n; i++) { var lit = !done && n - 1 - i <= walk; g.fillStyle = i === 0 ? C.gold : lit ? C.red : C.ice; g.beginPath(); g.arc(pos[i][0], pos[i][1], 16, 0, 7); g.fill(); g.fillStyle = C.bg; g.font = F(16, 700); g.textAlign = "center"; g.fillText(i === 0 ? "root" : i, pos[i][0], pos[i][1] + 5); }
    out.textContent = done ? "After compression every node points at the root: the next find takes one step." : comp ? "find(7) walks up " + walk + " link" + (walk === 1 ? "" : "s") + "…" : "Without compression, every find(7) walks all 7 links, every time.";
  }
  var film = k.loop(6, draw, { label: "Find" });
  k.buttons([["With compression", function () { comp = true; film.set(0); film.play(); }], ["Without", function () { comp = false; film.set(0); film.play(); }]], true);
  comp = true; st.draw = function () { draw(film.t()); };
});
