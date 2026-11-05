/* sorting/index.md: hear a sort. 48 bars in random order; each comparison lights two bars and plays a note whose
   pitch is the height of the bar. Insertion sort and bubble sort grow like n²; merge sort and quicksort like n log n,
   and you can hear the difference in how long they take. The counts are real comparisons of this run. */
PLAY("sortsound", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 320, st = k.stage(W, H), g = st.g, out = k.out(), N = 48, a, hi = [], cmp = 0, algo = "insertion", timer = 0, steps = [];
  function shuffle() { a = []; for (var i = 1; i <= N; i++) a.push(i); for (i = N - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)), t = a[i]; a[i] = a[j]; a[j] = t; } }
  function record() {   // run the sort on a copy and keep every step: ["c", i, j] compare, ["s", i, v] set a[i] = v
    var b = a.slice(), s = [];
    function less(i, j) { s.push(["c", i, j]); return b[i] < b[j]; }
    function set(i, v) { b[i] = v; s.push(["s", i, v]); }
    function swap(i, j) { var t = b[i]; set(i, b[j]); set(j, t); }
    if (algo === "insertion") for (var i = 1; i < N; i++) for (var j = i; j > 0 && less(j, j - 1); j--) swap(j, j - 1);
    if (algo === "bubble") for (i = 0; i < N - 1; i++) for (j = 0; j < N - 1 - i; j++) if (less(j + 1, j)) swap(j, j + 1);
    if (algo === "merge") (function ms(l, r) { if (r - l < 2) return; var m = (l + r) >> 1; ms(l, m); ms(m, r);
      var t = [], x = l, y = m; while (x < m && y < r) { if (less(y, x)) t.push(b[y++]); else t.push(b[x++]); } while (x < m) t.push(b[x++]); while (y < r) t.push(b[y++]);
      t.forEach(function (v, q) { set(l + q, v); }); })(0, N);
    if (algo === "quick") (function qs(l, r) { if (r - l < 1) return; var p = r, i = l; for (var j = l; j < r; j++) if (less(j, p)) { swap(i, j); i++; } swap(i, r); qs(l, i - 1); qs(i + 1, r); })(0, N - 1);
    return s;
  }
  function tone(v) { var ac = k.audio(); if (!ac) return; var o = ac.createOscillator(), e = ac.createGain(); o.type = "triangle"; o.frequency.value = 180 + v * 18;
    e.gain.setValueAtTime(0.08, ac.currentTime); e.gain.exponentialRampToValueAtTime(0.0005, ac.currentTime + 0.07); o.connect(e); e.connect(ac.destination); o.start(); o.stop(ac.currentTime + 0.08); }
  function draw() {
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H); var bw = (W - 40) / N;
    for (var i = 0; i < N; i++) { g.fillStyle = hi.indexOf(i) >= 0 ? C.gold : C.rust; g.fillRect(20 + i * bw + 1, 290 - a[i] * 5, bw - 2, a[i] * 5); }
    g.font = F(20, 600, "d"); g.fillStyle = C.ink; g.fillText({ insertion: "Insertion sort", bubble: "Bubble sort", merge: "Merge sort", quick: "Quicksort" }[algo], 20, 30);
    g.font = F(16, 500, "m"); g.fillStyle = C.ink2; g.textAlign = "right"; g.fillText(cmp + " comparisons", W - 20, 30); g.textAlign = "left";
  }
  function run() {
    clearInterval(timer); shuffle(); steps = record(); cmp = 0; var n = 0, per = Math.max(1, Math.round(steps.length / 900));
    timer = setInterval(function () {
      for (var q = 0; q < per && n < steps.length; q++, n++) { var s = steps[n]; if (s[0] === "c") { cmp++; hi = [s[1], s[2]]; if (q === 0) tone(a[s[1]]); } else a[s[1]] = s[2]; }
      if (n >= steps.length) { clearInterval(timer); hi = []; out.textContent = "Done: " + cmp + " comparisons for " + N + " items. n² would be " + N * N + "; n log₂ n about " + Math.round(N * Math.log2(N)) + "."; }
      draw();
    }, 16);
    out.textContent = "Sorting… (sound on to hear it)";
  }
  shuffle(); st.draw = draw; draw();
  k.buttons([["Insertion", function () { algo = "insertion"; run(); }], ["Bubble", function () { algo = "bubble"; run(); }], ["Merge", function () { algo = "merge"; run(); }], ["Quick", function () { algo = "quick"; run(); }]], true);
  k.buttons([["Stop", function () { clearInterval(timer); hi = []; draw(); }]]);
  out.textContent = "Pick a sort to watch and hear it.";
  if (window.IntersectionObserver) new IntersectionObserver(function (es) { if (!es[0].isIntersecting) clearInterval(timer); }).observe(fig);
});
