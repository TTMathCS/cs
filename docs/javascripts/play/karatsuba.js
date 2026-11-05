/* books/algorithms/11: Karatsuba multiplication. Schoolbook multiplication of two n-digit numbers does n² digit
   products; Karatsuba replaces four half-size products with three, for about n^1.585. (Counts here assume n is a power
   of 2 and recurse down to single digits.) */
PLAY("karatsuba", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 240, st = k.stage(W, H), g = st.g, out = k.out(), e = 6;
  function draw() {
    var n = Math.pow(2, e), school = n * n, kar = Math.pow(3, e); g.fillStyle = C.bg; g.fillRect(0, 0, W, H); g.textAlign = "left";
    [[school, "schoolbook: n²", C.red], [kar, "Karatsuba: 3^log₂n", C.green]].forEach(function (r, i) { var y = 28 + i * 100; g.fillStyle = C.ink3; g.font = F(18, 600); g.fillText(r[1], 20, y); g.fillStyle = r[2]; g.fillRect(20, y + 10, Math.max(3, 560 * r[0] / school), 28); g.fillStyle = C.ink; g.font = F(20, 700); g.fillText(r[0].toLocaleString("en") + " digit products", 20, y + 62); });
    out.textContent = n.toLocaleString("en") + "-digit numbers: Karatsuba does " + (100 * kar / school).toFixed(1) + "% of the schoolbook work.";
  }
  k.slider("Digits", 1, 14, 1, e, function (v) { return Math.pow(2, v).toLocaleString("en"); }, function (v) { e = +v; draw(); });
  st.draw = draw; draw();
});
