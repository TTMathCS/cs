/* first-steps/01: a strict partner follows the words exactly. The vague instructions leave the size and place of the
   triangle open, so the drawing goes wrong; the exact ones say every length and corner. */
PLAY("strict", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 300, st = k.stage(W, H), g = st.g, out = k.out(), exact = false;
  var V = ["Draw a square.", "Draw a triangle on top."], E = ["Draw a square, sides 4 cm.", "Put a dot above the middle of the top side, 3 cm up.", "Join the dot to both top corners."];
  function draw(t) {
    var L = exact ? E : V, n = Math.min(L.length, Math.floor(t * (L.length + 0.5)) + (t > 0 ? 1 : 0));
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H); g.textAlign = "left";
    L.forEach(function (s, i) { g.fillStyle = i < n ? C.ink : C.ink3; g.font = F(19, i < n ? 600 : 500); g.fillText((i + 1) + ". " + s, 20, 40 + i * 32); });
    var x = 470, y = 160, s = 90; g.strokeStyle = C.gold; g.lineWidth = 4; g.lineJoin = "round";
    if (n >= 1) g.strokeRect(x, y, s, s);
    if (exact) {
      if (n >= 2) { g.fillStyle = C.gold; g.beginPath(); g.arc(x + s / 2, y - 70, 6, 0, 7); g.fill(); }
      if (n >= 3) { g.beginPath(); g.moveTo(x, y); g.lineTo(x + s / 2, y - 70); g.lineTo(x + s, y); g.stroke(); }
    } else if (n >= 2) { g.beginPath(); g.moveTo(x + 70, y - 2); g.lineTo(x + 100, y - 40); g.lineTo(x + 130, y - 2); g.closePath(); g.stroke(); }
    out.textContent = n < L.length ? "The partner does exactly what each step says…" : exact ? "Every length and corner was written down, so the house comes out right." : "“A triangle on top”: how big? Where? The partner guessed, and the roof is wrong.";
  }
  var film = k.loop(6, draw, { label: "Steps" });
  k.buttons([["Vague steps", function () { exact = false; film.set(0); film.play(); }], ["Exact steps", function () { exact = true; film.set(0); film.play(); }]], true);
  st.draw = function () { draw(film.t()); };
});
