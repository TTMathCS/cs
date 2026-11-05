/* first-steps/05: the robot from this page. "repeat until there is something in front: step", then "pick up", works
   however far away the object is. The wrong loop, "repeat until there is something in front: turn left", never changes
   what is in front, so it spins forever. */
PLAY("robot", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 230, st = k.stage(W, H), g = st.g, out = k.out(), far = 5, bad = false;
  function draw(t) {
    var n = Math.floor(t * 30), pos = 0, dir = 0, got = false, line = 0;
    for (var s = 0; s < n; s++) { if (bad) { dir = (dir + 1) % 4; line = 1; } else if (pos + 1 < far) { pos++; line = 1; } else { got = true; line = 2; break; } }
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    var x0 = 60, sx = 480 / 9;
    for (var i = 0; i < 10; i++) { g.strokeStyle = C.line; g.strokeRect(x0 + i * sx - sx / 2, 130, sx, 50); }
    if (!got) { g.fillStyle = C.gold; g.beginPath(); g.arc(x0 + far * sx, 155, 14, 0, 7); g.fill(); }
    var rx = x0 + pos * sx; g.save(); g.translate(rx, 155); g.rotate(-dir * Math.PI / 2); g.fillStyle = C.ice; g.fillRect(-16, -16, 32, 32); g.fillStyle = C.bg; g.beginPath(); g.moveTo(16, 0); g.lineTo(6, -8); g.lineTo(6, 8); g.fill(); g.restore();
    if (got) { g.fillStyle = C.gold; g.beginPath(); g.arc(rx, 130, 10, 0, 7); g.fill(); }
    var P = bad ? ["repeat until something in front:", "    turn left", "pick up"] : ["repeat until something in front:", "    step", "pick up"];
    P.forEach(function (p, i) { g.textAlign = "left"; g.fillStyle = i === line && n ? C.gold : C.ink2; g.font = F(18, i === line ? 700 : 500, "m"); g.fillText(p, 20, 30 + i * 26); });
    g.textAlign = "right"; g.fillStyle = C.ink; g.font = F(18, 600); g.fillText(bad ? "turns: " + n : "steps: " + pos, 580, 30);
    out.textContent = bad ? (n > 8 ? "Turning left never puts anything in front: an infinite loop." : "The robot turns…") : got ? "Something in front: the loop stops, and the robot picks it up." : "Nothing in front yet, so: step.";
  }
  var film = k.loop(8, draw, { label: "Time" });
  k.slider("How far away", 2, 9, 1, far, function (v) { return v + " steps"; }, function (v) { far = +v; draw(film.t()); });
  k.buttons([["Good loop", function () { bad = false; film.set(0); film.play(); }], ["Wrong loop", function () { bad = true; film.set(0); film.play(); }]], true);
  st.draw = function () { draw(film.t()); };
});
