/* books/algorithms/05: count the comparisons. Insertion sort makes about n²/4 on shuffled input and n − 1 on sorted input;
   merge sort stays near n lg n whatever the order. Pick an order and a size. */
PLAY("sortcount", function (fig, k) {
  var C = k.C, F = k.F, W = 600, H = 210, st = k.stage(W, H), g = st.g, out = k.out(), n = 100, ord = "shuffled";
  function arr() { var a = []; for (var i = 0; i < n; i++) a.push(i); if (ord === "reversed") a.reverse(); if (ord === "shuffled") for (i = n - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)), t = a[i]; a[i] = a[j]; a[j] = t; } return a; }
  function ins(a) { a = a.slice(); var c = 0; for (var i = 1; i < a.length; i++) { var x = a[i], j = i - 1; while (j >= 0) { c++; if (a[j] > x) { a[j + 1] = a[j]; j--; } else break; } a[j + 1] = x; } return c; }
  function mer(a) { var c = 0; (function ms(b) { if (b.length < 2) return b; var m = b.length >> 1, L = ms(b.slice(0, m)), R = ms(b.slice(m)), o = [], i = 0, j = 0; while (i < L.length && j < R.length) { c++; o.push(L[i] <= R[j] ? L[i++] : R[j++]); } return o.concat(L.slice(i), R.slice(j)); })(a); return c; }
  function draw() {
    var a = arr(), ci = ins(a), cm = mer(a), mx = Math.max(ci, cm, 1);
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H); g.textAlign = "left";
    g.fillStyle = C.ink; g.font = F(20, 700); g.fillText(n + " items, " + ord, 20, 32);
    [["insertion sort", ci, C.rust], ["merge sort", cm, C.green]].forEach(function (r, i) {
      var y = 60 + i * 66; g.fillStyle = C.ink2; g.font = F(18, 700); g.fillText(r[0] + ": " + r[1].toLocaleString("en"), 20, y + 4);
      g.fillStyle = r[2]; g.fillRect(20, y + 14, Math.max(3, 560 * r[1] / mx), 24); });
    out.textContent = "Insertion sort: " + ci.toLocaleString("en") + " comparisons, merge sort: " + cm.toLocaleString("en") + ". For reference n²/4 = " + Math.round(n * n / 4).toLocaleString("en") + " and n lg n = " + Math.round(n * Math.log2(n)).toLocaleString("en") + ".";
  }
  k.slider("Items n", 10, 1000, 10, n, function (v) { return v; }, function (v) { n = +v; draw(); });
  k.buttons([["Shuffled", function () { ord = "shuffled"; draw(); }], ["Already sorted", function () { ord = "sorted"; draw(); }], ["Reversed", function () { ord = "reversed"; draw(); }]], true);
  st.draw = draw; draw();
});
