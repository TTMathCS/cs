/* books/algorithms/06: counting sort. Count how many of each key there are, then write the keys out in order: no
   comparisons at all. Twelve made-up digits; press Play. */
PLAY("countsort", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 260, st = k.stage(W, H), g = st.g, out = k.out(), A = [3, 7, 1, 3, 9, 0, 7, 3, 5, 1, 7, 2];
  function draw(t) {
    var s = Math.floor(t * (2 * A.length + 0.999)), cnt = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], i, cw = 44;
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H); g.textAlign = "center";
    g.fillStyle = C.ink2; g.font = F(16, 700); g.textAlign = "left"; g.fillText("input", 20, 26); g.fillText("counts", 20, 116); g.fillText("output", 20, 206);
    g.textAlign = "center";
    for (i = 0; i < A.length; i++) { var on = s < A.length && i === s; g.fillStyle = i < Math.min(s, A.length) ? C.line : on ? C.gold : C.ink3; g.fillRect(80 + i * cw, 8, cw - 6, 32); g.fillStyle = C.bg; g.font = F(20, 800); g.fillText(A[i], 80 + i * cw + (cw - 6) / 2, 31); }
    for (i = 0; i < Math.min(s, A.length); i++) cnt[A[i]]++;
    for (var d = 0; d < 10; d++) { var x = 80 + d * 50; g.fillStyle = C.ink3; g.font = F(16, 600); g.fillText(d, x + 20, 80); g.fillStyle = cnt[d] ? C.ice : C.line; g.fillRect(x, 88, 40, 36); g.fillStyle = cnt[d] ? C.bg : C.ink3; g.font = F(20, 800); g.fillText(cnt[d], x + 20, 113); }
    var o = []; for (d = 0; d < 10; d++) for (i = 0; i < cnt[d]; i++) o.push(d); var shown = Math.max(0, s - A.length);
    for (i = 0; i < Math.min(shown, o.length); i++) { g.fillStyle = C.green; g.fillRect(80 + i * cw, 186, cw - 6, 32); g.fillStyle = C.bg; g.font = F(20, 800); g.fillText(o[i], 80 + i * cw + (cw - 6) / 2, 209); }
    out.textContent = s < A.length ? "Counting: one pass over the input adds 1 to the box of each key." : "Writing out: each key as many times as it was counted. " + Math.min(shown, o.length) + " of " + o.length + " written, 0 comparisons.";
  }
  var film = k.loop(9, draw, { label: "Steps" }); st.draw = function () { draw(film.t()); };
});
