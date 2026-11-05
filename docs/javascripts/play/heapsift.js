/* books/algorithms/09: a binary min-heap in an array. Each new key goes in the next free slot and sifts up past any
   bigger parent. Made-up keys; press Play. */
PLAY("heapsift", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 300, st = k.stage(W, H), g = st.g, out = k.out(), K = [42, 17, 30, 8, 25, 12, 3, 20, 9, 14];
  var frames = [], h = [];
  K.forEach(function (x) { h.push(x); var i = h.length - 1; frames.push({ h: h.slice(), at: i, msg: "Add " + x + " at the end." });
    while (i > 0 && h[(i - 1) >> 1] > h[i]) { var p = (i - 1) >> 1, t = h[p]; h[p] = h[i]; h[i] = t; i = p; frames.push({ h: h.slice(), at: i, msg: x + " is smaller than its parent: swap up." }); } });
  frames.push({ h: h.slice(), at: -1, msg: "Done: the smallest key, " + h[0] + ", sits at the root, ready to take out." });
  function pos(i) { var d = Math.floor(Math.log2(i + 1)), j = i - (Math.pow(2, d) - 1), n = Math.pow(2, d); return [40 + (j + 0.5) * 520 / n, 34 + d * 64]; }
  function draw(t) {
    var f = frames[Math.min(frames.length - 1, Math.floor(t * frames.length))], a = f.h;
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H); g.strokeStyle = C.ink3; g.lineWidth = 2;
    for (var i = 1; i < a.length; i++) { var p = pos(i), q = pos((i - 1) >> 1); g.beginPath(); g.moveTo(p[0], p[1]); g.lineTo(q[0], q[1]); g.stroke(); }
    g.textAlign = "center"; for (i = 0; i < a.length; i++) { p = pos(i); g.fillStyle = i === f.at ? C.gold : C.ice; g.beginPath(); g.arc(p[0], p[1], 20, 0, 7); g.fill(); g.fillStyle = C.bg; g.font = F(18, 800); g.fillText(a[i], p[0], p[1] + 6); }
    var cw = 42; for (i = 0; i < 10; i++) { var x = 20 + i * cw; g.strokeStyle = C.line; g.strokeRect(x, 252, cw - 4, 32); if (i < a.length) { g.fillStyle = i === f.at ? C.gold : C.ink2; g.font = F(17, 800); g.fillText(a[i], x + (cw - 4) / 2, 274); } }
    out.textContent = f.msg;
  }
  var film = k.loop(16, draw, { label: "Steps" }); st.draw = function () { draw(film.t()); };
});
