/* books/algorithms/19: the Fermat test. If n is prime, a^(n−1) ≡ 1 (mod n) for every base a from 2 to n − 1. Type a
   number: each square is one base, gold if it says "maybe prime", red if it proves n composite. Try 561, a Carmichael
   number that fools every base coprime to it. */
PLAY("fermat", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 250, st = k.stage(W, H), g = st.g, out = k.out(), n = 91;
  function pw(a, e, m) { var r = 1n, b = BigInt(a) % BigInt(m), E = BigInt(e), M = BigInt(m); while (E > 0n) { if (E & 1n) r = r * b % M; b = b * b % M; E >>= 1n; } return r; }
  function gcd(a, b) { while (b) { var t = a % b; a = b; b = t; } return a; }
  function draw() {
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H); var B = Math.min(n - 2, 400), cols = 40, s = 13.5, liars = 0, wit = 0;
    for (var a = 2; a < 2 + B; a++) { var i = a - 2, ok = pw(a, n - 1, n) === 1n; if (ok) liars++; else wit++; g.fillStyle = ok ? C.gold : C.red; g.fillRect(20 + (i % cols) * s, 20 + Math.floor(i / cols) * s, s - 2, s - 2); }
    var prime = n > 1; for (var d = 2; d * d <= n; d++) if (n % d === 0) { prime = false; break; }
    var car = !prime && liars > 0; for (var a2 = 2; car && a2 < 2 + B; a2++) if (gcd(a2, n) === 1 && pw(a2, n - 1, n) !== 1n) car = false;
    out.textContent = n + (prime ? " is prime: every base says maybe prime." : " is composite (" + (function () { for (var d = 2; d * d <= n; d++) if (n % d === 0) return d + " × " + n / d; })() + "): " + wit + " of the " + B + " bases shown prove it" + (liars ? ", and " + liars + " are Fermat liars." : ".") + (car ? " Every red base shares a factor with " + n + ": a Carmichael number fools all the others." : "")) + (B < n - 2 ? " (First 400 bases shown.)" : "");
  }
  var box = k.text("Number n", n, function (v) { var m = parseInt(v, 10); if (m >= 5 && m < 1e7) { n = m; draw(); } });
  function pick(m) { return function () { n = m; if (box) box.value = m; draw(); }; }
  k.buttons([["91", pick(91)], ["97", pick(97)], ["561", pick(561)], ["341", pick(341)]]);
  st.draw = draw; draw();
});
