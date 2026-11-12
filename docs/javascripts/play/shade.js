/* topics/Materials-from-formulas: how a surface answers light. A ball lit by one sun, every pixel computed with the
   formulas on the page: Lambert diffuse, the GGX microfacet highlight with Smith's shadowing and Schlick's Fresnel,
   a clear coat as a second GGX layer, and the "Charlie" sheen for cloth (the functions three.js uses). The six
   buttons load the numbers of the Crown's materials from the Art repo. Right: how the light that arrives at 45° leaves
   a flat piece of the same material, in every direction of that plane. */
PLAY("shade", function (fig, k) {
  var C = k.C, F = k.F, W = 640, H = 320, N = 150, st, out, rs, ls;
  var M = {   // from crown_rooms.py, seating.py and furn.py (linear colours); glass from lib.glass
    Basalt:  { base: [0.040, 0.039, 0.038], r: 0.20, metal: 0, coat: 0.4, coatR: 0.10 },
    Plaster: { base: [0.85, 0.80, 0.72], r: 0.90, metal: 0 },
    Bronze:  { base: [0.40, 0.29, 0.19], r: 0.35, metal: 1 },
    Glass:   { base: [0.93, 0.95, 0.93], r: 0.0, metal: 0, glass: true },
    Leather: { base: [0.30, 0.14, 0.06], r: 0.43, metal: 0, coat: 0.25, coatR: 0.35 },
    Rug:     { base: [0.24, 0.20, 0.17], r: 1.0, metal: 0, sheen: 1.0, sheenR: 0.5 }
  };
  var name = "Bronze", m = M[name], rough = m.r, sunDeg = 40;
  st = k.stage(W, H); var g = st.g;
  var off = document.createElement("canvas"); off.width = N; off.height = N; var og = off.getContext("2d"), img = og.createImageData(N, N);

  function dot(a, b) { return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]; }
  function norm(a) { var l = Math.hypot(a[0], a[1], a[2]) || 1; return [a[0] / l, a[1] / l, a[2] / l]; }
  function schlick(f0, c) { var p = Math.pow(1 - c, 5); return f0 + (1 - f0) * p; }
  function ggx(a, nh) { var a2 = a * a, d = nh * nh * (a2 - 1) + 1; return a2 / (Math.PI * d * d); }
  function smith(a, nl, nv) { var a2 = a * a, gv = nl * Math.sqrt(nv * nv * (1 - a2) + a2), gl = nv * Math.sqrt(nl * nl * (1 - a2) + a2); return 0.5 / Math.max(gv + gl, 1e-6); }
  function charlie(r, nh) { var a = Math.max(r * r, 1e-3), s2 = Math.max(1 - nh * nh, 0.0078125); return (2 + 1 / a) * Math.pow(s2, 0.5 / a) / (2 * Math.PI); }
  function sky(d) { var t = Math.max(0, d[1]); return [0.55 + 0.25 * t, 0.42 + 0.18 * t, 0.32 + 0.12 * t].map(function (x) { return x * 0.35; }); }   // a dusty Mars sky, brighter overhead
  function back(x, y) { var s = (Math.floor(x * 8) + Math.floor(y * 8)) & 1; return s ? [0.30, 0.16, 0.09] : [0.08, 0.05, 0.04]; }

  // the light leaving a surface point with normal n towards the eye v, from a sun in direction l (all unit vectors)
  function shade(n, v, l, r, out3, sunOnly) {
    var a = Math.max(r * r, 0.002), nl = Math.max(dot(n, l), 0), nv = Math.max(dot(n, v), 1e-4), h = norm([l[0] + v[0], l[1] + v[1], l[2] + v[2]]);
    var nh = Math.max(dot(n, h), 0), vh = Math.max(dot(v, h), 0), E = 3.2, res = [0, 0, 0];
    var refl = [2 * nv * n[0] - v[0], 2 * nv * n[1] - v[1], 2 * nv * n[2] - v[2]], env = sky(refl), envDiff = sky([0, 1, 0]);
    var blur = Math.min(1, r * 1.4);                                       // a rough surface sees a blurred sky: here simply its average
    for (var c = 0; c < 3; c++) {
      var f0 = m.metal ? m.base[c] : 0.04, Fs = schlick(f0, vh), Fe = schlick(f0, nv);
      var spec = ggx(a, nh) * smith(a, nl, nv) * Fs;
      var diff = m.metal || m.glass ? 0 : m.base[c] / Math.PI;
      var L = (diff + spec) * E * nl;
      if (!sunOnly) L += (m.metal ? 0 : m.glass ? 0 : m.base[c] * envDiff[c] * 0.9) + Fe * (env[c] * (1 - blur) + envDiff[c] * blur);
      if (m.sheen) L += m.sheen * charlie(m.sheenR, nh) / (4 * (nl + nv - nl * nv) + 1e-4) * E * nl * 0.5;
      if (m.coat) { var Fc = schlick(0.04, vh), ac = m.coatR * m.coatR; L = L * (1 - m.coat * schlick(0.04, nv)) + m.coat * (ggx(ac, nh) * smith(ac, nl, nv) * Fc * E * nl + (sunOnly ? 0 : schlick(0.04, nv) * env[c])); }
      res[c] = L;
    }
    if (m.glass) {   // seen straight through (not bent), dimmed by what the surface reflects
      var Fg = schlick(0.0426, nv); for (c = 0; c < 3; c++) res[c] += (1 - Fg) * out3[c] * m.base[c];
    }
    return res;
  }
  function tone(x) { x = x / (1 + x); return x <= 0.0031308 ? 12.92 * x : 1.055 * Math.pow(x, 1 / 2.4) - 0.055; }

  function draw() {
    var sr = sunDeg * Math.PI / 180, l = norm([Math.cos(sr) * 0.9, Math.sin(sr) * 0.9 + 0.1, 0.55]), v = [0, 0, 1], p = 0, i, j;
    for (j = 0; j < N; j++) for (i = 0; i < N; i++) {
      var x = (i + 0.5) / N * 2 - 1, y = 1 - (j + 0.5) / N * 2, rr = x * x + y * y, bg = back(i / N, j / N), col;
      var cov = Math.max(0, Math.min(1, (1 - Math.sqrt(rr)) * N / 2 + 0.5));   // how much of this pixel the ball covers: a soft edge
      if (cov <= 0) col = bg;
      else { var q = Math.min(rr, 0.9999), n = [x, y, Math.sqrt(1 - q)]; col = shade(n, v, l, rough, bg).map(tone); if (cov < 1) col = col.map(function (c, e) { return c * cov + bg[e] * (1 - cov); }); }
      img.data[p++] = col[0] * 255; img.data[p++] = col[1] * 255; img.data[p++] = col[2] * 255; img.data[p++] = 255;
    }
    og.putImageData(img, 0, 0); g.fillStyle = C.bg; g.fillRect(0, 0, W, H);
    g.imageSmoothingEnabled = true; g.drawImage(off, 20, 20, 280, 280);
    // the lobe: light in at 45° from the left onto a flat piece; length of each spoke = how much leaves that way
    var cx = 480, cy = 270, R = 130, li = norm([-Math.sin(Math.PI / 4), Math.cos(Math.PI / 4), 0]), nn = [0, 1, 0], vals = [], mx = 0, d;
    for (d = -88; d <= 88; d += 2) {
      var t = d * Math.PI / 180, vo = [Math.sin(t), Math.cos(t), 0];
      var s = shade(nn, vo, li, rough, [0, 0, 0], true);
      var y1 = (s[0] + s[1] + s[2]) / 3; vals.push([t, y1]); if (y1 > mx) mx = y1;
    }
    g.strokeStyle = C.line; g.lineWidth = 1; g.beginPath(); g.moveTo(cx - R - 10, cy); g.lineTo(cx + R + 10, cy); g.stroke();
    g.strokeStyle = C.ice; g.lineWidth = 2; g.beginPath(); g.moveTo(cx - R * 0.75, cy - R * 0.75); g.lineTo(cx, cy); g.stroke();
    g.strokeStyle = C.gold; g.lineWidth = 2; g.beginPath();
    vals.forEach(function (q, idx) { var len = q[1] / (mx || 1) * R, X = cx + Math.sin(q[0]) * len, Y = cy - Math.cos(q[0]) * len; idx ? g.lineTo(X, Y) : g.moveTo(X, Y); });
    g.stroke();
    g.fillStyle = C.ink3; g.font = F(13, 500); g.textAlign = "left"; g.fillText("light in at 45°", cx - R - 6, cy - R * 0.8);
    g.fillText("gold: the light that leaves, by direction", 340, 58);
    g.fillStyle = C.ink; g.font = F(16, 600); g.fillText(name, 340, 34);
    var a = Math.max(rough * rough, 0.002);
    out.textContent = name + ": roughness " + rough.toFixed(2) + ", so α = roughness² = " + a.toFixed(3) + "; the highlight's peak D = 1/(πα²) = " + (1 / (Math.PI * a * a)).toFixed(a < 0.01 ? 0 : 1) +
      (m.metal ? ". A metal: its colour is its reflection (F0 = base colour), no diffuse light." : m.glass ? ". Glass: 4% reflected head-on (F0 for IOR 1.52), the rest passes through." : ". Not a metal: about 4% reflected head-on, the rest enters and comes back out coloured.") +
      (m.coat ? " Plus a clear coat (a second, smoother highlight)." : "") + (m.sheen ? " Plus sheen: fibres light up at grazing angles." : "");
  }
  k.buttons(Object.keys(M).map(function (key) { return [key, function () { name = key; m = M[key]; rs.value = m.r; rs.dispatchEvent(new Event("input")); }]; }), true);
  k.fig.querySelectorAll(".btns button").forEach(function (b) { b.setAttribute("aria-pressed", b.textContent === name); });
  rs = k.slider("Roughness", 0, 1, 0.01, rough, function (v) { return v.toFixed(2); }, function (v) { rough = v; draw(); });
  ls = k.slider("Sun", 10, 170, 1, sunDeg, function (v) { return v + "°"; }, function (v) { sunDeg = v; draw(); });
  out = k.out(); st.draw = draw; draw();
});
