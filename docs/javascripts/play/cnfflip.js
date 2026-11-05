/* books/ai/08: a formula in conjunctive normal form is true only when every clause has at least one true literal. Flip
   A, B and C and watch the clauses. The formula is a small made-up example. */
PLAY("cnfflip", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 230, st = k.stage(W, H), g = st.g, out = k.out(), v = { A: false, B: false, C: false };
  var CL = [[["A", 1], ["B", 1]], [["A", 0], ["C", 1]], [["B", 0], ["C", 0]], [["B", 1], ["C", 1]]];
  function sat(c, x) { return c.some(function (l) { return x[l[0]] === !!l[1]; }); }
  function draw() {
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H); g.textAlign = "left";
    ["A", "B", "C"].forEach(function (n, i) { g.fillStyle = v[n] ? C.green : C.red; g.font = F(20, 800); g.fillText(n + " = " + (v[n] ? "true" : "false"), 20 + i * 170, 34); });
    var all = true;
    CL.forEach(function (c, i) { var ok = sat(c, v); all = all && ok; var x = 20 + i * 142, y = 64; g.fillStyle = ok ? C.green : C.red; g.globalAlpha = 0.2; g.fillRect(x, y, 132, 60); g.globalAlpha = 1; g.strokeStyle = ok ? C.green : C.red; g.lineWidth = 2; g.strokeRect(x, y, 132, 60);
      g.fillStyle = C.ink; g.font = F(20, 700); g.textAlign = "center"; g.fillText(c.map(function (l) { return (l[1] ? "" : "¬") + l[0]; }).join(" ∨ "), x + 66, y + 38); g.textAlign = "left"; });
    var n = 0; for (var m = 0; m < 8; m++) { var x = { A: !!(m & 4), B: !!(m & 2), C: !!(m & 1) }; if (CL.every(function (c) { return sat(c, x); })) n++; }
    g.fillStyle = all ? C.green : C.ink2; g.font = F(20, 700); g.fillText(all ? "every clause true: the formula is satisfied" : "a red clause makes the whole formula false", 20, 166);
    g.fillStyle = C.ink3; g.font = F(16, 600); g.fillText(n + " of the 8 rows of the truth table satisfy it", 20, 200);
    out.textContent = "(A ∨ B) ∧ (¬A ∨ C) ∧ (¬B ∨ ¬C) ∧ (B ∨ C): " + (all ? "satisfied." : "not yet; flip a letter.");
  }
  k.buttons(["A", "B", "C"].map(function (n) { return ["Flip " + n, function () { v[n] = !v[n]; draw(); }]; }));
  st.draw = draw; draw();
});
