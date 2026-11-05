/* books/ai/19: a small repeated prisoner's dilemma tournament with this page's payoffs (both cooperate 3 each, both defect
   1 each, a lone defector 5 and the cooperator 0). Every strategy meets every other for 50 rounds. Pick who enters. */
PLAY("ipd", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 260, st = k.stage(W, H), g = st.g, out = k.out();
  var S = [["Tit for tat", function (me, them) { return them.length ? them[them.length - 1] : "C"; }, true], ["Always defect", function () { return "D"; }, true], ["Always cooperate", function () { return "C"; }, true], ["Grudger", function (me, them) { return them.indexOf("D") >= 0 ? "D" : "C"; }, true], ["Random", function () { return Math.random() < 0.5 ? "C" : "D"; }, false]];
  var PAY = { CC: [3, 3], CD: [0, 5], DC: [5, 0], DD: [1, 1] };
  function play(a, b) { var ha = [], hb = [], sa = 0, sb = 0; for (var r = 0; r < 50; r++) { var x = a(ha, hb), y = b(hb, ha); ha.push(x); hb.push(y); sa += PAY[x + y][0]; sb += PAY[x + y][1]; } return [sa, sb]; }
  function draw() {
    var on = S.filter(function (s) { return s[2]; }), sc = on.map(function () { return 0; });
    for (var i = 0; i < on.length; i++) for (var j = i + 1; j < on.length; j++) { var r = play(on[i][1], on[j][1]); sc[i] += r[0]; sc[j] += r[1]; }
    var order = sc.map(function (v, i) { return i; }).sort(function (a, b) { return sc[b] - sc[a]; }), mx = Math.max.apply(null, sc.concat([1]));
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    order.forEach(function (i, r) { var y = 20 + r * 44; g.fillStyle = r === 0 ? C.gold : C.ice; g.fillRect(200, y, 330 * sc[i] / mx, 30); g.fillStyle = C.ink; g.font = F(18, 700); g.textAlign = "right"; g.fillText(on[i][0], 190, y + 22); g.textAlign = "left"; g.fillText(sc[i], 206 + 330 * sc[i] / mx, y + 22); });
    out.textContent = on.length < 2 ? "Pick at least two players." : "Winner: " + on[order[0]][0] + " with " + sc[order[0]] + " points over its games.";
  }
  k.buttons(S.map(function (s) { return [s[0], function () { s[2] = !s[2]; draw(); }]; }));
  out.textContent = ""; st.draw = draw; draw();
  var row = fig.querySelectorAll(".btns button"); S.forEach(function (s, i) { if (row[i]) { row[i].setAttribute("aria-pressed", s[2]); row[i].addEventListener("click", function () { row[i].setAttribute("aria-pressed", s[2]); }); } });
});
