/* first-steps/03: guess my number. The computer picks a number from 1 to 100 and says higher or lower. Guess with the
   slider, or let it use the middle trick: never more than 7 guesses. */
PLAY("guessnum", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 200, st = k.stage(W, H), g = st.g, out = k.out(), secret, lo, hi, tries, last, sl, val = 50;
  function fresh() { secret = 1 + Math.floor(Math.random() * 100); lo = 1; hi = 100; tries = []; last = ""; }
  function guess(v) {
    if (last === "yes") return; v = Math.round(v); tries.push(v);
    if (v === secret) last = "yes"; else if (v < secret) { last = "higher"; lo = Math.max(lo, v + 1); } else { last = "lower"; hi = Math.min(hi, v - 1); }
    draw();
  }
  function draw() {
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    var sx = 540 / 100; g.fillStyle = "rgba(244,230,212,0.08)"; g.fillRect(30, 60, 540, 34); g.fillStyle = "rgba(246,196,83,0.35)"; g.fillRect(30 + (lo - 1) * sx, 60, (hi - lo + 1) * sx, 34);
    tries.forEach(function (v, i) { g.fillStyle = v === secret ? C.green : C.red; g.fillRect(30 + (v - 1) * sx, 56, 3, 42); });
    g.fillStyle = C.ink3; g.font = F(17, 600); g.textAlign = "left"; g.fillText("1", 30, 120); g.textAlign = "right"; g.fillText("100", 570, 120);
    g.textAlign = "left"; g.fillStyle = C.ink; g.font = F(22, 700);
    g.fillText(last === "yes" ? "Yes! " + secret + " in " + tries.length + " guess" + (tries.length > 1 ? "es" : "") : last ? tries[tries.length - 1] + "? " + last + "." : "I'm thinking of a number from 1 to 100.", 30, 36);
    g.fillStyle = C.gold; g.font = F(18, 600); g.fillText("still possible: " + lo + " to " + hi, 30, 160);
    out.textContent = "Guesses so far: " + (tries.length ? tries.join(", ") : "none") + ".";
  }
  sl = k.slider("Your guess", 1, 100, 1, val, function (v) { return v; }, function (v) { val = +v; });
  k.buttons([["Guess", function () { guess(val); }], ["Middle trick", function () { if (last !== "yes") guess(Math.floor((lo + hi) / 2)); }], ["New number", function () { fresh(); draw(); }]]);
  fresh(); st.draw = draw; draw();
});
