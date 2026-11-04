// Where each page of cs.akadian.ca sits on the shared ladder Beginner, Intermediate, Expert.
// reader.js (the same on cs, math and cryptography) draws the badge; only this file differs per site.
// path: the page's path; ch: its chapter number in its book (0 if not a chapter); n: chapters in that book.
window.akadianLevel = function (path, ch, n) {
  if (/\/first-steps\//.test(path)) return "Beginner";                        // the beginner track
  if (/\/topics\/./.test(path)) return "All";                         // guides: one part per level
  if (/\/books\/[^\/]+\/\d+-/.test(path) && ch && n) {
    if (ch === n) return "Expert";                                   // the last chapter: where the field goes
    if (ch <= Math.ceil(n * 0.2)) return "Intermediate";
    if (ch > n * 0.75) return "Expert";
    return "Intermediate";
  }
  if (/\/(foundations|sorting|searching)\/./.test(path)) return "Intermediate";
  if (/\/(data-structures|graphs|dp|greedy|strings|number-theory|backtracking)\/./.test(path)) return "Intermediate";
  return null;
};
