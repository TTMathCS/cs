// Where each page of cs.akadian.ca sits on the shared ladder Start, Student, University, Expert, Research.
// reader.js (the same on cs, math and cryptography) draws the badge; only this file differs per site.
// path: the page's path; ch: its chapter number in its book (0 if not a chapter); n: chapters in that book.
window.akadianLevel = function (path, ch, n) {
  if (/\/topics\/./.test(path)) return "All";                         // guides: one part per level
  if (/\/books\/[^\/]+\/\d+-/.test(path) && ch && n) {
    if (ch === n) return "Research";                                   // the last chapter: where the field goes
    if (ch <= Math.ceil(n * 0.2)) return "Student";
    if (ch > n * 0.75) return "Expert";
    return "University";
  }
  if (/\/(foundations|sorting|searching)\/./.test(path)) return "Student";
  if (/\/(data-structures|graphs|dp|greedy|strings|number-theory|backtracking)\/./.test(path)) return "University";
  return null;
};
