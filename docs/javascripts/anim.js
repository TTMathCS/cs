// "Watch it step by step" animations (as on cryptography.akadian.ca: nothing moves until the reader presses Play
// or Step). A box is <div class="cs-anim" data-anim="bubble-sort"></div>; its frames are docs/anim/bubble-sort.json,
// made by tools/anim/make_frames.py from a real run of the algorithm, so the picture always matches the code.
// Three views: "array" (bars or boxes), "graph" (nodes and edges, also used for trees) and "grid" (DP tables,
// string matching). Every frame carries a sentence saying what just happened.
(function () {
  var NS = "http://www.w3.org/2000/svg";
  function svgEl(tag, attrs, text) {
    var e = document.createElementNS(NS, tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (text !== undefined) e.textContent = text;
    return e;
  }
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }
  function btn(text) { var b = el("button", "cs-anim__btn", text); b.type = "button"; return b; }
  function base() {
    var b = ".";
    try { b = JSON.parse(document.getElementById("__config").textContent).base || "."; } catch (e) { /* this folder */ }
    return new URL(b.replace(/\/?$/, "/"), location.href).href;
  }

  // ---- array: bars when the values are numbers, boxes otherwise ----
  function drawArray(svg, spec, f) {
    var a = f.a, n = a.length, boxes = spec.boxes || a.some(function (v) { return typeof v !== "number"; });
    var W = Math.max(600, n * 46), H = boxes ? 96 : 190, cw = W / n;
    svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    var max = 1; if (!boxes) a.forEach(function (v) { if (v > max) max = v; });
    var cls = f.cls || {}, done = {}; (f.done || []).forEach(function (i) { done[i] = 1; });
    var dim = {}; (f.dim || []).forEach(function (i) { dim[i] = 1; });
    for (var i = 0; i < n; i++) {
      var c = cls[i] || (done[i] ? "done" : (dim[i] ? "dim" : "")), x = i * cw;
      if (boxes) {
        var bw = Math.min(cw - 6, 56);
        svg.append(svgEl("rect", { x: x + (cw - bw) / 2, y: 18, width: bw, height: 40, rx: 6, "class": "cs-cell " + c }));
        svg.append(svgEl("text", { x: x + cw / 2, y: 44, "class": "cs-val", "text-anchor": "middle" }, a[i] === null ? "" : String(a[i])));
      } else {
        var h = Math.max(4, (a[i] / max) * 120);
        var bw2 = Math.min(cw - 8, 48);
        svg.append(svgEl("rect", { x: x + (cw - bw2) / 2, y: 140 - h, width: bw2, height: h, rx: 4, "class": "cs-bar " + c }));
        svg.append(svgEl("text", { x: x + cw / 2, y: 134 - h, "class": "cs-val", "text-anchor": "middle" }, String(a[i])));
      }
      svg.append(svgEl("text", { x: x + cw / 2, y: boxes ? 12 : 156, "class": "cs-idx", "text-anchor": "middle" }, String(i)));
    }
    var row = {};
    for (var p in (f.ptr || {})) {
      var at = f.ptr[p]; if (at === null || at === undefined || at < 0 || at > n) continue;
      var r = row[at] = (row[at] || 0) + 1;
      svg.append(svgEl("text", { x: at * cw + cw / 2, y: (boxes ? 74 : 170) + (r - 1) * 13, "class": "cs-ptr", "text-anchor": "middle" }, "↑" + p));
    }
    if (boxes) svg.setAttribute("viewBox", "0 0 " + W + " " + (70 + 13 * Math.max(1, maxRow(row)) + 6));
    else svg.setAttribute("viewBox", "0 0 " + W + " " + (158 + 13 * Math.max(0, maxRow(row)) + 6));
  }
  function maxRow(row) { var m = 0; for (var k in row) if (row[k] > m) m = row[k]; return m; }

  // ---- graph: nodes at fixed places, edges with weights; also trees ----
  function drawGraph(svg, spec, f) {
    var W = spec.w || 520, H = spec.h || 300, R = spec.r || 18;
    svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    var pos = {}; spec.nodes.forEach(function (nd) { pos[nd.id] = nd; });
    var nodes = f.nodes || spec.nodes, edges = f.edges || spec.edges || [];
    if (f.nodes) { pos = {}; nodes.forEach(function (nd) { pos[nd.id] = nd; }); }
    var ec = f.e || {}, nc = f.n || {}, nl = f.nl || {};
    var defs = svgEl("defs", {});
    ["", "hot", "done", "path", "dim", "active"].forEach(function (k) {
      var m = svgEl("marker", { id: "ah-" + svg.dataset.uid + "-" + k, viewBox: "0 0 10 10", refX: 10, refY: 5, markerWidth: 7, markerHeight: 7, orient: "auto-start-reverse" });
      m.append(svgEl("path", { d: "M0,0 L10,5 L0,10 z", "class": "cs-arrow " + k })); defs.append(m);
    });
    svg.append(defs);
    edges.forEach(function (ed, i) {
      var a = pos[ed.u], b = pos[ed.v]; if (!a || !b) return;
      var dx = b.x - a.x, dy = b.y - a.y, L = Math.sqrt(dx * dx + dy * dy) || 1, ux = dx / L, uy = dy / L;
      var bend = ed.bend || 0, c = ec[i] || "";
      var x1 = a.x + ux * R, y1 = a.y + uy * R, x2 = b.x - ux * (R + (spec.directed ? 2 : 0)), y2 = b.y - uy * (R + (spec.directed ? 2 : 0));
      var mx = (x1 + x2) / 2 - uy * bend, my = (y1 + y2) / 2 + ux * bend;
      var attrs = { d: "M" + x1 + "," + y1 + " Q" + mx + "," + my + " " + x2 + "," + y2, "class": "cs-edge " + c, fill: "none" };
      if (spec.directed) attrs["marker-end"] = "url(#ah-" + svg.dataset.uid + "-" + c + ")";
      svg.append(svgEl("path", attrs));
      if (ed.w !== undefined) {
        var lx = (x1 + 2 * mx + x2) / 4 - uy * 9, ly = (y1 + 2 * my + y2) / 4 + ux * 9;
        svg.append(svgEl("text", { x: lx, y: ly + 4, "class": "cs-w " + c, "text-anchor": "middle" }, String(ed.w)));
      }
    });
    nodes.forEach(function (nd) {
      var c = nc[nd.id] || "";
      svg.append(svgEl("circle", { cx: nd.x, cy: nd.y, r: R, "class": "cs-node " + c }));
      svg.append(svgEl("text", { x: nd.x, y: nd.y + 5, "class": "cs-nlabel", "text-anchor": "middle" }, nd.label !== undefined ? String(nd.label) : String(nd.id)));
      if (nl[nd.id] !== undefined) svg.append(svgEl("text", { x: nd.x, y: nd.y - R - 6, "class": "cs-ntag", "text-anchor": "middle" }, String(nl[nd.id])));
    });
  }

  // ---- grid: a table of cells with row and column headings ----
  function drawGrid(box, spec, f) {
    var t = el("table", "cs-grid"), cls = f.cls || {};
    var rows = f.rows || spec.rows, cols = f.cols || spec.cols;
    if (cols) {
      var tr = el("tr"); if (rows) tr.append(el("th", "", spec.corner || ""));
      cols.forEach(function (c) { tr.append(el("th", "", String(c))); }); t.append(tr);
    }
    f.cells.forEach(function (row, r) {
      var tr = el("tr"); if (rows) tr.append(el("th", "", String(rows[r])));
      row.forEach(function (v, c) {
        var td = el("td", cls[r + "," + c] || "", v === null || v === undefined ? "" : String(v)); tr.append(td);
      });
      t.append(tr);
    });
    box.append(t);
  }

  function build(box, data) {
    var frames = data.frames, k = 0, timer = null;
    var bar = el("p", "cs-anim__bar"), play = btn("Play"), back = btn("Back"), step = btn("Step"), reset = btn("Reset");
    var count = el("span", "cs-anim__count");
    bar.append(play, back, step, reset, count);
    var title = data.title ? el("p", "cs-anim__title", data.title) : null;
    var stage = el("div", "cs-anim__stage"), note = el("p", "cs-anim__note"), info = el("div", "cs-anim__info");
    if (title) box.append(title);
    box.append(bar, stage, note, info);
    var uid = Math.random().toString(36).slice(2, 8);
    function draw() {
      var f = frames[k]; stage.textContent = "";
      if (data.view === "grid") drawGrid(stage, data, f);
      else {
        var svg = svgEl("svg", { "class": "cs-svg", role: "img", "aria-label": f.note || data.title || "" });
        svg.dataset.uid = uid; stage.append(svg);
        if (data.view === "graph") drawGraph(svg, data, f); else drawArray(svg, data, f);
      }
      note.textContent = f.note || "";
      info.textContent = "";
      (f.info || []).forEach(function (line) { info.append(el("div", "", line)); });
      count.textContent = "step " + (k + 1) + " of " + frames.length;
      step.disabled = k === frames.length - 1; back.disabled = k === 0;
    }
    function stop() { clearInterval(timer); timer = null; play.textContent = "Play"; }
    function next() { if (k < frames.length - 1) { k++; draw(); } if (k === frames.length - 1) stop(); }
    play.addEventListener("click", function () {
      if (timer) { stop(); return; }
      if (k === frames.length - 1) { k = 0; draw(); }
      play.textContent = "Pause";
      timer = setInterval(next, data.speed || 1100);
    });
    step.addEventListener("click", function () { stop(); next(); });
    back.addEventListener("click", function () { stop(); if (k > 0) { k--; draw(); } });
    reset.addEventListener("click", function () { stop(); k = 0; draw(); });
    draw();
  }

  function init() {
    var root = base();
    document.querySelectorAll(".cs-anim:not([data-ready])").forEach(function (box) {
      box.dataset.ready = "1";
      fetch(root + "anim/" + box.dataset.anim + ".json")
        .then(function (r) { return r.json(); })
        .then(function (data) { build(box, data); })
        .catch(function () { box.textContent = "The animation could not load."; });
    });
  }
  if (typeof document$ !== "undefined") document$.subscribe(init);
  else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
