/* searching/binary-search.md: binary search against a plain scan, in a sorted list of 1,000 numbers. Pick the number
   to find and press Play: the scan checks one item after another; binary search checks the middle and throws away
   half each time, so it never needs more than 10 looks (2¹⁰ = 1,024). */
PLAY("halving", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 300, st = k.stage(W, H), g = st.g, out = k.out(), N = 1000, target = 737, trail = [];
  function search() { var lo = 1, hi = N, r = []; while (lo <= hi) { var m = (lo + hi) >> 1; r.push([lo, hi, m]); if (m === target) break; if (m < target) lo = m + 1; else hi = m - 1; } return r; }
  function x(v) { return 20 + (v - 1) / (N - 1) * (W - 40); }
  function draw(t) {
    trail = search(); var steps = trail.length, sec = t * 10, bs = Math.min(steps, Math.floor(sec * 1.2)), scan = Math.min(target, Math.floor(sec * 1.2));
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    g.font = F(18, 600); g.fillStyle = C.ink; g.fillText("Binary search: " + bs + " look" + (bs === 1 ? "" : "s") + (bs >= steps ? ", found" : ""), 20, 34);
    for (var i = 0; i < bs; i++) { var r = trail[i], y = 52 + i * 14; g.fillStyle = "rgba(156,201,234,0.35)"; g.fillRect(x(r[0]), y, Math.max(2, x(r[1]) - x(r[0])), 10); g.fillStyle = C.gold; g.fillRect(x(r[2]) - 1, y - 2, 3, 14); }
    g.fillStyle = C.ink; g.fillText("Plain scan: " + scan + " look" + (scan === 1 ? "" : "s") + (scan >= target ? ", found" : ""), 20, 230);
    g.fillStyle = "rgba(244,230,212,0.08)"; g.fillRect(20, 244, W - 40, 16); g.fillStyle = C.rust; g.fillRect(20, 244, x(scan) - 20, 16);
    g.strokeStyle = C.gold; g.lineWidth = 2; g.beginPath(); g.moveTo(x(target), 46); g.lineTo(x(target), 268); g.stroke();
    g.font = F(14, 500); g.fillStyle = C.ink3; g.fillText("1", 20, 286); g.textAlign = "right"; g.fillText("1,000", W - 20, 286); g.textAlign = "left";
    out.textContent = "Looking for " + target + ": binary search needs " + steps + " looks; a plain scan from the start needs " + target + ".";
  }
  st.draw = function () { draw(film.t()); };
  var film = k.loop(10, draw, { start0: true, label: "Time" });
  k.slider("Find", 1, 1000, 1, target, function (v) { return v; }, function (v) { target = v; film.set(0); });
});
