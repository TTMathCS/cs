/* books/algorithms/04: a dynamic array that doubles when full. Most appends cost 1; the append that finds it full also
   copies every element. The spikes grow, but they come rarer, so the average stays under 3 per append. */
PLAY("dynarray", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 260, st = k.stage(W, H), g = st.g, out = k.out(), grow = 2;
  function draw(t) {
    var n = Math.max(1, Math.ceil(t * 64)), cap = 1, size = 0, tot = 0, costs = [];
    for (var i = 0; i < n; i++) { var c = 1; if (size === cap) { c += size; cap = Math.max(cap + 1, Math.ceil(cap * grow)); } size++; tot += c; costs.push(c); }
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H); var mx = 0; costs.forEach(function (c) { mx = Math.max(mx, c); }); var sy = 150 / Math.max(mx, 33);
    costs.forEach(function (c, i) { g.fillStyle = c > 1 ? C.red : C.ice; g.fillRect(30 + i * 8.5, 210 - c * sy, 7, c * sy); });
    var avg = tot / n; g.strokeStyle = C.gold; g.setLineDash([6, 6]); g.beginPath(); g.moveTo(30, 210 - avg * sy); g.lineTo(580, 210 - avg * sy); g.stroke(); g.setLineDash([]);
    g.textAlign = "left"; g.fillStyle = C.ink; g.font = F(19, 700); g.fillText(n + " appends, capacity " + cap + ", total cost " + tot, 20, 30); g.fillStyle = C.gold; g.fillText("average " + avg.toFixed(2) + " per append", 20, 240);
    out.textContent = "Grow by ×" + grow + ": red bars are the appends that had to copy everything; the average stays at " + avg.toFixed(2) + ".";
  }
  var film = k.loop(8, draw, { label: "Appends" });
  k.buttons([["Double", function () { grow = 2; draw(film.t()); }], ["×1.5", function () { grow = 1.5; draw(film.t()); }], ["Add 4 each time", function () { grow = 0; draw(film.t()); }]], true);
  st.draw = function () { draw(film.t()); };
  var orig = draw; draw = function (t) { if (grow === 0) { var n = Math.max(1, Math.ceil(t * 64)), cap = 4, size = 0, tot = 0, costs = []; for (var i = 0; i < n; i++) { var c = 1; if (size === cap) { c += size; cap += 4; } size++; tot += c; costs.push(c); } g.fillStyle = C.bg; g.fillRect(0, 0, W, H); var sy = 150 / 64; costs.forEach(function (c, i) { g.fillStyle = c > 1 ? C.red : C.ice; g.fillRect(30 + i * 8.5, 210 - c * sy, 7, c * sy); }); var avg = tot / n; g.strokeStyle = C.gold; g.setLineDash([6, 6]); g.beginPath(); g.moveTo(30, 210 - avg * sy); g.lineTo(580, 210 - avg * sy); g.stroke(); g.setLineDash([]); g.textAlign = "left"; g.fillStyle = C.ink; g.font = F(19, 700); g.fillText(n + " appends, capacity " + cap + ", total cost " + tot, 20, 30); g.fillStyle = C.gold; g.fillText("average " + avg.toFixed(2) + " per append", 20, 240); out.textContent = "Grow by a fixed 4: copies come every 4 appends and keep getting bigger, so the average keeps climbing (about n/8)."; } else orig(t); };
});
