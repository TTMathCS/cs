/* books/algorithms/24: ski rental, from this page. Renting costs 1 a day and buying costs B; you do not know how many
   days the snow will last. The break-even rule (rent for B − 1 days, then buy) never pays more than twice what someone
   who knew the future would pay. Slide the season length and compare. */
PLAY("skirental", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 250, st = k.stage(W, H), g = st.g, out = k.out(), B = 10, d = 7;
  function draw() {
    var opt = Math.min(d, B), be = d < B ? d : (B - 1) + B, rent = d, buy = B, mx = Math.max(opt, be, rent, buy);
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    [["always rent", rent, C.ice], ["buy on day 1", buy, C.ice], ["break-even rule", be, C.gold], ["knowing the future", opt, C.green]].forEach(function (r, i) {
      var y = 20 + i * 46; g.fillStyle = C.ink2; g.font = F(18, 600); g.textAlign = "right"; g.fillText(r[0], 200, y + 22); g.fillStyle = r[2]; g.fillRect(212, y, 340 * r[1] / mx, 32); g.fillStyle = C.ink; g.textAlign = "left"; g.font = F(18, 700); g.fillText(r[1], 218 + 340 * r[1] / mx, y + 22);
    });
    out.textContent = "Season of " + d + " days, skis cost " + B + ": the break-even rule pays " + be + ", " + (be / opt).toFixed(2) + "× the best possible " + opt + ".";
  }
  k.slider("Days of snow", 1, 40, 1, d, function (v) { return v; }, function (v) { d = +v; draw(); });
  k.slider("Price to buy (B)", 2, 20, 1, B, function (v) { return v; }, function (v) { B = +v; draw(); });
  st.draw = draw; draw();
});
