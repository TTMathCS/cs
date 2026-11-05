/* books/algorithms/01: Euclid's algorithm as cutting squares. From an a × b rectangle cut the biggest squares you can;
   the leftover strip is (a mod b) × b; repeat. The last square's side is gcd(a, b). Starts with this page's example,
   gcd(1071, 462) = 21. */
PLAY("euclidsq", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 280, st = k.stage(W, H), g = st.g, out = k.out(), A = 1071, B = 462, ta, tb;
  function steps() { var a = A, b = B, S = []; while (b) { S.push([a, b, Math.floor(a / b), a % b]); var t = a % b; a = b; b = t; } return S; }
  function draw(t) {
    var S = steps(), n = Math.max(1, Math.ceil(t * S.length)), sc = Math.min(540 / A, 200 / B), x = 30, y = 50, w = A, h = B, horiz = true, cols = [C.gold, C.ice, C.green, C.rust, C.mars, C.earth];
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H); g.strokeStyle = C.ink3; g.lineWidth = 1; g.strokeRect(30, 50, A * sc, B * sc);
    for (var i = 0; i < n; i++) {
      var s = S[i], side = s[1];
      for (var q = 0; q < s[2]; q++) { g.fillStyle = cols[i % cols.length]; g.globalAlpha = 0.75; if (horiz) g.fillRect(x + q * side * sc + 1, y + 1, side * sc - 2, side * sc - 2); else g.fillRect(x + 1, y + q * side * sc + 1, side * sc - 2, side * sc - 2); g.globalAlpha = 1; }
      if (horiz) x += s[2] * side * sc; else y += s[2] * side * sc; horiz = !horiz;
    }
    g.textAlign = "left"; g.fillStyle = C.ink; g.font = F(18, 700, "m"); var s2 = S[n - 1]; g.fillText(s2[0] + " = " + s2[2] + " × " + s2[1] + " + " + s2[3], 30, 32);
    out.textContent = n >= S.length ? "The last squares fit exactly: gcd(" + A + ", " + B + ") = " + S[S.length - 1][1] + ", in " + S.length + " steps." : "Step " + n + ": cut " + s2[2] + " square" + (s2[2] > 1 ? "s" : "") + " of side " + s2[1] + "; " + s2[3] + " left over.";
  }
  var film = k.loop(8, draw, { label: "Steps" });
  ta = k.text("a", A, function (v) { var m = parseInt(v, 10); if (m > 0 && m < 1e6) { A = Math.max(m, B); draw(film.t()); } });
  tb = k.text("b", B, function (v) { var m = parseInt(v, 10); if (m > 0 && m <= A) { B = m; draw(film.t()); } });
  st.draw = function () { draw(film.t()); };
});
