#include <iostream>
#include <string>
#include <vector>
using namespace std;

int n, countSolutions;
vector<bool> cols, diag1, diag2;
vector<int> place, first;

void go(int r) {
    if (r == n) {
        countSolutions++;
        if (first.empty()) first = place;
        return;
    }
    for (int c = 0; c < n; c++) {
        if (cols[c] || diag1[r + c] || diag2[r - c + n]) continue;   // attacked: prune this branch
        cols[c] = diag1[r + c] = diag2[r - c + n] = true;
        place[r] = c;
        go(r + 1);
        cols[c] = diag1[r + c] = diag2[r - c + n] = false;   // undo, try the next column
    }
}

// Place n queens on an n x n board so that none attacks another. One queen per row: try each column,
// skip columns and diagonals already under attack, and back up when a row has no safe square.
// Returns the number of solutions; the first one found is put in first.
int nQueens(int size) {
    n = size; countSolutions = 0; first.clear();
    cols.assign(n, false); diag1.assign(2 * n, false); diag2.assign(2 * n, false);
    place.assign(n, 0);
    go(0);
    return countSolutions;
}

int main() {
    cout << "[";
    for (int k = 1; k <= 10; k++) cout << (k > 1 ? ", " : "") << nQueens(k);
    cout << "]\n";
    nQueens(8);
    cout << "[";
    for (int i = 0; i < 8; i++) cout << (i ? ", " : "") << first[i];
    cout << "]\n";
    nQueens(6);
    for (int c : first) {
        string row(6, '.');
        row[c] = 'Q';
        cout << row << "\n";
    }
}
