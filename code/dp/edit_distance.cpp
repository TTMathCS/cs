#include <algorithm>
#include <iostream>
#include <string>
#include <vector>
using namespace std;

// The fewest single-letter inserts, deletes and replacements that turn a into b (Levenshtein distance).
// Returns the distance; the list of steps is put in steps.
int editDistance(const string& a, const string& b, vector<string>& steps) {
    int n = a.size(), m = b.size();
    vector<vector<int>> D(n + 1, vector<int>(m + 1, 0));   // D[i][j] = distance from a[:i] to b[:j]
    for (int i = 0; i <= n; i++) D[i][0] = i;        // delete all i letters
    for (int j = 0; j <= m; j++) D[0][j] = j;        // insert all j letters
    for (int i = 1; i <= n; i++)
        for (int j = 1; j <= m; j++) {
            int same = a[i - 1] == b[j - 1] ? 0 : 1;
            D[i][j] = min({D[i - 1][j] + 1,          // delete a[i-1]
                           D[i][j - 1] + 1,          // insert b[j-1]
                           D[i - 1][j - 1] + same}); // keep or replace
        }
    steps.clear();
    int i = n, j = m;
    while (i > 0 || j > 0) {                         // walk back to list the steps
        if (i > 0 && j > 0 && D[i][j] == D[i - 1][j - 1] + (a[i - 1] != b[j - 1] ? 1 : 0)) {
            if (a[i - 1] != b[j - 1]) steps.push_back(string("replace ") + a[i - 1] + " with " + b[j - 1]);
            i--; j--;
        } else if (i > 0 && D[i][j] == D[i - 1][j] + 1) {
            steps.push_back(string("delete ") + a[i - 1]); i--;
        } else {
            steps.push_back(string("insert ") + b[j - 1]); j--;
        }
    }
    reverse(steps.begin(), steps.end());
    return D[n][m];
}

int main() {
    vector<pair<string, string>> pairs = {{"kitten", "sitting"}, {"sunday", "saturday"}, {"mars", "stars"}};
    for (auto& p : pairs) {
        vector<string> steps;
        int d = editDistance(p.first, p.second, steps);
        cout << p.first << " " << p.second << " " << d << " ";
        for (size_t k = 0; k < steps.size(); k++) cout << (k ? "; " : "") << steps[k];
        cout << "\n";
    }
}
