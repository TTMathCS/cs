/* books/algorithms/08: the same 15 keys put into a plain binary search tree in two orders. In random order the tree is
   bushy, about log n deep; in sorted order every key goes right and it becomes a list 15 deep. Balanced trees (AVL,
   red-black) rotate to stop that. */
PLAY("bstorder", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 290, st = k.stage(W, H), g = st.g, out = k.out(), sorted = false, keys;
  function make() { keys = []; for (var i = 1; i <= 15; i++) keys.push(i); if (!sorted) { var s = 4; for (i = 14; i > 0; i--) { s = (s * 16807) % 2147483647; var j = s % (i + 1), t = keys[i]; keys[i] = keys[j]; keys[j] = t; } } }
  function draw(t) {
    var n = Math.max(1, Math.ceil(t * 15)), root = null, depth = 0;
    function ins(nd, v, d) { if (!nd) { depth = Math.max(depth, d); return { v: v, l: null, r: null }; } if (v < nd.v) nd.l = ins(nd.l, v, d + 1); else nd.r = ins(nd.r, v, d + 1); return nd; }
    for (var i = 0; i < n; i++) root = ins(root, keys[i], 1);
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H); var dy = Math.min(50, 240 / Math.max(depth, 1));
    (function dr(nd, d) { if (!nd) return; var x = 20 + (nd.v - 0.5) * 37, y = 26 + (d - 1) * dy; [nd.l, nd.r].forEach(function (c) { if (c) { g.strokeStyle = C.line; g.lineWidth = 2; g.beginPath(); g.moveTo(x, y); g.lineTo(20 + (c.v - 0.5) * 37, y + dy); g.stroke(); } }); g.fillStyle = nd.v === keys[n - 1] ? C.gold : C.ice; g.beginPath(); g.arc(x, y, 13, 0, 7); g.fill(); g.fillStyle = C.bg; g.font = F(15, 700); g.textAlign = "center"; g.fillText(nd.v, x, y + 5); dr(nd.l, d + 1); dr(nd.r, d + 1); })(root, 1);
    out.textContent = (sorted ? "Sorted order" : "Random order") + ": " + n + " keys, depth " + depth + (sorted ? ". A search may walk past every key." : ". A search walks at most " + depth + " steps.");
  }
  make(); var film = k.loop(8, draw, { label: "Keys" });
  k.buttons([["Random order", function () { sorted = false; make(); film.set(0); film.play(); }], ["Sorted order", function () { sorted = true; make(); film.set(0); film.play(); }]], true);
  st.draw = function () { draw(film.t()); };
});
