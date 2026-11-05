/* books/ai/07: min-conflicts on 8 queens. Start with one queen in each column at random; repeatedly pick a queen that is
   attacked and move it, within its column, to the row with the fewest attacks. It usually solves the board in a few
   dozen moves. */
PLAY("minconf", function (fig, k) {
  var C = k.C, F = k.F, N = 8, cs = 32, W = 600, H = 280, st = k.stage(W, H), g = st.g, out = k.out(), hist, seedv = 3;
  function conflicts(Q, c, r) { var n = 0; for (var j = 0; j < N; j++) if (j !== c && (Q[j] === r || Math.abs(Q[j] - r) === Math.abs(j - c))) n++; return n; }
  function run() {
    var s = seedv; function rn() { s = (s * 16807) % 2147483647; return s / 2147483647; }
    var Q = []; for (var i = 0; i < N; i++) Q.push(Math.floor(rn() * N)); var H2 = [Q.slice()];
    for (var step = 0; step < 1000; step++) {
      var bad = []; for (i = 0; i < N; i++) if (conflicts(Q, i, Q[i])) bad.push(i); if (!bad.length) break;
      var c = bad[Math.floor(rn() * bad.length)], best = [], bv = 99; for (var r = 0; r < N; r++) { var v = conflicts(Q, c, r); if (v < bv) { bv = v; best = [r]; } else if (v === bv) best.push(r); }
      Q[c] = rn() < 0.1 ? Math.floor(rn() * N) : best[Math.floor(rn() * best.length)]; H2.push(Q.slice());
    }
    return H2;
  }
  function draw(t) {
    var i = Math.min(hist.length - 1, Math.floor(t * hist.length)), Q = hist[i], tot = 0; g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    for (var c = 0; c < N; c++) for (var r = 0; r < N; r++) { g.fillStyle = (c + r) % 2 ? "#3a281e" : "#5a4434"; g.fillRect(20 + c * cs, 12 + r * cs, cs, cs); }
    for (c = 0; c < N; c++) { var n = conflicts(Q, c, Q[c]); tot += n; g.fillStyle = n ? C.red : C.gold; g.font = F(24, 700); g.textAlign = "center"; g.fillText("♛", 20 + c * cs + cs / 2, 12 + Q[c] * cs + 25); }
    g.textAlign = "left"; g.fillStyle = C.ink; g.font = F(21, 700); g.fillText("move " + i, 320, 60); g.fillStyle = tot ? C.red : C.green; g.fillText(tot ? "attacks: " + tot / 2 : "solved", 320, 96);
    out.textContent = tot ? "Red queens are attacked; each move puts one where it is attacked least (now and then a random row, to escape a stuck spot)." : "No queen attacks another: solved in " + i + " moves.";
  }
  hist = run(); var film = k.loop(10, draw, { label: "Moves" });
  k.buttons([["New start", function () { seedv = (seedv * 31 + 7) % 99991 + 1; hist = run(); film.set(0); film.play(); }]]);
  st.draw = function () { draw(film.t()); };
});
