/* first-steps/02: the two card methods on this page, counting every comparison. Method A (pick the smallest) is
   selection sort and always makes 28 comparisons for 8 cards; Method B (slide into place) is insertion sort, which
   needs far fewer when the cards are almost in order. */
PLAY("cardsort", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 220, st = k.stage(W, H), g = st.g, out = k.out(), method = 0, start = [5, 2, 8, 1, 7, 3, 6, 4], frames;
  function run() {
    var a = start.slice(), f = [], c = 0, i, j;
    f.push([a.slice(), -1, -1, 0, -1]);
    if (method === 0) for (i = 0; i < 8; i++) { var m = i; for (j = i + 1; j < 8; j++) { c++; if (a[j] < a[m]) m = j; f.push([a.slice(), j, m, c, i]); } var t = a[i]; a[i] = a[m]; a[m] = t; f.push([a.slice(), i, i, c, i + 1]); }
    else for (i = 1; i < 8; i++) { j = i; while (j > 0) { c++; f.push([a.slice(), j - 1, j, c, i]); if (a[j - 1] > a[j]) { var u = a[j]; a[j] = a[j - 1]; a[j - 1] = u; j--; f.push([a.slice(), j, j, c, i]); } else break; } }
    f.push([a.slice(), -1, -1, c, 8]); return f;
  }
  function draw(t) {
    var fr = frames[Math.min(frames.length - 1, Math.floor(t * frames.length))];
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    fr[0].forEach(function (v, i) {
      var x = 30 + i * 68, hot = i === fr[1] || i === fr[2], done = method === 0 ? i < fr[4] : false;
      g.fillStyle = hot ? C.gold : done ? C.green : "#f4e6d4"; g.fillRect(x, 50, 56, 80); g.strokeStyle = C.bg; g.strokeRect(x, 50, 56, 80);
      g.fillStyle = C.bg; g.font = F(34, 700); g.textAlign = "center"; g.fillText(v, x + 28, 102);
    });
    g.textAlign = "left"; g.fillStyle = C.ink; g.font = F(22, 700); g.fillText("comparisons: " + fr[3], 30, 180);
    g.fillStyle = C.ink3; g.font = F(18, 500); g.fillText(method === 0 ? "Method A: pick the smallest" : "Method B: slide into place", 30, 32);
    out.textContent = t >= 1 ? (method === 0 ? "Method A: " : "Method B: ") + fr[3] + " comparisons." : "Gold cards are being compared.";
  }
  var film = k.loop(14, draw, { label: "Steps" });
  function reset() { frames = run(); film.set(0); film.play(); }
  k.buttons([["Method A", function () { method = 0; reset(); }], ["Method B", function () { method = 1; reset(); }]], true);
  k.buttons([["Shuffled", function () { start = [5, 2, 8, 1, 7, 3, 6, 4]; reset(); }], ["Almost in order", function () { start = [1, 2, 4, 3, 5, 6, 8, 7]; reset(); }]], true);
  frames = run(); st.draw = function () { draw(film.t()); };
});
