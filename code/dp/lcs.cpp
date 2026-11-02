#include <algorithm>
#include <iostream>
#include <string>
#include <vector>
using namespace std;

// The longest common subsequence of a and b: the longest string whose letters appear in both, in order
// (not necessarily next to each other). Returns its length; one such string is put in found.
int lcs(const string& a, const string& b, string& found) {
    int n = a.size(), m = b.size();
    vector<vector<int>> L(n + 1, vector<int>(m + 1, 0));   // L[i][j] = LCS length of a[:i] and b[:j]
    for (int i = 1; i <= n; i++)
        for (int j = 1; j <= m; j++)
            if (a[i - 1] == b[j - 1]) L[i][j] = L[i - 1][j - 1] + 1;   // last letters match: use them
            else L[i][j] = max(L[i - 1][j], L[i][j - 1]);        // drop the last letter of a, or of b
    found.clear();
    int i = n, j = m;
    while (i > 0 && j > 0) {                         // walk back from the corner
        if (a[i - 1] == b[j - 1]) { found += a[i - 1]; i--; j--; }
        else if (L[i - 1][j] >= L[i][j - 1]) i--;
        else j--;
    }
    reverse(found.begin(), found.end());
    return L[n][m];
}

int main() {
    vector<pair<string, string>> pairs = {{"ABCBDAB", "BDCABA"}, {"AGGTAB", "GXTXAYB"}, {"OLYMPUS", "ELYSIUM"}};
    for (auto& p : pairs) {
        string found;
        int k = lcs(p.first, p.second, found);
        cout << k << " " << found << "\n";
    }
}
