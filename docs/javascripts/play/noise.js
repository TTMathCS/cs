/* topics/Materials-from-formulas: the patterns behind the Crown's materials. Left, the pattern as a picture; right,
   the same numbers along the dashed line as a graph. Value noise, gradient (Perlin) noise, fBm (add octaves, each
   twice as fine and `roughness` times as strong), Voronoi cells (distance to the nearest random point), and the
   basalt recipe that mixes them. Every pixel is computed from its x and y; nothing is a stored picture. */
PLAY("noise", function (fig, k) {
  var C = k.C, F = k.F, W = 640, H = 320, N = 160, mode = "fbm", oct = 4, rough = 0.5, st, out;
  st = k.stage(W, H); var g = st.g;
  var off = document.createElement("canvas"); off.width = N; off.height = N; var og = off.getContext("2d"), img = og.createImageData(N, N);

  function hash(x, y, s) {   // two whole numbers in, one 32-bit number out: the same corner always gives the same number
    var h = Math.imul(x | 0, 73856093) ^ Math.imul(y | 0, 19349663) ^ (s | 0);
    h ^= h >>> 13; h = Math.imul(h, 0x5bd1e995); h ^= h >>> 15; return h >>> 0;
  }
  function fade(t) { return t * t * t * (t * (t * 6 - 15) + 10); }
  function value(x, y) {      // a random height at each corner, blended: about 0..1
    var ix = Math.floor(x), iy = Math.floor(y), u = fade(x - ix), v = fade(y - iy);
    var a = hash(ix, iy, 7) / 4294967296, b = hash(ix + 1, iy, 7) / 4294967296, c = hash(ix, iy + 1, 7) / 4294967296, d = hash(ix + 1, iy + 1, 7) / 4294967296;
    return (a + u * (b - a)) + v * ((c + u * (d - c)) - (a + u * (b - a)));
  }
  function grad(x, y) {       // a random slope at each corner, blended: about -1..1
    var ix = Math.floor(x), iy = Math.floor(y), fx = x - ix, fy = y - iy;
    function cn(dx, dy) { var a = hash(ix + dx, iy + dy, 3) / 4294967296 * 6.283185307; return Math.cos(a) * (fx - dx) + Math.sin(a) * (fy - dy); }
    var u = fade(fx), v = fade(fy), p = cn(0, 0), q = cn(1, 0), r = cn(0, 1), s = cn(1, 1);
    return ((p + u * (q - p)) + v * ((r + u * (s - r)) - (p + u * (q - p)))) * 1.41421356;
  }
  function fbm(x, y, n, ro) { var t = 0, a = 1, m = 0, f = 1; for (var i = 0; i < n; i++) { t += a * grad(x * f + i * 17.3, y * f); m += a; a *= ro; f *= 2; } return 0.5 * t / m + 0.5; }
  function cells(x, y) {      // Worley F1: distance to the nearest of one random point per square
    var ix = Math.floor(x), iy = Math.floor(y), best = 9;
    for (var dx = -1; dx <= 1; dx++) for (var dy = -1; dy <= 1; dy++) {
      var h = hash(ix + dx, iy + dy, 11), px = ix + dx + (h & 65535) / 65536, py = iy + dy + (h >>> 16) / 65536;
      var d = Math.hypot(x - px, y - py); if (d < best) best = d;
    }
    return best;
  }
  // one number 0..1 for the picture (and the graph), at x, y in units of the picture's width (0..1)
  function f(x, y) {
    if (mode === "value") return value(x * 6, y * 6);
    if (mode === "grad") return 0.5 + 0.5 * grad(x * 6, y * 6);
    if (mode === "fbm") return fbm(x * 4, y * 4, oct, rough);
    if (mode === "cells") return Math.min(1, cells(x * 8, y * 8));
    // basalt, a 10 cm square: grains every 1/260 m, clouds 0.7 per metre
    var X = x * 0.1, Y = y * 0.1, t = Math.max(0, Math.min(1, 0.6 * cells(X * 260, Y * 260) + 0.5 * fbm(X * 0.7 + 3, Y * 0.7, 6, 0.5)));
    return t;
  }
  function srgb(c) { c = Math.max(0, Math.min(1, c)); return c <= 0.0031308 ? 12.92 * c : 1.055 * Math.pow(c, 1 / 2.4) - 0.055; }
  function draw() {
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    var line = [], i, j, v, p = 0;
    for (j = 0; j < N; j++) for (i = 0; i < N; i++) {
      v = f(i / N, j / N);
      if (j === N >> 1) line.push(v);
      var r, gg, b;
      if (mode === "basalt") { var lin = 0.018 + v * 0.042; r = gg = b = srgb(lin * 6); }   // shown 6x brighter, as in the Python
      else { r = 0.12 + 0.85 * v; gg = 0.08 + 0.72 * v; b = 0.06 + 0.58 * v; }
      img.data[p++] = r * 255; img.data[p++] = gg * 255; img.data[p++] = b * 255; img.data[p++] = 255;
    }
    og.putImageData(img, 0, 0);
    g.imageSmoothingEnabled = false; g.drawImage(off, 20, 20, 280, 280);
    g.strokeStyle = C.ice; g.setLineDash([6, 5]); g.lineWidth = 1.5; g.beginPath(); g.moveTo(20, 160); g.lineTo(300, 160); g.stroke(); g.setLineDash([]);
    // the graph of the dashed line
    var gx = 340, gw = 280, gy = 40, gh = 240;
    g.strokeStyle = C.line; g.lineWidth = 1; g.strokeRect(gx, gy, gw, gh);
    g.fillStyle = C.ink3; g.font = F(13, 500); g.textAlign = "left"; g.fillText("1", gx - 14, gy + 5); g.fillText("0", gx - 14, gy + gh + 4);
    g.fillText("along the dashed line", gx, gy + gh + 22);
    g.strokeStyle = C.gold; g.lineWidth = 2; g.beginPath();
    for (i = 0; i < line.length; i++) { var X = gx + i / (line.length - 1) * gw, Y = gy + gh - line[i] * gh; i ? g.lineTo(X, Y) : g.moveTo(X, Y); }
    g.stroke();
    g.fillStyle = C.ink; g.font = F(16, 600);
    g.fillText({ value: "Value noise", grad: "Gradient (Perlin) noise", fbm: "fBm, " + oct + " octave" + (oct > 1 ? "s" : ""), cells: "Voronoi cells (F1)", basalt: "Basalt, a 10 cm square" }[mode], gx, gy - 14);
    out.textContent = {
      value: "A random height at each whole-number corner, blended with the fade curve 6t⁵ − 15t⁴ + 10t³. Smooth, but you can see the grid.",
      grad: "A random slope at each corner instead of a height: every corner sits at the middle value, so the grid hides better.",
      fbm: "Octave number i is 2ⁱ times finer and " + rough + "ⁱ times as strong. More octaves add finer detail; roughness says how strong the fine detail is.",
      cells: "The distance to the nearest random point: 0 at each point (dark), largest on the borders between cells. Used for stone grains and leather.",
      basalt: "0.6 × cells at 260 per metre (grains about 4 mm) + 0.5 × fBm at 0.7 per metre (slow clouds, which hardly change over 10 cm), into a ramp from almost black to dark grey. Shown 6 times brighter."
    }[mode];
  }
  k.buttons([["Value", function () { mode = "value"; draw(); }], ["Gradient", function () { mode = "grad"; draw(); }], ["fBm", function () { mode = "fbm"; draw(); }],
    ["Cells", function () { mode = "cells"; draw(); }], ["Basalt", function () { mode = "basalt"; draw(); }]], true);
  k.fig.querySelectorAll(".btns button").forEach(function (b) { b.setAttribute("aria-pressed", b.textContent === "fBm"); });
  k.slider("Octaves", 1, 8, 1, 4, function (v) { return v; }, function (v) { oct = v; if (mode === "fbm") draw(); });
  k.slider("Roughness", 0.2, 0.8, 0.05, 0.5, function (v) { return v.toFixed(2); }, function (v) { rough = +v.toFixed(2); if (mode === "fbm") draw(); });
  out = k.out(); st.draw = draw; draw();
});
