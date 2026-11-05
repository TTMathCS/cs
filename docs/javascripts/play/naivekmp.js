/* books/algorithms/18: naive string matching against KMP on the worst case, text aaa…a and pattern aa…ab. The naive
   method restarts after every mismatch and makes about n·m comparisons; KMP's prefix function lets it never move
   backward in the text, about 2n. */
PLAY("naivekmp", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 220, st = k.stage(W, H), g = st.g, out = k.out(), n = 1000, m = 20;
  function counts() {
    var T = new Array(n + 1).join("a"), P = new Array(m).join("a") + "b", c1 = 0, c2 = 0, i, j;
    for (i = 0; i + m <= n; i++) { for (j = 0; j < m; j++) { c1++; if (T[i + j] !== P[j]) break; } }
    var pi = [0]; for (i = 1, j = 0; i < m; i++) { while (j && P[i] !== P[j]) j = pi[j - 1]; if (P[i] === P[j]) j++; pi.push(j); }
    for (i = 0, j = 0; i < n; i++) { while (true) { c2++; if (T[i] === P[j]) { j++; break; } if (!j) break; j = pi[j - 1]; } if (j === m) j = pi[j - 1]; }
    return [c1, c2];
  }
  function draw() {
    var c = counts(), mx = Math.max(c[0], c[1]); g.fillStyle = C.bg; g.fillRect(0, 0, W, H); g.textAlign = "left";
    [[c[0], "naive", C.red], [c[1], "KMP", C.green]].forEach(function (r, i) { var y = 30 + i * 84; g.fillStyle = C.ink3; g.font = F(18, 600); g.fillText(r[1], 20, y); g.fillStyle = r[2]; g.fillRect(20, y + 10, Math.max(3, 560 * r[0] / mx), 28); g.fillStyle = C.ink; g.font = F(20, 700); g.fillText(r[0].toLocaleString("en") + " comparisons", 20, y + 62); });
    out.textContent = "Text of " + n.toLocaleString("en") + " a's, pattern of " + m + ": naive " + c[0].toLocaleString("en") + ", KMP " + c[1].toLocaleString("en") + " (" + (c[0] / c[1]).toFixed(1) + "× fewer).";
  }
  k.slider("Pattern length m", 2, 100, 1, m, function (v) { return v; }, function (v) { m = +v; draw(); });
  st.draw = draw; draw();
});
