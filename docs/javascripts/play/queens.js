/* books/algorithms/14: backtracking on six queens. Place a queen row by row in the first safe square; when a row has no
   safe square, take the last queen back and try her next square. Press Play. */
PLAY("queens", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 300, st = k.stage(W, H), g = st.g, out = k.out(), N = 6, frames = [], tried = 0;
  (function go(Q) {
    if (Q.length === N) { frames.push({ q: Q.slice(), msg: "Solved after trying " + tried + " placements." }); return true; }
    for (var c = 0; c < N; c++) { tried++; var ok = Q.every(function (qc, r) { return qc !== c && Math.abs(qc - c) !== Q.length - r; });
      if (ok) { Q.push(c); frames.push({ q: Q.slice(), msg: "Row " + Q.length + ": safe at column " + (c + 1) + "." }); if (go(Q)) return true; Q.pop(); frames.push({ q: Q.slice(), back: true, msg: "Dead end below: take the queen in row " + (Q.length + 1) + " back." }); } }
    return false; })([]);
  function draw(t) {
    var f = frames[Math.min(frames.length - 1, Math.floor(t * frames.length))], s = 44, x0 = 20, y0 = 20;
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    for (var r = 0; r < N; r++) for (var c = 0; c < N; c++) { g.fillStyle = (r + c) % 2 ? C.line : C.ink3; g.globalAlpha = (r + c) % 2 ? 1 : 0.35; g.fillRect(x0 + c * s, y0 + r * s, s, s); }
    g.globalAlpha = 1; g.textAlign = "center"; g.font = F(30, 800);
    f.q.forEach(function (c, r) { g.fillStyle = f.back ? C.rust : r === f.q.length - 1 ? C.gold : C.ice; g.fillText("♛", x0 + c * s + s / 2, y0 + r * s + s / 2 + 11); });
    g.textAlign = "left"; g.fillStyle = C.ink; g.font = F(20, 700); g.fillText("step " + (frames.indexOf(f) + 1) + " of " + frames.length, 310, 50);
    g.fillStyle = C.ink2; g.font = F(17, 600); g.fillText("queens placed: " + f.q.length, 310, 84);
    out.textContent = f.msg;
  }
  var film = k.loop(14, draw, { label: "Steps" }); st.draw = function () { draw(film.t()); };
});
