// Typeset math with KaTeX (as on cryptography.akadian.ca).
// Markdown writes math as $...$ (inline) or $$...$$ (display); pymdownx.arithmatex wraps it in .arithmatex
// elements, and this renders only those, so code blocks and hex values are never touched. KaTeX is served
// from this site (docs/katex/), not a CDN.
(function () {
  function render() {
    if (!window.renderMathInElement) return;
    document.querySelectorAll(".arithmatex:not([data-ready])").forEach(function (el) {
      el.dataset.ready = "1";
      window.renderMathInElement(el, {
        delimiters: [
          { left: "\\(", right: "\\)", display: false },
          { left: "\\[", right: "\\]", display: true }
        ],
        throwOnError: false
      });
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", render); else render();
})();
